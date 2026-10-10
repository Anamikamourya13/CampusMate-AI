"""
Application launcher for CampusMate AI.
Starts the Uvicorn ASGI server with configurable host, port, and auto-reload.
"""
import sys
import uvicorn
from app.config import settings

# Ensure UTF-8 output on Windows terminals
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

def main():
    print("=" * 65)
    print("  [*] CampusMate AI -- Smart Campus Assistant")
    print("      Your Campus. Your Notices. Your AI Assistant.")
    print("=" * 65)
    print(f"  [+] Server URL:     http://localhost:{settings.PORT}")
    print(f"  [+] AI Model:       {settings.GEMINI_MODEL}")
    print(f"  [+] AI Configured:  {'Yes (Ready)' if settings.is_gemini_configured else 'No (Missing GEMINI_API_KEY in .env)'}")
    print(f"  [+] Environment:    {settings.APP_ENV}")
    print("=" * 65)
    print("  Press CTRL+C to stop the server.\n")

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )

if __name__ == "__main__":
    main()
