import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "study-guide-app")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///studybuddy.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_TYPE = os.getenv("SESSION_TYPE", "filesystem")
    # CORS origin (frontend)
    FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
    # Gemini key
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
