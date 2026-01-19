import os

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
PORT = os.getenv("PORT", "8000")
GENERATING_MODEL = os.getenv("GENERATING_MODEL", "gemma3n:e2b")