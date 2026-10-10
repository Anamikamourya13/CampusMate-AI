"""
Notice intelligence service orchestrator for CampusMate AI.
Coordinates file extraction, validation, and Gemini AI processing.
"""
from typing import Optional, Tuple
from app.services.document_service import document_service
from app.services.gemini_service import gemini_service
from app.schemas.notice_schemas import AnalyzeNoticeResponse, AskQuestionResponse
from app.utils.validators import (
    validate_notice_text,
    validate_question,
    validate_upload_meta,
    sanitize_language
)

class NoticeService:
    """Coordinates notice text extraction, file handling, and AI analysis."""

    def process_and_analyze(
        self,
        text: Optional[str] = None,
        file_bytes: Optional[bytes] = None,
        filename: Optional[str] = None,
        language: str = "English"
    ) -> AnalyzeNoticeResponse:
        """
        Process incoming notice input (text, PDF, image, or TXT) and run Gemini analysis.
        """
        target_lang = sanitize_language(language)

        # Case 1: File is provided
        if file_bytes and filename:
            cleaned_filename, ext = validate_upload_meta(filename, len(file_bytes))

            if ext == ".pdf":
                extracted_text = document_service.extract_from_pdf(file_bytes)
                valid_text = validate_notice_text(extracted_text)
                return gemini_service.analyze_notice(notice_text=valid_text, language=target_lang)

            elif ext in (".png", ".jpg", ".jpeg", ".webp"):
                img_data, mime = document_service.validate_and_prepare_image(file_bytes, cleaned_filename)
                # Multimodal analysis directly with image bytes
                return gemini_service.analyze_notice(
                    notice_text=text,
                    language=target_lang,
                    image_bytes=img_data,
                    image_mime=mime
                )

            elif ext == ".txt":
                extracted_text = document_service.extract_from_txt(file_bytes)
                valid_text = validate_notice_text(extracted_text)
                return gemini_service.analyze_notice(notice_text=valid_text, language=target_lang)

            else:
                raise ValueError(f"Unsupported file type '{ext}'.")

        # Case 2: Plain text provided
        elif text:
            valid_text = validate_notice_text(text)
            return gemini_service.analyze_notice(notice_text=valid_text, language=target_lang)

        else:
            raise ValueError("Please provide either notice text or upload a document (PDF/Image).")

    def answer_notice_question(
        self,
        notice_text: str,
        question: str,
        language: str = "English"
    ) -> AskQuestionResponse:
        """
        Validate context and question, then generate grounded answer.
        """
        valid_text = validate_notice_text(notice_text)
        valid_q = validate_question(question)
        target_lang = sanitize_language(language)

        return gemini_service.ask_question(
            notice_text=valid_text,
            question=valid_q,
            language=target_lang
        )

notice_service = NoticeService()
