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
        kwargs = {"api_key": key, "model": model_name, "timeout": 120}
        # Some models don't support temperature
        if "o1" not in model_name and "gpt-6" not in model_name:
            kwargs["temperature"] = temperature
        return ChatOpenAI(**kwargs)
        
    return init_chat_model(os.getenv("LAB_MODEL", "deepseek:deepseek-chat"), temperature=temperature)
