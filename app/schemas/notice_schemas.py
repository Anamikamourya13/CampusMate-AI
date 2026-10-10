"""
Pydantic schemas for CampusMate AI API requests and responses.
"""
from typing import List, Optional
from pydantic import BaseModel, Field

class ImportantDateItem(BaseModel):
    """Represents a date, deadline, or scheduled event extracted from the notice."""
    event: str = Field(description="Name or description of the event or deadline")
    date: str = Field(description="Date as mentioned in the notice (normalized if clear)")
    time: str = Field(default="Not mentioned", description="Time of event or deadline")
    venue: str = Field(default="Not mentioned", description="Location or venue")
    category: str = Field(default="event", description="Category: examination, deadline, reporting, event, other")

class ImportantInfoItem(BaseModel):
    """Key factual item extracted from the notice."""
    label: str = Field(description="Label for this information (e.g. Issuing Authority, Eligibility, Required Documents)")
    value: str = Field(description="Extracted value or detail")

class AnalyzeNoticeRequest(BaseModel):
    """Request payload for notice text analysis."""
    text: Optional[str] = Field(default=None, description="Pasted college notice text")
    language: str = Field(default="English", description="Target response language: English, Hindi, or Hinglish")

class AnalyzeNoticeResponse(BaseModel):
    """Structured AI output for notice analysis."""
    success: bool = True
    notice_title: str = Field(default="College Notice", description="Extracted notice title or subject")
    issuing_authority: str = Field(default="Not mentioned", description="Department or authority that issued the notice")
    notice_date: str = Field(default="Not mentioned", description="Date the notice was released/signed")
    urgency: str = Field(default="Informational", description="Urgency level: Urgent, Upcoming, or Informational")
    summary: List[str] = Field(default_factory=list, description="Concise summary in 3-6 bullet points")
    important_information: List[ImportantInfoItem] = Field(default_factory=list, description="Factual attributes")
    dates: List[ImportantDateItem] = Field(default_factory=list, description="Extracted events and deadlines")
    action_items: List[str] = Field(default_factory=list, description="List of short actionable checklist tasks")
    missing_information: List[str] = Field(default_factory=list, description="Important details not specified in the notice")
    language: str = Field(default="English", description="Language of response")
    error: Optional[str] = None

class AskQuestionRequest(BaseModel):
    """Request payload for asking a question about a notice."""
    notice_text: str = Field(description="The full text context of the notice")
    question: str = Field(description="Student question regarding the notice")
    language: str = Field(default="English", description="Target response language: English, Hindi, or Hinglish")

class AskQuestionResponse(BaseModel):
    """Response payload for question answering."""
    answer: str = Field(description="Clear answer based strictly on the notice")
    found_in_notice: bool = Field(description="True if the answer is explicitly in the notice; False if missing/unspecified")
    language: str = Field(default="English", description="Language used for the answer")

class HealthResponse(BaseModel):
    """Health check response schema."""
    status: str = "ok"
    application: str = "CampusMate AI"
    version: str = "1.0.0"
    ai_configured: bool = True
