import streamlit as st
import requests
import json
import base64
import tempfile
import os
from users import USERS
from audio_recorder_streamlit import audio_recorder
import assemblyai as aai
from speech_service import AudioTranscriber
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Agent Chatbot",
    page_icon="🤖",
    layout="centered"
)

API_URL = "http://localhost:8000/ask"
aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY") 
transcriber = AudioTranscriber(os.getenv("ASSEMBLYAI_API_KEY"))

def authenticate_user(email, password):
    """Authenticate user with email and password"""
    if email in USERS and USERS[email]["password"] == password:
        return USERS[email]["role"]
    return None

def transcribe_audio(audio_bytes):
    """Convert audio bytes to text using AssemblyAI"""
    try:
        if audio_bytes is None or len(audio_bytes) == 0:
            return "Error: No audio data received"
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_file_path = tmp_file.name
        if not os.path.exists(tmp_file_path) or os.path.getsize(tmp_file_path) == 0:
            return "Error: Audio file is empty or not created"
        config = aai.TranscriptionConfig(
            speech_model=aai.SpeechModel.best,
            language_detection=True,
            audio_start_from=0,
            auto_highlights=False
        )
        transcriber = aai.Transcriber(config=config)
        transcript = transcriber.transcribe(tmp_file_path)
        try:
            os.unlink(tmp_file_path)
        except:
            pass  
        if transcript.status == aai.TranscriptStatus.error:
            return f"Transcription failed: {transcript.error}"
        elif transcript.status == aai.TranscriptStatus.completed:
            if transcript.text and transcript.text.strip():
                return transcript.text.strip()
            else:
                return "No speech detected in the audio. Please try speaking more clearly or closer to the microphone."
        else:
            return f"Transcription status: {transcript.status}"
    except Exception as e:
        return f"Error in transcription: {str(e)}"

def get_response_from_api(question):
    """Get response from FastAPI backend"""
    try:
        response = requests.post(
            API_URL,
            json={"user_question": question},
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {"response": f"Error: {response.status_code} - {response.text}", "audio": ""}
    except requests.exceptions.RequestException as e:
        return {"response": f"Connection error: {str(e)}", "audio": ""}
    
def play_audio_response(audio_base64):
    """Convert base64 audio to playable format and display audio player"""
    if audio_base64:
        try:
            audio_bytes = base64.b64decode(audio_base64)
            st.audio(audio_bytes, format="audio/wav")
            return True
        except Exception as e:
            st.error(f"Error playing audio: {str(e)}")
            return False
    return False

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
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("🤖 Agent Chatbot")
        st.markdown(f"**Role:** {st.session_state.user_role} | **User:** {st.session_state.user_email}")
    with col2:
        if st.button("Logout", type="secondary"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    st.markdown("---")
    if "messages" not in st.session_state:
        st.session_state.messages = []
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Audio input section
    st.markdown("### 🎤 Voice Input")
    audio_bytes = audio_recorder(
        text="Click to record",
        recording_color="#e8b62c",
        neutral_color="#6aa36f",
        icon_name="microphone",
        icon_size="2x",
    )
    if audio_bytes:
        st.audio(audio_bytes, format="audio/wav")
        st.write(f"Audio data size: {len(audio_bytes)} bytes")
        with st.spinner("Converting speech to text..."):
            transcribed_text = transcribe_audio(audio_bytes)
        st.write(f"Transcription result: '{transcribed_text}'")
        if transcribed_text and not transcribed_text.startswith("Error") and not transcribed_text.startswith("Transcription failed") and not transcribed_text.startswith("No speech detected"):
            st.success("Speech converted to text successfully!")
            st.write("**Transcribed Text:**", transcribed_text)
            # Add transcribed text to chat and process
            st.session_state.messages.append({"role": "user", "content": transcribed_text})
            with st.chat_message("user"):
                st.markdown(transcribed_text)
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    api_response = get_response_from_api(transcribed_text)
                    response_text = api_response.get("response", "")
                    audio_data = api_response.get("audio", "")
                    st.markdown(response_text)
                    if audio_data:
                        st.markdown("🔊 **Audio Response:**")
                        play_audio_response(audio_data)
                    st.session_state.messages.append({"role": "assistant", "content": response_text})
        else:
            st.error(f"Transcription issue: {transcribed_text}")
            st.info("Try speaking more clearly, closer to the microphone, or in a quieter environment.")
    st.markdown("---")

    # Text input section
    st.markdown("### ⌨️ Text Input")
    if prompt := st.chat_input("Ask me anything..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                api_response = get_response_from_api(prompt)
                response_text = api_response.get("response", "")
                audio_data = api_response.get("audio", "")
                st.markdown(response_text)
                if audio_data:
                    st.markdown("🔊 **Audio Response:**")
                    play_audio_response(audio_data)
                st.session_state.messages.append({"role": "assistant", "content": response_text})

    # Sidebar
    with st.sidebar:
        st.subheader("Your Role: " + st.session_state.user_role)
        roles = {
            "Admin": "🔧 You have access to all functionalities",
            "Engineering": "💻 Ask me about technical topics, architecture, and development",
            "Finance": "💰 Ask me about budgets, financial analysis, and accounting",
            "Marketing": "📢 Ask me about campaigns, market research, and branding",
            "HR": "👥 Ask me about policies, recruitment, and employee relations"
        }
        st.info(roles.get(st.session_state.user_role, "📝 Ask me general questions on any topic"))
        st.markdown("---")
        st.subheader("Input Methods")
        st.info("🎤 **Voice**: Click the microphone to record your question")
        st.info("⌨️ **Text**: Type your question in the chat input")
        st.markdown("---")
        if st.button("Clear Chat History"):
            st.session_state.messages = []
            st.rerun()
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
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if st.session_state.authenticated:
        chat_page()
    else:
        login_page()

if __name__ == "__main__":
    main()
