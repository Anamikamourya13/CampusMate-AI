"""
Input validation utilities for CampusMate AI.
Ensures security, bounds checking, and clean error messages.
"""
import os
from typing import Tuple
from app.config import settings

ALLOWED_EXTENSIONS = {".txt", ".pdf", ".png", ".jpg", ".jpeg", ".webp"}
ALLOWED_LANGUAGES = {"English", "Hindi", "Hinglish"}

def validate_notice_text(text: str) -> str:
    """
    Validate raw notice text.
    Ensures non-empty and within character limits.
    """
    if not text:
        raise ValueError("Please provide the text of the college notice to analyze.")
    
    cleaned = text.strip()
    if len(cleaned) < settings.MIN_NOTICE_CHARS:
        raise ValueError(
            f"The notice text is too short ({len(cleaned)} characters). "
            f"Please provide at least {settings.MIN_NOTICE_CHARS} characters of notice content."
        )
    
    if len(cleaned) > settings.MAX_NOTICE_CHARS:
        raise ValueError(
            f"The notice text exceeds the maximum allowed length "
            f"({len(cleaned)} / {settings.MAX_NOTICE_CHARS} characters). "
            f"Please provide a shorter notice or section."
        )
    
    return cleaned

def validate_question(question: str) -> str:
    """
    Validate student question.
    """
    if not question:
        raise ValueError("Please enter a question to ask about the notice.")
    
    cleaned = question.strip()
    if len(cleaned) < 3:
        raise ValueError("Question is too short. Please ask a specific question.")
    
    if len(cleaned) > settings.MAX_QUESTION_CHARS:
        raise ValueError(
            f"Question is too long ({len(cleaned)} characters). "
            f"Maximum length is {settings.MAX_QUESTION_CHARS} characters."
        )
    
    return cleaned

def validate_upload_meta(filename: str, file_size: int) -> Tuple[str, str]:
    """
    Validate uploaded file name and size before processing.
    Returns (cleaned_filename, extension).
    """
    if not filename:
        raise ValueError("Uploaded file must have a valid filename.")
    
    _, ext = os.path.splitext(filename.lower())
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file format '{ext}'. "
            f"Supported formats: PDF, PNG, JPG, JPEG, WEBP, TXT."
        )
    
    if file_size <= 0:
        raise ValueError("The uploaded file appears to be empty (0 bytes).")
    
    if file_size > settings.MAX_UPLOAD_BYTES:
        max_mb = settings.MAX_UPLOAD_MB
        raise ValueError(
            f"Uploaded file exceeds the maximum limit of {max_mb} MB "
            f"({file_size / (1024*1024):.1f} MB provided)."
        )
    
    return filename, ext

def sanitize_language(language: str) -> str:
    """
    Normalize requested language to English, Hindi, or Hinglish.
    """
    if not language:
        return "English"
    lang_clean = language.strip().capitalize()
    if lang_clean in ALLOWED_LANGUAGES:
        return lang_clean
    # Handle localized spellings
    if "hind" in lang_clean.lower():
        if "hing" in lang_clean.lower():
            return "Hinglish"
        return "Hindi"
    return "English"
