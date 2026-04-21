from src.utils.config import get_settings

settings = get_settings()
print(f"LLM Provider: {settings.llm_provider}")
print(f"LLM Model: {settings.llm_model}")
print(f"Groq API Key exists: {settings.groq_api_key is not None}")
print(f"Groq API Key starts with 'gsk_': {settings.groq_api_key.startswith('gsk_') if settings.groq_api_key else False}")
print(f"Groq API Key length: {len(settings.groq_api_key) if settings.groq_api_key else 0}")
# Don't print the actual key for security!
