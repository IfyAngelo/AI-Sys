# src/education_ai_system/utils/supabase_manager.py
import os
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime
from typing import Dict, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SupabaseManager")

load_dotenv()

class SupabaseManager:
    def __init__(self):
        logger.info("Initializing Supabase client")
        try:
            self.client: Client = create_client(
                os.getenv("SUPABASE_URL"),
                os.getenv("SUPABASE_KEY")
            )
            logger.info("✅ Supabase client initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Supabase client: {str(e)}")
            raise
    
    # CONTEXT OPERATIONS
    def store_context(self, subject: str, grade_level: str, topic: str, context: str) -> str:
        """Stores curriculum context in the database."""
        logger.info(f"Storing context for {subject} ({grade_level}) - {topic}")
        try:
            result = self.client.table('curriculum_context').insert({
                "subject": subject,
                "grade_level": grade_level,
                "topic": topic,
                "context": context
            }).execute()
            
            if result.data:
                context_id = result.data[0]['id']
                logger.info(f"✅ Context stored successfully. ID: {context_id}")
                return context_id
            logger.error("❌ Context storage failed: No data returned")
            return None
        except Exception as e:
            logger.error(f"❌ Context storage error: {str(e)}")
            return None

    def get_context_by_id(self, context_id: str) -> dict:
        logger.info(f"Fetching context with ID: {context_id}")
        try:
            result = self.client.table('curriculum_context').select("*").eq("id", context_id).execute()
            if result.data:
                context_data = result.data[0]
                logger.info(f"✅ Found context: ID={context_data['id']}")
                
                # NEW: Ensure all required fields exist
                context_data.setdefault('subject', 'Unknown')
                context_data.setdefault('grade_level', 'Unknown')
                context_data.setdefault('topic', 'Unknown')
                context_data.setdefault('context', 'No context available')
                
                return context_data
            logger.warning("⚠️ Context not found")
            return None
        except Exception as e:
            logger.error(f"❌ Context fetch error: {str(e)}")
            return None

    # SCHEME OPERATIONS
    def create_scheme(self, data: dict) -> str:
        logger.info("Creating new scheme")
        try:
            # Build scheme data with context_id if available
            scheme_data = {
                "payload": data.get("payload"),
                "content": data.get("content"),
                "created_at": datetime.now().isoformat()
            }
            
            # Add context_id if provided
            if "context_id" in data:
                scheme_data["context_id"] = data["context_id"]
            
            result = self.client.table('schemes').insert(scheme_data).execute()
            
            if result.data:
                scheme_id = result.data[0]['id']
                logger.info(f"✅ Scheme created. ID: {scheme_id}")
                return scheme_id
            logger.error("❌ Scheme creation failed: No data returned")
            return None
        except Exception as e:
            logger.error(f"❌ Scheme creation error: {str(e)}")
            return None

    def get_scheme(self, scheme_id: str) -> dict:
        logger.info(f"Fetching scheme with ID: {scheme_id}")
        try:
            result = self.client.table('schemes').select("*").eq("id", scheme_id).execute()
            if result.data:
                logger.info(f"✅ Found scheme: ID={result.data[0]['id']}")
                return result.data[0]
            logger.warning("⚠️ Scheme not found")
            return None
        except Exception as e:
            logger.error(f"❌ Scheme fetch error: {str(e)}")
            return None

    def get_scheme_by_context(self, context_id: str) -> dict:
        logger.info(f"Fetching scheme by context ID: {context_id}")
        try:
            result = self.client.table('schemes').select("*").eq("context_id", context_id).execute()
            if result.data:
                scheme_id = result.data[0]['id']
                logger.info(f"✅ Found scheme: ID={scheme_id} for context {context_id}")
                return result.data[0]
            logger.warning("⚠️ Scheme not found for given context")
            return None
        except Exception as e:
            logger.error(f"❌ Scheme by context fetch error: {str(e)}")
            return None

    # LESSON PLAN OPERATIONS - UPDATED WITH WEEK FIELD
    def create_lesson_plan(self, scheme_id: str, data: dict) -> str:
        logger.info(f"Creating lesson plan for scheme ID: {scheme_id}")
        try:
            if not scheme_id:
                raise ValueError("Scheme ID is required")
            
            required_fields = ["payload", "content"]
            if not all(field in data for field in required_fields):
                raise ValueError("Missing required fields in lesson plan data")
            
            # Prepare the data to be inserted
            insert_data = {
                "scheme_id": scheme_id,
                "payload": data["payload"],
                "content": data["content"]
            }
            
            # Add week only if column exists
            if hasattr(self, '_week_column_exists') and self._week_column_exists:
                insert_data["week"] = data.get("week", "1")
            
            # Check if "context_id" is in the data and include it
            if "context_id" in data:
                insert_data["context_id"] = data["context_id"]
            
            # Insert the data into the table
            response = self.client.table('lesson_plans').insert(insert_data).execute()
            
            if response.data:
                plan_id = response.data[0]['id']
                logger.info(f"✅ Lesson plan created. ID: {plan_id}")
                return plan_id
            logger.error("❌ Lesson plan creation failed: No data returned")
            return None
        except Exception as e:
            # Handle missing week column specifically
            if "Could not find the 'week' column" in str(e):
                logger.warning("⚠️ 'week' column not found. Creating without week information")
                self._week_column_exists = False
                return self.create_lesson_plan(scheme_id, data)  # Retry without week
            logger.error(f"❌ Lesson plan creation error: {str(e)}")
            return None

    def get_lesson_plan(self, lesson_plan_id: str) -> dict:
        logger.info(f"Fetching lesson plan with ID: {lesson_plan_id}")
        try:
            result = self.client.table('lesson_plans').select("*").eq("id", lesson_plan_id).execute()
            if result.data:
                logger.info(f"✅ Found lesson plan: ID={result.data[0]['id']}")
                return result.data[0]
            logger.warning("⚠️ Lesson plan not found")
            return None
        except Exception as e:
            logger.error(f"❌ Lesson plan fetch error: {str(e)}")
            return None

    def get_lesson_plan_by_context(self, context_id: str) -> dict:
        logger.info(f"Fetching lesson plan by context ID: {context_id}")
        try:
            result = self.client.table('lesson_plans').select("*").eq("context_id", context_id).execute()
            if result.data:
                plan_id = result.data[0]['id']
                logger.info(f"✅ Found lesson plan: ID={plan_id} for context {context_id}")
                return result.data[0]
            logger.warning("⚠️ Lesson plan not found for given context")
            return None
        except Exception as e:
            logger.error(f"❌ Lesson plan by context fetch error: {str(e)}")
            return None

    # LESSON NOTES OPERATIONS - UPDATED WITH WEEK FIELD
    def create_lesson_notes(self, scheme_id: str, lesson_plan_id: str, data: dict) -> str:
        logger.info(f"Creating lesson notes for scheme: {scheme_id}, plan: {lesson_plan_id}")
        try:
            # Check if scheme_id and lesson_plan_id are provided
            if not all([scheme_id, lesson_plan_id]):
                raise ValueError("Both scheme ID and lesson plan ID are required")
            
            # Ensure required fields are present in data
            required_fields = ["payload", "content"]
            if not all(field in data for field in required_fields):
                raise ValueError("Missing required fields in lesson notes data")
            
            # Build the data to be inserted, including context_id if provided
            insert_data = {
                "scheme_id": scheme_id,
                "lesson_plan_id": lesson_plan_id,
                "payload": data["payload"],
                "content": data["content"],
                "week": data.get("week", "1")  # Add week field with default
            }
            
            # Add context_id if provided
            if "context_id" in data:
                insert_data["context_id"] = data["context_id"]
            
            # Insert the lesson notes into the table
            response = self.client.table('lesson_notes').insert(insert_data).execute()
            
            if response.data:
                notes_id = response.data[0]['id']
                logger.info(f"✅ Lesson notes created. ID: {notes_id}")
                return notes_id
            logger.error("❌ Lesson notes creation failed: No data returned")
            return None
        except Exception as e:
            logger.error(f"❌ Lesson notes creation error: {str(e)}")
            return None

    def get_lesson_notes(self, notes_id: str) -> dict:
        logger.info(f"Fetching lesson notes with ID: {notes_id}")
        try:
            result = self.client.table('lesson_notes').select("*").eq("id", notes_id).execute()
            if result.data:
                logger.info(f"✅ Found lesson notes: ID={result.data[0]['id']}")
                return result.data[0]
            logger.warning("⚠️ Lesson notes not found")
            return None
        except Exception as e:
            logger.error(f"❌ Lesson notes fetch error: {str(e)}")
            return None

    def get_lesson_notes_by_context(self, context_id: str) -> dict:
        logger.info(f"Fetching lesson notes by context ID: {context_id}")
        try:
            result = self.client.table('lesson_notes').select("*").eq("context_id", context_id).execute()
            if result.data:
                notes_id = result.data[0]['id']
                logger.info(f"✅ Found lesson notes: ID={notes_id} for context {context_id}")
                return result.data[0]
            logger.warning("⚠️ Lesson notes not found for given context")
            return None
        except Exception as e:
            logger.error(f"❌ Lesson notes by context fetch error: {str(e)}")
            return None