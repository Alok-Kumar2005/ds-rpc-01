import streamlit as st
import requests
import json
from users import USERS

# Configure page
st.set_page_config(
    page_title="Agent Chatbot",
    page_icon="🤖",
    layout="centered"
)


# FastAPI backend URL
API_URL = "http://localhost:8000/ask"

def authenticate_user(email, password):
    """Authenticate user with email and password"""
    if email in USERS and USERS[email]["password"] == password:
        return USERS[email]["role"]
    return None

def get_response_from_api(question):
    """Get response from FastAPI backend"""
    try:
        response = requests.post(
            API_URL,
            json={"user_question": question},
            timeout=30
        )
        if response.status_code == 200:
            return response.json().get("response", "No response received")
        else:
            return f"Error: {response.status_code} - {response.text}"
    except requests.exceptions.RequestException as e:
        return f"Connection error: {str(e)}"

def login_page():
    """Display login page"""
    st.title("🤖 Agent Chatbot - Login")
    
    with st.form("login_form"):
        st.subheader("Please log in to continue")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        login_button = st.form_submit_button("Login")
        
        if login_button:
            if email and password:
                role = authenticate_user(email, password)
                if role:
                    st.session_state.authenticated = True
                    st.session_state.user_email = email
                    st.session_state.user_role = role
                    st.success(f"Welcome! You are logged in as {role}")
                    st.rerun()
                else:
                    st.error("Invalid email or password")
            else:
                st.error("Please enter both email and password")
    

def chat_page():
    """Display chat interface"""
    # Header with user info and logout
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.title("🤖 Agent Chatbot")
        st.markdown(f"**Role:** {st.session_state.user_role} | **User:** {st.session_state.user_email}")
    
    with col2:
        if st.button("Logout", type="secondary"):
            # Clear session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    st.markdown("---")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me anything..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = get_response_from_api(prompt)
                st.markdown(response)
                
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Sidebar with role-specific information
    with st.sidebar:
        st.subheader("Your Role: " + st.session_state.user_role)
        
        if st.session_state.user_role == "Admin":
            st.info("🔧 You have access to all functionalities")
        elif st.session_state.user_role == "Engineering":
            st.info("💻 Ask me about technical topics, architecture, and development")
        elif st.session_state.user_role == "Finance":
            st.info("💰 Ask me about budgets, financial analysis, and accounting")
        elif st.session_state.user_role == "Marketing":
            st.info("📢 Ask me about campaigns, market research, and branding")
        elif st.session_state.user_role == "HR":
            st.info("👥 Ask me about policies, recruitment, and employee relations")
        else:
            st.info("📝 Ask me general questions on any topic")
        
        st.markdown("---")
        
        # Clear chat button
        if st.button("Clear Chat History"):
            st.session_state.messages = []
            st.rerun()
        
        # Connection status
        st.markdown("---")
        st.subheader("Connection Status")
        try:
            response = requests.get("http://localhost:8000/", timeout=5)
            if response.status_code == 200:
                st.success("✅ Backend Connected")
            else:
                st.error(f"❌ Backend Error: {response.status_code}")
        except requests.exceptions.ConnectionError:
            st.error("❌ Backend Offline - Start your FastAPI server")
        except requests.exceptions.Timeout:
            st.error("❌ Backend Timeout")
        except Exception as e:
            st.error(f"❌ Backend Error: {str(e)}")

def main():
    """Main application logic"""
    # Initialize session state
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    # Show appropriate page based on authentication status
    if st.session_state.authenticated:
        chat_page()
    else:
        login_page()

if __name__ == "__main__":
    main()