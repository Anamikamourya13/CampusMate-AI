# 🎓 CampusMate AI — Smart Campus Assistant
> **Your Campus. Your Notices. Your AI Assistant.**  
> *AI-Powered College Notice Intelligence built with Google Gemini API & FastAPI*

---

## 📌 1. Project Overview

**CampusMate AI** is an intelligent web application designed to solve a ubiquitous student problem: reading through long, convoluted college notices, circulars, and administrative PDFs to find out what actually matters.

Students frequently receive lengthy notices containing examination schedules, assignment deadlines, hostel fee notices, and attendance warnings written in formal legalese. Important dates and crucial instructions often get buried.

**CampusMate AI** transforms these complex notices into:
- ⚡ **Concise AI Summaries** (3–6 clear bullet points).
- 📅 **Extracted Important Dates & Deadlines** (Events, dates, times, venues, and categories).
- ✅ **Actionable Student Checklists** (Interactive tasks with real-time completion tracking).
- ⚠️ **Missing Information Disclosures** (Honest reporting of omitted details, such as missing venues or contact info).
- 💬 **Ask Your Notice (Grounded Q&A)** (Chat directly with the analyzed notice; no hallucinations or invented facts).
- 🌐 **Multilingual Explanations** (English, हिंदी / Hindi, and Hinglish).

---

## 🚀 2. Architecture & Tech Stack

CampusMate AI is built as a clean, lightweight, single-page application served directly by FastAPI.

```
                    ┌──────────────────────────────┐
                    │     Frontend Single-Page     │
                    │   HTML5 / Modern CSS / JS    │
                    └──────────────┬───────────────┘
                                   │ HTTP (REST)
                                   ▼
                    ┌──────────────────────────────┐
                    │     FastAPI Backend (Py)     │
                    │      Uvicorn ASGI Server     │
                    └──────┬───────────────┬───────┘
                           │               │
            Document Parser│               │LLM Inference
                           ▼               ▼
           ┌──────────────────────┐ ┌──────────────────────┐
           │ PyMuPDF (PDF Parser) │ │   Google Gemini API  │
           │  Pillow (Image OCR)  │ │ (google-genai SDK)   │
           └──────────────────────┘ └──────────────────────┘
```

### Technology Matrix
| Component | Technology | Description |
|---|---|---|
| **Frontend** | HTML5, CSS3, Vanilla JavaScript (ES Modules) | Responsive campus-tech dashboard with Dark/Light themes |
| **Backend Framework** | FastAPI (Python 3.10+) | High-performance asynchronous API service |
| **AI Provider** | **Google Gemini API** | Real multimodal LLM inference via official `google-genai` SDK |
| **Document Processing** | PyMuPDF (`pymupdf`), Pillow (`PIL`) | PDF text extraction and image validation |
| **Schema Validation** | Pydantic v2 | Strict request/response typing and JSON schema enforcement |
| **Testing** | Pytest | Complete test suite covering health, validation, and AI parsing |
| **Environment** | `python-dotenv` | Secure local credential management |

> **Note on AI Model**: This application strictly utilizes the **Google Gemini API** (via the official `google-genai` SDK). It has **zero dependencies on Gemma 4** and runs 100% independently.

---

## 📁 3. Project Directory Structure

```
CampusMate-AI/
├── app/
│   ├── __init__.py               # Package metadata
│   ├── main.py                   # FastAPI app, middleware, and asset mounts
│   ├── config.py                 # Configuration and environment variable loader
│   ├── routes/
│   │   ├── __init__.py
│   │   └── notice_routes.py      # /api/health, /api/notices/analyze, /api/notices/ask
│   ├── services/
│   │   ├── __init__.py
│   │   ├── gemini_service.py     # Gemini client, prompt engineering & model fallbacks
│   │   ├── notice_service.py     # Business logic coordinator
│   │   └── document_service.py   # PDF text extraction and image preparation
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── notice_schemas.py     # Pydantic models for structured AI output
│   └── utils/
│       ├── __init__.py
│       └── validators.py         # Character bounds, file types, and sanitation
├── frontend/
│   ├── index.html                # Responsive single-page dashboard
│   ├── style.css                 # Custom CSS design system (Dark & Light themes)
│   ├── src/
│   │   ├── main.js               # Application logic, tabs, sample loader, and checklist
│   │   ├── api.js                # Fetch API client
│   │   ├── state.js              # Client state & localStorage persistence
│   │   └── utils.js              # Toasts, escaping, and formatting
│   └── assets/
│       └── logo.svg              # Custom CampusMate AI vector logo
├── tests/
│   ├── __init__.py
│   ├── test_health.py            # Health endpoint test
│   ├── test_validation.py        # Input limits, oversized files, unsupported types
│   └── test_notice_processing.py # PDF extraction, corruption handling, schema validation
├── .env                          # Local environment variables (Not committed)
├── .env.example                  # Template for environment configuration
├── .gitignore                    # Git exclusions
├── requirements.txt              # Production and test dependencies
├── README.md                     # Project documentation
└── run.py                        # Server startup launcher
```

---

## ⚡ 4. Quickstart & Local Setup

