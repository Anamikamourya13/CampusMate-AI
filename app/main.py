"""
Main FastAPI Application entry point for CampusMate AI.
Configures middleware, routes, static asset serving, and exception handling.
"""
import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from app.config import settings
from app.routes.notice_routes import router as notice_router

app = FastAPI(
    title="CampusMate AI",
    description="Smart Campus Assistant | AI-Powered College Notice Intelligence",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(notice_router)

# Locate frontend directory
project_root = Path(__file__).resolve().parent.parent
frontend_dir = project_root / "frontend"

if frontend_dir.exists():
    # Mount assets and source files if present
    assets_dir = frontend_dir / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    src_dir = frontend_dir / "src"
    if src_dir.exists():
        app.mount("/src", StaticFiles(directory=str(src_dir)), name="src")

    @app.get("/", include_in_schema=False)
    async def serve_index():
        """Serve the single-page frontend application."""
        index_file = frontend_dir / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
        return JSONResponse({"message": "CampusMate AI Backend is running. Frontend index.html not found."})

    @app.get("/style.css", include_in_schema=False)
    async def serve_css():
        """Serve the custom frontend stylesheet."""
        css_file = frontend_dir / "style.css"
        if css_file.exists():
            return FileResponse(str(css_file), media_type="text/css")
        return JSONResponse({"detail": "style.css not found"}, status_code=404)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Clean validation error response for client requests."""
    errors = exc.errors()
    first_err = errors[0]["msg"] if errors else "Invalid request input."
    return JSONResponse(
        status_code=422,
        content={"detail": first_err, "errors": errors}
    )
