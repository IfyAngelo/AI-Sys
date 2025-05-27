# src/education_ai_system/utils/session_manager.py
from datetime import datetime
from .supabase_manager import SupabaseManager

class SessionManager:
    def __init__(self):
        self.supabase = SupabaseManager()
        self.current_scheme_id = None
        self.current_lesson_plan_id = None
        self.current_lesson_notes_id = None

    # Scheme Operations
    def create_scheme(self, data: dict) -> str:
        scheme_id = self.supabase.create_scheme(data)
        self.current_scheme_id = scheme_id
        return scheme_id

    def get_scheme(self, scheme_id: str) -> dict:
        return self.supabase.get_scheme(scheme_id)

    # Lesson Plan Operations
    def create_lesson_plan(self, scheme_id: str, data: dict) -> str:
        lesson_plan_id = self.supabase.create_lesson_plan(scheme_id, data)
        self.current_lesson_plan_id = lesson_plan_id
        return lesson_plan_id

    def get_lesson_plan(self, lesson_plan_id: str) -> dict:
        return self.supabase.get_lesson_plan(lesson_plan_id)

    # Lesson Notes Operations
    def create_lesson_notes(self, scheme_id: str, lesson_plan_id: str, data: dict) -> str:
        notes_id = self.supabase.create_lesson_notes(scheme_id, lesson_plan_id, data)
        self.current_lesson_notes_id = notes_id
        return notes_id

    def get_lesson_notes(self, notes_id: str) -> dict:
        return self.supabase.get_lesson_notes(notes_id)