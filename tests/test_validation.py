"""
Unit tests for input validation, file uploads, and limits.
"""
import io
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.utils.validators import (
    validate_notice_text,
    validate_question,
    validate_upload_meta,
    sanitize_language
)

client = TestClient(app)

def test_empty_notice_rejection():
    """Test 2 — Verify that empty or overly short notice input is rejected."""
    # Test validator directly
    with pytest.raises(ValueError) as excinfo:
        validate_notice_text("")
    assert "Please provide" in str(excinfo.value)

    with pytest.raises(ValueError) as excinfo:
        validate_notice_text("   short   ")
    assert "too short" in str(excinfo.value)

    # Test via API
    resp = client.post("/api/notices/analyze-json", json={"text": "", "language": "English"})
    assert resp.status_code == 400

def test_unsupported_file_type():
    """Test 3 — Verify that unsupported uploads are rejected."""
    with pytest.raises(ValueError) as excinfo:
        validate_upload_meta("malicious_script.exe", 1024)
    assert "Unsupported file format" in str(excinfo.value)

    # Test via multipart API
    files = {"file": ("virus.exe", b"fake binary data", "application/octet-stream")}
    resp = client.post("/api/notices/analyze", files=files, data={"language": "English"})
    assert resp.status_code in (400, 415)

def test_oversized_file():
    """Test 4 — Verify that files exceeding the configured limit are rejected."""
    # 15 MB exceeding 10 MB limit
    oversized = 15 * 1024 * 1024
    with pytest.raises(ValueError) as excinfo:
        validate_upload_meta("huge_file.pdf", oversized)
    assert "exceeds the maximum limit" in str(excinfo.value)

def test_question_validation():
    """Verify question length and emptiness validation."""
    with pytest.raises(ValueError):
        validate_question("")

    with pytest.raises(ValueError):
        validate_question("hi")

    valid_q = validate_question("When is the end semester examination?")
    assert valid_q == "When is the end semester examination?"

def test_language_sanitization():
    """Verify language normalization."""
    assert sanitize_language("english") == "English"
    assert sanitize_language("hindi") == "Hindi"
    assert sanitize_language("hinglish") == "Hinglish"
    assert sanitize_language("unknown_lang") == "English"
