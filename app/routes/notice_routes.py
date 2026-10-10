"""
FastAPI route handlers for CampusMate AI.
Exposes endpoints for health checks, notice analysis, and Q&A.
"""
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status, Request
from google.genai.errors import ClientError, APIError

from app.config import settings
from app.schemas.notice_schemas import (
    HealthResponse,
    AnalyzeNoticeRequest,
    AnalyzeNoticeResponse,
    AskQuestionRequest,
    AskQuestionResponse
)
from app.services.notice_service import notice_service

router = APIRouter(prefix="/api", tags=["CampusMate AI"])

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    Returns operational status and verifies whether AI configuration is present.
    Never exposes API keys or secrets.
    """
    return HealthResponse(
        status="ok",
        application="CampusMate AI",
        version="1.0.0",
        ai_configured=settings.is_gemini_configured
    )

@router.post("/notices/analyze", response_model=AnalyzeNoticeResponse)
async def analyze_notice_form(
    request: Request,
    file: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(None),
    language: str = Form("English")
):
    """
    Analyze a college notice uploaded as a file (PDF, Image) or submitted as form text.
    Returns structured summary, important dates, facts, checklist, and missing info.
    """
    try:
        file_bytes = None
        filename = None
        if file and file.filename:
            file_bytes = await file.read()
            filename = file.filename

        result = notice_service.process_and_analyze(
            text=text,
            file_bytes=file_bytes,
            filename=filename,
            language=language
        )
        return result

    except ValueError as ve:
        err_msg = str(ve)
        if "exceeds the maximum limit" in err_msg:
            raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=err_msg)
        elif "Unsupported file format" in err_msg:
            raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail=err_msg)
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err_msg)

    except ClientError as ce:
        err_text = str(ce)
        if "API_KEY_INVALID" in err_text or "401" in err_text or "403" in err_text:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Authentication failed with Google Gemini API. Please check your GEMINI_API_KEY."
            )
        elif "RESOURCE_EXHAUSTED" in err_text or "429" in err_text:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Gemini API rate limit reached. Please wait a few seconds and try again."
            )
        elif "NOT_FOUND" in err_text or "404" in err_text:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Configured Gemini model is not found or unavailable. Please check GEMINI_MODEL."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Google Gemini service error: {err_text[:150]}"
            )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred while analyzing the notice: {str(e)}"
        )

@router.post("/notices/analyze-json", response_model=AnalyzeNoticeResponse)
async def analyze_notice_json(payload: AnalyzeNoticeRequest):
    """
    JSON payload endpoint for analyzing raw notice text.
    """
    try:
        return notice_service.process_and_analyze(
            text=payload.text,
            language=payload.language
        )
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except ClientError as ce:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(ce))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/notices/ask", response_model=AskQuestionResponse)
async def ask_notice_question(payload: AskQuestionRequest):
    """
    Ask a question regarding the currently loaded notice.
    Strictly grounded in the provided notice.
    """
    try:
        return notice_service.answer_notice_question(
            notice_text=payload.notice_text,
            question=payload.question,
            language=payload.language
        )
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except ClientError as ce:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI service error during Q&A: {str(ce)[:150]}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process question: {str(e)}"
        )
