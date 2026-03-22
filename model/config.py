# config.py
import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY is None:
    raise ValueError("GEMINI_API_KEY is missing. Add it to your .env file.")

MODEL_NAME = "gemini-2.5-flash-lite"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"