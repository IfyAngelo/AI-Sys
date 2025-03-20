from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import FileResponse
from src.education_ai_system.utils.file_operations import convert_md_to_docx, load_inputs
from pathlib import Path
import uuid
import os
from src.education_ai_system.utils.session_manager import SessionManager
from datetime import datetime

router = APIRouter()
session_mgr = SessionManager()

@router.post("/generate-document")
async def generate_document(
    content_type: str = Body(..., embed=True),
    scheme_of_work_id: str = Body(None),
    lesson_plan_id: str = Body(None),
    lesson_notes_id: str = Body(None),
    custom_filename: str = Body(None)
):
    """Convert curriculum content to DOCX format"""
    try:
        # Validate content type
        valid_types = ["scheme", "lesson_plan", "lesson_notes"]
        if content_type not in valid_types:
            raise HTTPException(400, detail=f"Invalid content type. Valid options: {', '.join(valid_types)}")

        content = None
        metadata = {}
        
        # Retrieve content with proper validation
        if content_type == "scheme":
            if not scheme_of_work_id:
                raise HTTPException(400, detail="scheme_of_work_id required for scheme documents")
                
            scheme = session_mgr.get_scheme(scheme_of_work_id)
            if not scheme:
                raise HTTPException(404, detail="Scheme not found")
                
            content = scheme.get("data", {}).get("content")
            metadata = scheme.get("data", {}).get("payload", {})

        elif content_type == "lesson_plan":
            if not lesson_plan_id:
                raise HTTPException(400, detail="lesson_plan_id required for lesson plans")
                
            lesson_plan = session_mgr.get_lesson_plan(lesson_plan_id)
            if not lesson_plan:
                raise HTTPException(404, detail="Lesson plan not found")
                
            scheme = session_mgr.get_scheme(lesson_plan.get("scheme_id"))
            if not scheme:
                raise HTTPException(404, detail="Associated scheme not found")
                
            content = lesson_plan.get("data", {}).get("content")
            metadata = scheme.get("data", {}).get("payload", {})

        elif content_type == "lesson_notes":
            if not lesson_notes_id:
                raise HTTPException(400, detail="lesson_notes_id required for lesson notes")
                
            notes = session_mgr.get_lesson_notes(lesson_notes_id)
            if not notes:
                raise HTTPException(404, detail="Lesson notes not found")
                
            lesson_plan = session_mgr.get_lesson_plan(notes.get("lesson_plan_id"))
            if not lesson_plan:
                raise HTTPException(404, detail="Associated lesson plan not found")
                
            scheme = session_mgr.get_scheme(notes.get("scheme_id"))
            if not scheme:
                raise HTTPException(404, detail="Associated scheme not found")
                
            content = notes.get("data", {}).get("content")
            metadata = scheme.get("data", {}).get("payload", {})

        # Validate content exists
        if not content:
            raise HTTPException(404, detail="Content not found in stored data")

        # Rest of the implementation remains the same...
        # [Keep the filename generation and DOCX conversion code here]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, detail=f"Unexpected error: {str(e)}")
