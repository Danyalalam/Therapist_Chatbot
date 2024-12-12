# frontend/frontend.py
import streamlit as st
import requests
import json

# Page configuration
st.set_page_config(page_title="AI Therapist", page_icon="🧠", layout="centered")

# Custom CSS (keep existing dark theme styling)
st.markdown("""
<style>
    .stApp {
        background-color: #2b2b2b;
        color: #f0f0f0;
    }
    .main-container {
        background-color: #3c3c3c;
        padding: 2rem;
        border-radius: 10px;
        margin: 1rem auto;
        max-width: 800px;
        color: #f0f0f0;
    }
    .chat-container {
        height: 60vh;
        overflow-y: auto;
        padding: 1rem;
        background-color: #2b2b2b;
        border: 1px solid #555555;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .message {
        padding: 0.8rem;
        border-radius: 10px;
        margin-bottom: 0.5rem;
        max-width: 70%;
        word-wrap: break-word;
    }
    .user-message {
        background-color: #4a90e2;
        margin-left: auto;
        color: white;
    }
    .bot-message {
        background-color: #7b7b7b;
        margin-right: auto;
        color: white;
    }
    .stTextInput>div>div>input {
        background-color: #4a4a4a !important;
        color: #f0f0f0 !important;
    }
    .stButton>button {
        background-color: #4a90e2 !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Sidebar for model selection
with st.sidebar:
    st.title("Model Selection")
    model_choice = st.radio(
        "Choose AI Model:",
        ["azure", "gemini"],
        format_func=lambda x: "Azure GPT-4" if x == "azure" else "Google Gemini"
    )

def send_message(user_input):
    try:
        response = requests.post(
            "http://localhost:8000/chat",
            headers={"Content-Type": "application/json"},
            json={
                "message": user_input,
                "model": model_choice
            },
            timeout=30
        )
        if response.status_code == 200:
            return response.json()["response"]
        return f"Error: {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"

# Main container
with st.container():
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # Header
    st.title("🧠 AI Therapist")
    st.write("Share your thoughts and feelings in a safe space.")
    
    # Chat container
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for message in st.session_state.messages:
        role = message["role"]
        content = message["content"]
        st.markdown(
            f"""<div class="message {'user-message' if role == 'user' else 'bot-message'}">
                <strong>{'You' if role == 'user' else 'Therapist'}:</strong> {content}
            </div>""",
            unsafe_allow_html=True
        )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Input form
    with st.form(key='chat_form', clear_on_submit=True):
        user_input = st.text_input('Type your message here...')
        submit_button = st.form_submit_button('Send')
        
        if submit_button and user_input.strip():
            # Add user message
            st.session_state.messages.append({
                "role": "user",
                "content": user_input.strip()
            })
            
            # Get bot response
            with st.spinner(" Therapist is thinking..."):
                bot_response = send_message(user_input.strip())
            
            # Add bot message
            st.session_state.messages.append({
                "role": "bot",
                "content": bot_response
            })
            
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
    <div style="position: fixed; bottom: 0; left: 0; width: 100%; background-color: #2b2b2b; 
                color: #aaaaaa; text-align: center; padding: 1rem; border-top: 1px solid #555555;">
        ⚠️ This is an AI assistant and not a replacement for professional mental health support.<br>
        If you're in crisis, please contact emergency services or a mental health professional.
    </div>
""", unsafe_allow_html=True)