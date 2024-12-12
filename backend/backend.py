# Therapist_Chatbot/backend/backend.py
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_openai import AzureChatOpenAI
import sqlite3
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from dotenv import load_dotenv
import google.generativeai as genai
from pathlib import Path

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Therapist Chatbot API",
    description="API for an empathetic AI therapist chatbot",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust as needed for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define directories
ROOT_DIR = Path(__file__).resolve().parent.parent  # Adjust if backend.py is nested differently
STATIC_DIR = ROOT_DIR / 'frontend' / 'static'
TEMPLATES_DIR = ROOT_DIR / 'frontend' / 'templates'
DATABASE_PATH = ROOT_DIR / 'database' / 'chatbot.db'

# Mount static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Initialize templates
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Database setup
def init_db():
    if not DATABASE_PATH.exists():
        raise FileNotFoundError(f"Database not found at {DATABASE_PATH}. Please run setup_db.py first.")
    else:
        print(f"Using database at {DATABASE_PATH}")

init_db()

# Initialize AI Models
class AIModels:
    def __init__(self):
        # Initialize Azure OpenAI
        if "SSL_CERT_FILE" in os.environ:
            del os.environ["SSL_CERT_FILE"]
        
        self.azure_llm = AzureChatOpenAI(
            openai_api_key=os.getenv('AZURE_OPENAI_API_KEY'),
            azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT'),
            azure_deployment="gpt-4",
            api_version="2023-05-15",
            temperature=0.7,
            max_tokens=150,
            timeout=30,
            max_retries=2
        )
        
        # Initialize Gemini
        GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
        genai.configure(api_key=GOOGLE_API_KEY)
        self.gemini = genai.GenerativeModel('gemini-1.5-pro')
        self.gemini_chats = {}

ai_models = AIModels()

# Pydantic models
class ChatRequest(BaseModel):
    message: str
    model: str = "azure"  # "azure" or "gemini"

# Message history management
class ChatSession:
    def __init__(self):
        self.history = []

    def add_message(self, role: str, content: str):
        self.history.append((role, content))

    def get_context(self):
        return self.history[-5:]  # Keep last 5 messages for context

# Initialize session storage
sessions = {}

# Define therapist personality
system_prompt = """You are an empathetic and professional therapist. 
Your responses should be:
- Compassionate and understanding
- Non-judgmental
- Focused on active listening
- Professional but warm
- Encouraging but not dismissive
- Avoid giving medical advice or diagnoses
- Use reflective listening techniques
- Ask open-ended questions to encourage conversation"""

# Routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        session_id = "default"  # TODO: Implement proper session management
        
        if request.model == "gemini":
            # Handle Gemini chat
            if session_id not in ai_models.gemini_chats:
                chat = ai_models.gemini.start_chat(history=[])
                chat.send_message(system_prompt)
                ai_models.gemini_chats[session_id] = chat
            
            response = ai_models.gemini_chats[session_id].send_message(request.message)
            bot_response = response.text
        else:
            # Handle Azure OpenAI chat
            if session_id not in sessions:
                sessions[session_id] = ChatSession()
            
            messages = [("system", system_prompt)]
            messages.extend(sessions[session_id].get_context())
            messages.append(("human", request.message))
            
            response = ai_models.azure_llm.invoke(messages)
            bot_response = response.content.strip()
            
            sessions[session_id].add_message("human", request.message)
            sessions[session_id].add_message("assistant", bot_response)

        # Log to database
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute(
            "INSERT INTO conversations (user_message, bot_response, model) VALUES (?, ?, ?)",
            (request.message, bot_response, request.model)
        )
        conn.commit()
        conn.close()

        return {"response": bot_response}
    except Exception as e:
        print(f"Error in /chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)