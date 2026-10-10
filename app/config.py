"""
Configuration management for CampusMate AI.
Loads settings from .env file securely.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Look for .env in current file's parent directories or root
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent

env_path = project_root / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

class Settings:
    """Application settings and configuration parameters."""
    
    # Environment
    APP_ENV: str = os.getenv("APP_ENV", "development").strip()
    DEBUG: bool = APP_ENV.lower() == "development"
    
    # Gemini AI configuration
    # Strip whitespace from keys and values in case .env has trailing spaces
    GEMINI_API_KEY: str = (
        os.getenv("GEMINI_API_KEY") or 
        os.getenv("GEMINI_API_KEY ") or 
        ""
    ).strip()
    
    # Configurable Gemini model identifier
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.8-flash").strip()
    
    # Server network settings
    HOST: str = os.getenv("HOST", "0.0.0.0").strip()
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Upload limits
    MAX_UPLOAD_MB: int = int(os.getenv("MAX_UPLOAD_MB", "10"))
    MAX_UPLOAD_BYTES: int = MAX_UPLOAD_MB * 1024 * 1024
    
    # Text length limits
    MIN_NOTICE_CHARS: int = 15
    MAX_NOTICE_CHARS: int = 50000
    MAX_QUESTION_CHARS: int = 500
    
    @property
    def is_gemini_configured(self) -> bool:
        """Check if a non-empty Gemini API key is configured."""
        return bool(self.GEMINI_API_KEY and len(self.GEMINI_API_KEY) > 10)

settings = Settings()
