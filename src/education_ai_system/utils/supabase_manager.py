# src/education_ai_system/utils/supabase_manager.py
import os
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

class SupabaseManager:
    def __init__(self):
        self.client: Client = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_KEY")
        )
    
    # SCHEME OPERATIONS
    def create_scheme(self, data: dict) -> str:
        result = self.client.table('schemes').insert({
            "payload": data.get("payload"),
            "content": data.get("content"),
            "created_at": datetime.now().isoformat()
        }).execute()
        return result.data[0]['id']

    def get_scheme(self, scheme_id: str) -> dict:
        result = self.client.table('schemes').select("*").eq("id", scheme_id).execute()
        return result.data[0] if result.data else None

    # LESSON PLAN OPERATIONS
    def create_lesson_plan(self, scheme_id: str, data: dict) -> str:
            if not scheme_id:
                raise ValueError("Scheme ID is required")
                
            required_fields = ["payload", "content"]
            if not all(field in data for field in required_fields):
                raise ValueError("Missing required fields in lesson plan data")
                
            response = self.client.table('lesson_plans').insert({
                "scheme_id": scheme_id,
                "payload": data["payload"],
                "content": data["content"]
            }).execute()
            return response.data[0]['id']

    def get_lesson_plan(self, lesson_plan_id: str) -> dict:
        result = self.client.table('lesson_plans').select("*").eq("id", lesson_plan_id).execute()
        return result.data[0] if result.data else None

    # LESSON NOTES OPERATIONS
    def create_lesson_notes(self, scheme_id: str, lesson_plan_id: str, data: dict) -> str:
        if not all([scheme_id, lesson_plan_id]):
            raise ValueError("Both scheme ID and lesson plan ID are required")
            
        required_fields = ["payload", "content"]
        if not all(field in data for field in required_fields):
            raise ValueError("Missing required fields in lesson notes data")
            
        response = self.client.table('lesson_notes').insert({
            "scheme_id": scheme_id,
            "lesson_plan_id": lesson_plan_id,
            "payload": data["payload"],
            "content": data["content"]
        }).execute()
        return response.data[0]['id']

    def get_lesson_notes(self, notes_id: str) -> dict:
        result = self.client.table('lesson_notes').select("*").eq("id", notes_id).execute()
        return result.data[0] if result.data else None