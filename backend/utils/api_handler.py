import time
import os
import logging
from typing import Any
from langchain_google_genai import ChatGoogleGenerativeAI

logger = logging.getLogger(__name__)

# Load multiple keys from an environment variable (comma-separated) or fallback to single key
raw_keys = os.getenv("HACKATHON_API_KEYS", "")
API_KEYS = [k.strip() for k in raw_keys.split(",") if k.strip()]

# Add standard env key if valid
env_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
if env_key and env_key not in API_KEYS:
    API_KEYS.insert(0, env_key)

# If no keys provided at all, we shouldn't fail instantly but warn
if not API_KEYS:
    logger.warning("No API Keys found! Please set GEMINI_API_KEY or HACKATHON_API_KEYS in your .env file.")
    API_KEYS = ["MISSING_API_KEY"] # Placeholder to prevent index errors before failure

_current_key_idx = 0

def get_next_key() -> str:
    global _current_key_idx
    key = API_KEYS[_current_key_idx]
    _current_key_idx = (_current_key_idx + 1) % len(API_KEYS)
    return key

def get_llm(model: str = "gemini-2.0-flash") -> ChatGoogleGenerativeAI:
    """Returns a new ChatGoogleGenerativeAI instance with the next rotated API key."""
    key = get_next_key()
    return ChatGoogleGenerativeAI(model=model, google_api_key=key)

def safe_llm_invoke(llm: ChatGoogleGenerativeAI, messages: Any, **kwargs) -> Any:
    """
    Robust retry with Key Rotation and Model Fallback on Quota errors.
    """
    models_to_try = [llm.model, "gemini-2.5-flash"]
    total_keys = max(1, len(API_KEYS))
    
    for current_model in models_to_try:
        if not current_model:
            continue
            
        for i in range(total_keys):
            try:
                # Update model if we fell back
                if llm.model != current_model:
                    new_key = get_next_key()
                    llm = ChatGoogleGenerativeAI(model=current_model, google_api_key=new_key)
                return llm.invoke(messages, **kwargs)
            except Exception as e:
                error_str = str(e).lower()
                if "429" in error_str or "exhausted" in error_str or "quota" in error_str:
                    logger.warning(f"Quota hit for {current_model}! Rotating key... (Attempt {i+1}/{total_keys})")
                    time.sleep(1) # Underlying client already backs off, so we keep this brief
                    # Rotate key
                    new_key = get_next_key()
                    llm = ChatGoogleGenerativeAI(model=current_model, google_api_key=new_key)
                    continue
                else:
                    # Other errors should crash/return normally
                    raise e
                    
    raise Exception("Error: API is currently overloaded across all available keys and fallback models. Please try again later.")
