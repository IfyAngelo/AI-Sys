from fastapi import APIRouter, Body, HTTPException
from src.education_ai_system.services.generators import ContentGenerator
from src.education_ai_system.services.pinecone_service import VectorizationService
from src.education_ai_system.utils.validators import validate_user_input
from src.education_ai_system.utils.session_manager import SessionManager

router = APIRouter()
generator = ContentGenerator()
session_mgr = SessionManager()

@router.post("/scheme-of-work")
async def generate_scheme(payload: dict = Body(...)):
    if not validate_user_input(payload):
        raise HTTPException(400, detail="Invalid input parameters")
    
    try:
        scheme_content = generator.generate("scheme_of_work", payload)
        scheme_id = session_mgr.create_scheme({
            "payload": payload,
            "content": scheme_content
        })
        
        return {
            "scheme_of_work_id": scheme_id,
            "scheme_of_work_output": scheme_content,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@router.post("/lesson-plan")
async def generate_lesson_plan(payload: dict = Body(...)):
    scheme_id = payload.get("scheme_of_work_id")
    
    if not scheme_id or not session_mgr.get_scheme(scheme_id):
        raise HTTPException(400, detail="Invalid scheme ID")
    
    try:
        # Get scheme data from database
        scheme_data = session_mgr.get_scheme(scheme_id)
        if not scheme_data:
            raise HTTPException(404, detail="Associated scheme not found")

        # Generate lesson plan content with constraints
        lesson_content = generator.generate("lesson_plan", {
            **payload,
            "curriculum_context": scheme_data.get("content", ""),
            "teaching_constraints": payload.get("limitations", "")
        })
        
        # Store in database
        lesson_plan_id = session_mgr.create_lesson_plan(scheme_id, {
            "payload": payload,
            "content": lesson_content
        })
        
        return {
            "scheme_of_work_id": scheme_id,
            "lesson_plan_id": lesson_plan_id,
            "lesson_plan_output": lesson_content,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@router.post("/lesson-notes")
async def generate_notes(payload: dict = Body(...)):
    required_fields = ["scheme_of_work_id", "lesson_plan_id"]
    if any(field not in payload for field in required_fields):
        raise HTTPException(400, detail="Missing required fields in payload")

    scheme_id = payload["scheme_of_work_id"]
    lesson_plan_id = payload["lesson_plan_id"]
    
    try:
        # Get database records
        scheme = session_mgr.get_scheme(scheme_id)
        lesson_plan = session_mgr.get_lesson_plan(lesson_plan_id)
        
        if not scheme or not lesson_plan:
            raise HTTPException(404, detail="Associated content not found")

        # Generate notes
        notes_content = generator.generate("lesson_notes", {
            "subject": payload.get("subject", scheme.get("payload", {}).get("subject", "")),
            "grade_level": payload.get("grade_level", scheme.get("payload", {}).get("grade_level", "")),
            "topic": payload.get("topic", scheme.get("payload", {}).get("topic", "")),
            "scheme_context": scheme.get("content", ""),
            "lesson_plan_context": lesson_plan.get("content", "")
        })
        
        # Store in database
        notes_id = session_mgr.create_lesson_notes(
            scheme_id,
            lesson_plan_id,
            {
                "payload": payload,
                "content": notes_content
            }
        )
        
        return {
            "scheme_of_work_id": scheme_id,
            "lesson_plan_id": lesson_plan_id,
            "lesson_notes_id": notes_id,
            "content": notes_content,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(500, detail=f"Generation failed: {str(e)}")
