# src/education_ai_system/utils/session_manager.py
from uuid import uuid4
from datetime import datetime, timedelta

class SessionManager:
    def __init__(self):
        self.schemes = {}
        self.lesson_plans = {}
        self.lesson_notes = {}

    # Scheme Operations
    def create_scheme(self, data: dict) -> str:
        scheme_id = str(uuid4())
        self.schemes[scheme_id] = {
            "created": datetime.now(),
            "data": data,
            "lesson_plans": []
        }
        return scheme_id

    def get_scheme(self, scheme_id: str) -> dict:
        return self.schemes.get(scheme_id)

    # Lesson Plan Operations
    def create_lesson_plan(self, scheme_id: str, data: dict) -> str:
        lesson_plan_id = str(uuid4())
        self.lesson_plans[lesson_plan_id] = {
            "scheme_id": scheme_id,
            "created": datetime.now(),
            "data": data
        }
        if scheme_id in self.schemes:
            self.schemes[scheme_id]["lesson_plans"].append(lesson_plan_id)
        return lesson_plan_id

    def get_lesson_plan(self, lesson_plan_id: str) -> dict:
        return self.lesson_plans.get(lesson_plan_id)

    # Lesson Notes Operations
    def create_lesson_notes(self, scheme_id: str, lesson_plan_id: str, data: dict) -> str:
        notes_id = str(uuid4())
        self.lesson_notes[notes_id] = {
            "scheme_id": scheme_id,
            "lesson_plan_id": lesson_plan_id,
            "created": datetime.now(),
            "data": data
        }
        return notes_id

    def cleanup_old_entries(self, max_age_hours=24):
        now = datetime.now()
        # Clean schemes and their dependencies
        for scheme_id in list(self.schemes.keys()):
            if (now - self.schemes[scheme_id]["created"]) > timedelta(hours=max_age_hours):
                del self.schemes[scheme_id]