# backend/test_azure_openai.py

import os
import getpass
from langchain_openai import AzureChatOpenAI
from dotenv import load_dotenv

load_dotenv()
# Set up Azure OpenAI credentials
if "AZURE_OPENAI_API_KEY" not in os.environ:
    os.environ["AZURE_OPENAI_API_KEY"] = getpass.getpass("Enter your AzureOpenAI API key: ")

os.environ["AZURE_OPENAI_ENDPOINT"] = "https://langrag.openai.azure.com/"

# Initialize Azure OpenAI
llm = AzureChatOpenAI(
    azure_deployment="gpt-4",
    api_version="2024-08-01-preview",
    temperature=0.7,  
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

# # Define therapist personality
# system_prompt = """You are an empathetic and professional therapist. 
# Your responses should be:
# - Compassionate and understanding
# - Non-judgmental
# - Focused on active listening
# - Professional but warm
# - Encouraging but not dismissive
# Never give medical advice or diagnoses."""

# # Test conversation
# messages = [
#     ("system", system_prompt),
#     ("human", "I've been feeling really anxious lately and I can't sleep.")
# ]

# # Get response
# response = llm.invoke(messages)
# print("\nTherapist:", response.content)

# # Test follow-up question
# messages.append(("assistant", response.content))
# messages.append(("human", "What can I do to feel better?"))
# response = llm.invoke(messages)
# print("\nTherapist:", response.content)

messages = [
    (
        "system",
        "You are a helpful assistant that translates English to French. Translate the user sentence.",
    ),
    ("human", "I love programming."),
]
ai_msg = llm.invoke(messages)
ai_msg

print(ai_msg.content)