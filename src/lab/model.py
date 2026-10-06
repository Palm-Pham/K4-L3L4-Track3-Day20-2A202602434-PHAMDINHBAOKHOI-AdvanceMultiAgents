"""Builds the chat model from environment variables (see .env)."""
import os

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()


def make_model():
    """Return a chat model configured from the environment."""
    temperature = float(os.getenv("LAB_TEMPERATURE", "0"))
    key = os.getenv("OPENAI_API_KEY")
    model_name = os.getenv("OPENAI_MODEL", "gpt-4o")
    
    if key:
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(api_key=key, model=model_name, temperature=temperature, timeout=120)
        
    return init_chat_model(os.getenv("LAB_MODEL", "deepseek:deepseek-chat"), temperature=temperature)
