import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    UPLOAD_DIR = "uploads"
    OUTPUT_DIR = "outputs"

settings = Settings()
