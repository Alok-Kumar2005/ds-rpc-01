# DS RPC 01: Internal chatbot with role based access control

This is the starter repository for Codebasics's [Resume Project Challenge](https://codebasics.io/challenge/codebasics-gen-ai-data-science-resume-project-challenge) of building a RAG based Internal Chatbot with role based access control. Please fork this repository to get started.

Basic Authentication using FastAPI's `HTTPBasic` has been implemented in `main.py` for learners to get started with.

Visit the challenge page to learn more: [DS RPC-01](https://codebasics.io/challenge/codebasics-gen-ai-data-science-resume-project-challenge)
![alt text](resources/RPC_01_Thumbnail.jpg)
### Roles Provided
 - **engineering**
 - **finance**
 - **general**
 - **hr**
 - **marketing**


## Environment Setup and download requirements
```
uv venv   ( python version: 3.10.17 )
uv add -r requirements.txt
```

## Run command to make the vector database
```
python app\Storage\vectors.py         ( create vector database for vector retrieval )
python app\Storage\keyword_ret.py     ( create vector database for keyword retrieval )
```

## Before executing the program 
- make a .env file and add all the important key
- api key's example are present in .env_example


## Run backend and frontend
```
python app/main.py          ( run backend )
streamlit run frontend.py   ( run frontend )
```

# Images
### Backend image
<img src="images/backend.png" alt="Backend Image Image" width="600"/>

### Frontend login
<img src="images/frontend_login.png" alt="Frontend login Image" width="600"/>

### Frontend 
<img src="images/frontend.png" alt="frontend Image" width="600"/>

### Workflow with Long Term Memory
<img src="workflow.png" alt="Workflow Image" width="800"/>