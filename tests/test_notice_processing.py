"""
Unit tests for PDF extraction, corrupt file handling, configuration,
structured output validation, and question answering.
"""
import io
import pymupdf
import pytest
from app.services.document_service import document_service
from app.schemas.notice_schemas import (
    AnalyzeNoticeResponse,
    AskQuestionResponse,
    ImportantDateItem,
    ImportantInfoItem
)
from app.config import Settings

def test_pdf_extraction_valid():
    """Test 5 — Verify that text can be extracted from a valid text-based PDF."""
    # Create an in-memory PDF using PyMuPDF
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text(
        (50, 72),
        "Official College Notice: The End-Semester Examinations will commence from 15 November 2026. All students must report by 9:30 AM."
    )
    pdf_bytes = doc.write()
    doc.close()

    extracted = document_service.extract_from_pdf(pdf_bytes)
    assert "End-Semester Examinations" in extracted
    assert "15 November 2026" in extracted

def test_invalid_or_corrupt_pdf():
    """Test 6 — Verify that corrupt PDFs produce a useful error."""
    corrupt_bytes = b"%PDF-1.4 definitely not a valid pdf content random garbage"
    with pytest.raises(ValueError) as excinfo:
        document_service.extract_from_pdf(corrupt_bytes)
    assert "Unable to read this PDF" in str(excinfo.value)

def test_scanned_pdf_error_message():
    """Verify that an empty/scanned PDF raises a helpful informative error."""
    doc = pymupdf.open()
    doc.new_page()  # Blank page with no text
    pdf_bytes = doc.write()
    doc.close()

    with pytest.raises(ValueError) as excinfo:
        document_service.extract_from_pdf(pdf_bytes)
    assert "scanned pages" in str(excinfo.value).lower()

def test_gemini_configuration_check():
    """Test 7 — Verify that missing API key is identified correctly."""
    empty_settings = Settings()
    empty_settings.GEMINI_API_KEY = ""
    assert empty_settings.is_gemini_configured is False

def test_structured_response_validation():
    """Test 8 — Verify structured response Pydantic schema validation."""
    valid_data = {
        "success": True,
        "notice_title": "End-Sem Exam Notice",
        "issuing_authority": "Office of the Dean Academic Affairs",
        "notice_date": "10 Oct 2026",
        "urgency": "Upcoming",
        "summary": ["Exams start 15 Nov", "Carry college ID card"],
        "important_information": [{"label": "Department", "value": "Academics"}],
        "dates": [{"event": "Exam", "date": "15 Nov 2026", "time": "9:30 AM", "venue": "Main Hall", "category": "examination"}],
        "action_items": ["Carry college identity card"],
        "missing_information": ["Room seating allocation not mentioned"],
        "language": "English"
    }
    response = AnalyzeNoticeResponse(**valid_data)
    assert response.notice_title == "End-Sem Exam Notice"
    assert len(response.dates) == 1
    assert response.dates[0].venue == "Main Hall"

def test_missing_information_representation():
    """Test 9 — Verify that absent information is represented without fabricating values."""
    date_item = ImportantDateItem(
        event="Assignment Submission",
        date="12 Nov 2026",
        time="Not mentioned",
        venue="Not mentioned",
        category="deadline"
    )
    assert date_item.time == "Not mentioned"
    assert date_item.venue == "Not mentioned"

def test_question_answering_schema():
    """Test 10 — Verify AskQuestionResponse distinguishes found vs not found."""
    found_resp = AskQuestionResponse(
        answer="The examination begins on 15 November 2026.",
        found_in_notice=True,
        language="English"
    )
    assert found_resp.found_in_notice is True

    unfound_resp = AskQuestionResponse(
        answer="The notice does not specify where the assignment must be submitted.",
        found_in_notice=False,
        language="English"
    )
    assert unfound_resp.found_in_notice is False
