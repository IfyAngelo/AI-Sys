# main.py
import asyncio
from fastapi import FastAPI
from dotenv import load_dotenv
from src.education_ai_system.api import (
    embeddings_routes,
    docx_conversion_routes,
    content_routes
)
from src.education_ai_system.utils.session_manager import SessionManager

load_dotenv()

app = FastAPI(
    title="Curriculum Builder API",
    description="API for Nigerian Curriculum Content Generation",
    version="1.0.0"
)

session_mgr = SessionManager()

# Include all routers
app.include_router(
    content_routes.router,
    prefix="/api/content",
    tags=["Content Generation"]
)

app.include_router(
    embeddings_routes.router,
    prefix="/api/embeddings",
    tags=["PDF Processing"]
)

app.include_router(
    docx_conversion_routes.router,
    prefix="/api/convert",
    tags=["Document Conversion"]
)

@app.get("/")
async def health_check():
    return {
        "status": "active",
        "version": app.version,
        "endpoints": {
            "process_pdf": "/api/embeddings/process_pdf",
            "generate_lesson_plan": "/api/content/generate/lesson_plan",
            "generate_scheme": "/api/content/generate/scheme_of_work",
            "generate_notes": "/api/content/generate/lesson_notes",
            "convert_docx": "/api/convert/convert_md_to_docx"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)