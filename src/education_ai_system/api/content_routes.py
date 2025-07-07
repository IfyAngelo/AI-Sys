from fastapi import APIRouter, Body, HTTPException
from src.education_ai_system.services.generators import ContentGenerator
from src.education_ai_system.services.pinecone_service import VectorizationService
from src.education_ai_system.utils.validators import validate_user_input, extract_week_topic, extract_week_content, load_predefined_inputs
from src.education_ai_system.utils.session_manager import SessionManager
from src.education_ai_system.tools.pinecone_exa_tools import PineconeRetrievalTool
import json

router = APIRouter()
generator = ContentGenerator()
session_mgr = SessionManager()

# Update generate_scheme endpoint
@router.post("/scheme-of-work")
async def generate_scheme(payload: dict = Body(...)):
    if not validate_user_input(payload):
        raise HTTPException(400, detail="Invalid input parameters")
    
    try:
        # Retrieve context from Pinecone
        retrieval_tool = PineconeRetrievalTool()
        result = json.loads(retrieval_tool.run(json.dumps(payload)))
        
        if result.get('status') != 'valid':
            raise HTTPException(400, detail="Failed to retrieve context: " + result.get('message', ''))
        
        context = result.get('context', '')
        
        # Store context in database
        context_id = session_mgr.supabase.store_context(
            payload['subject'],
            payload['grade_level'],
            payload['topic'],
            context
        )
        
        # Generate content with retrieved context
        scheme_content = generator.generate("scheme_of_work", {
            **payload,
            "curriculum_context": context
        })
        
        # Store scheme with context reference
        scheme_id = session_mgr.create_scheme({
            "payload": payload,
            "content": scheme_content,
            "context_id": context_id
        })
        
        return {
            "scheme_of_work_id": scheme_id,
            "context_id": context_id,
            "scheme_of_work_output": scheme_content,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(500, detail=str(e))

# Update generate_lesson_plan endpoint
@router.post("/lesson-plan")
async def generate_lesson_plan(payload: dict = Body(...)):
    scheme_id = payload.get("scheme_of_work_id")
    week = payload.get("week")
    
    if not scheme_id or not session_mgr.get_scheme(scheme_id):
        raise HTTPException(400, detail="Invalid scheme ID")
    
    try:
        # Get scheme data from database
        scheme_data = session_mgr.get_scheme(scheme_id)
        if not scheme_data:
            raise HTTPException(404, detail="Associated scheme not found")
        
        # Retrieve context from scheme
        context_id = scheme_data.get("context_id")
        if not context_id:
            raise HTTPException(400, detail="No context found for scheme")

        # Extract the full scheme content and then the week-specific topic
        scheme_content = scheme_data.get("content", "")
        week_topic = extract_week_topic(scheme_content, week)
        if not week_topic:
            raise HTTPException(400, detail=f"No topic found for week {week}")

        # Extract other subject details from scheme payload
        scheme_payload = scheme_data.get("payload", {})

        # Generate lesson plan content with week-specific topic and constraints
        lesson_content = generator.generate("lesson_plan", {
            "subject": scheme_payload.get("subject", ""),
            "grade_level": scheme_payload.get("grade_level", ""),
            "topic": week_topic,
            "curriculum_context": scheme_content,
            "teaching_constraints": payload.get("limitations", ""),
            "week": week
        })
        
        # Store in database
        lesson_plan_id = session_mgr.create_lesson_plan(scheme_id, {
            "payload": {
                "subject": scheme_payload.get("subject", ""),
                "grade_level": scheme_payload.get("grade_level", ""),
                "topic": week_topic,
                "limitations": payload.get("limitations", ""),
                "week": week
            },
            "content": lesson_content,
            "context_id": context_id
        })
        
        return {
            "scheme_of_work_id": scheme_id,
            "lesson_plan_id": lesson_plan_id,
            "lesson_plan_output": lesson_content,
            "context_id": context_id,
            "week": week,
            "status": "success"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, detail=str(e))

# Update generate_lesson_notes endpoint
@router.post("/lesson-notes")
async def generate_notes(payload: dict = Body(...)):
    required_fields = ["scheme_of_work_id", "lesson_plan_id", "week"]
    if any(field not in payload for field in required_fields):
        raise HTTPException(400, detail="Missing required fields in payload")

    scheme_id = payload["scheme_of_work_id"]
    lesson_plan_id = payload["lesson_plan_id"]
    week = payload["week"]
    
    try:
        # Get database records
        scheme = session_mgr.get_scheme(scheme_id)
        lesson_plan = session_mgr.get_lesson_plan(lesson_plan_id)
        
        if not scheme or not lesson_plan:
            raise HTTPException(404, detail="Associated content not found")

        # Extract context ID from scheme
        context_id = scheme.get("context_id")
        if not context_id:
            raise HTTPException(400, detail="Scheme is missing context ID")

        # Extract week-specific content
        scheme_week_content = extract_week_content(scheme.get("content", ""), week)
        lesson_plan_week_content = extract_week_content(lesson_plan.get("content", ""), week)

        # Generate notes with week-specific content
        notes_content = generator.generate("lesson_notes", {
            "subject": payload.get("subject", scheme.get("payload", {}).get("subject", "")),
            "grade_level": payload.get("grade_level", scheme.get("payload", {}).get("grade_level", "")),
            "topic": payload.get("topic", scheme.get("payload", {}).get("topic", "")),
            "week": week,
            "scheme_context": scheme_week_content,
            "lesson_plan_context": lesson_plan_week_content
        })
        
        # Store in database with context_id
        notes_id = session_mgr.create_lesson_notes(
            scheme_id,
            lesson_plan_id,
            {
                "payload": {
                    "teaching_method": payload.get("teaching_method", ""),
                    "topic": payload.get("topic", ""),
                    "week": week
                },
                "content": notes_content,
                "context_id": context_id  # Add context ID to lesson notes
            }
        )
        
        return {
            "scheme_of_work_id": scheme_id,
            "lesson_plan_id": lesson_plan_id,
            "lesson_notes_id": notes_id,
            "content": notes_content,
            "context_id": context_id,  # Return context ID in response
            "week": week,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(500, detail=f"Generation failed: {str(e)}")