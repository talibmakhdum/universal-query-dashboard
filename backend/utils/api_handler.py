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
    Exponential Backoff and Key Rotation on Quota errors.
    """
    max_retries = 3
    for i in range(max_retries):
        try:
            return llm.invoke(messages, **kwargs)
        except Exception as e:
            error_str = str(e).lower()
            if "429" in error_str or "exhausted" in error_str or "quota" in error_str:
                wait_time = (i + 1) * 5
                logger.warning(f"Quota hit or rate limit exceeded! Retrying in {wait_time}s with a new key...")
                time.sleep(wait_time)
                # Rotate key by recreating LLM temporarily for next attempt
                new_key = get_next_key()
                llm = ChatGoogleGenerativeAI(model=llm.model, google_api_key=new_key)
                continue
            else:
                # Other errors should crash/return normally
                raise e
    
    raise Exception("Error: API is currently overloaded. Max retries exhausted. Please try again.")