### Prerequisites
- Python 3.10 or higher
- A Google Gemini API Key from [Google AI Studio](https://aistudio.google.com/apikey)

### Step 1: Clone or Navigate to Directory
```bash
cd "D:\IIT BHILAI HACKTOCTUBER\CampusMate-AI"
```

### Step 2: Create and Activate Virtual Environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
Copy `.env.example` to `.env` and provide your Google Gemini API key:
```bash
copy .env.example .env
```
Edit `.env`:
```ini
GEMINI_API_KEY=MAI NHI BATAUNGA KHUD SE KRO
GEMINI_MODEL=gemini-3.5-flash
APP_ENV=development
MAX_UPLOAD_MB=10
HOST=0.0.0.0
PORT=8000
```

### Step 5: Start the Application
```bash
python run.py
```
Open your browser at: **`http://localhost:8000`**

---

## 🧪 5. Automated Testing

Run the full automated test suite using `pytest`:
```bash
pytest tests/ -v
```
All 13 tests verify:
- Health check endpoint (`GET /api/health`)
- Rejection of empty or too-short notices
- Rejection of unsupported file types (`.exe`, `.zip`)
- Enforcement of maximum upload sizes (10 MB)
- Text-based PDF extraction with PyMuPDF
- Corruption detection for damaged PDFs
- Informative error handling for scanned/blank PDFs
- Gemini configuration validation
- Pydantic schema validation on AI JSON responses
- Representation of missing facts (`"Not mentioned"`)
- Grounded Q&A response validation (`found_in_notice: true` vs `false`)

---

## 📡 6. API Reference

### 1. Health Check
- **Endpoint**: `GET /api/health`
- **Response**:
```json
{
  "status": "ok",
  "application": "CampusMate AI",
  "version": "1.0.0",
  "ai_configured": true
}
```

### 2. Analyze Notice
- **Endpoint**: `POST /api/notices/analyze`
- **Content-Type**: `multipart/form-data`
- **Fields**:
  - `file`: (Optional) PDF, PNG, JPG, or TXT file
  - `text`: (Optional) Notice raw text
  - `language`: `English`, `Hindi`, or `Hinglish`
- **Response**:
```json
{
  "success": true,
  "notice_title": "End-Semester Examinations - Autumn 2026",
  "issuing_authority": "Dean of Academic Affairs, IIT Bhilai",
  "notice_date": "10 October 2026",
  "urgency": "Upcoming",
  "summary": [
    "Exams will commence from 15 November 2026 to 28 November 2026.",
    "Students must report 30 minutes prior to exam start.",
    "Carry Institute ID card and printed Admit Card.",
    "Pending lab assignments must be submitted by 05 November 2026."
  ],
  "dates": [
    {
      "event": "Pending Lab Assignment Submission",
      "date": "05 November 2026",
      "time": "5:00 PM",
      "venue": "Academic Portal",
      "category": "deadline"
    },
    {
      "event": "Commencement of Examinations",
      "date": "15 November 2026",
      "time": "9:00 AM (Morning) / 2:00 PM (Afternoon)",
      "venue": "To be displayed on notice boards",
      "category": "examination"
    }
  ],
  "action_items": [
    "Submit pending lab assignments via portal before 05 November, 5:00 PM.",
    "Print Admit Card.",
    "Carry Institute ID card to exam hall.",
    "Report 30 minutes prior to exam start."
  ],
  "missing_information": [
    "Subject-wise schedule",
    "Specific exam room/hall numbers"
  ],
  "language": "English"
}
```

### 3. Ask Your Notice
- **Endpoint**: `POST /api/notices/ask`
- **Content-Type**: `application/json`
- **Body**:
```json
{
  "notice_text": "...",
  "question": "What documents do I need to carry?",
  "language": "English"
}
```
- **Response**:
```json
{
  "answer": "According to the notice, you must carry your valid physical Institute Identity Card and a printed copy of your Examination Admit Card.",
  "found_in_notice": true,
  "language": "English"
}
```

---

## 🔒 7. Security & Privacy

1. **API Key Protection**:
   - The Gemini API key is loaded only on the backend from `.env`.
   - Never embedded in source code, client-side bundles, or logs.
   - `.env` is ignored in `.gitignore`.
2. **Ephemeral Document Processing**:
   - Notices are parsed in-memory and processed ephemerally.
   - No database, user accounts, or persistent personal logs.
3. **Prompt Injection Defense**:
   - Uploaded notices are treated strictly as untrusted document context. System instructions prevent adversarial prompt hijacking from altering the assistant's persona or policies.
4. **Output Sanitization**:
   - All AI output and student inputs are HTML-escaped before DOM insertion to prevent Cross-Site Scripting (XSS).

---

## 💡 8. Known Limitations & Future Roadmap

- **Scanned Image-Only PDFs**: Text extraction currently expects text-layer PDFs. For scanned documents, students can upload the notice directly as an image (PNG/JPG) where Gemini's native vision analyzes the document directly.
- **Future Improvements**:
  - Export checklist items directly to Google Calendar / `.ics` format.
  - Multi-notice comparison (e.g. comparing conflicting exam and placement schedules).
  - Audio summary narration for visually impaired students.

---

## 📜 9. License

Developed for **IIT Bhilai Hacktoberfest 2026**. Released under the MIT License.
