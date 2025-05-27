from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from src.education_ai_system.utils.validators import load_prompt
import yaml

class ContentGenerator:
    def __init__(self):
        # self.llm = ChatOpenAI(model_name="gpt-4o", temperature=0.7)
        self.llm = ChatGroq(temperature=0.5,
                            model_name="llama-3.3-70b-versatile",
                            max_tokens=4096
                            )
        self.prompts = {
            "lesson_plan": load_prompt("lesson_plan"),
            "scheme_of_work": load_prompt("scheme_of_work"),
            "lesson_notes": load_prompt("lesson_notes")
        }

    def generate(self, content_type: str, context: dict):
        prompt = self._build_prompt(content_type, context)
        try:
            return self.llm.invoke(prompt).content
        except Exception as e:
            return f"Error generating content: {str(e)}"

    def _build_prompt(self, content_type: str, context: dict):
        template = self.prompts[content_type]
        
        # For lesson notes specifically
        if content_type == "lesson_notes":
            return template.format(
                subject=context['subject'],
                grade_level=context['grade_level'],
                topic=context['topic'],
                scheme_context=context.get('scheme_context', ''),
                lesson_plan_context=context.get('lesson_plan_context', '')
            )
        elif content_type == "lesson_plan":
            return template.format(
                subject=context['subject'],
                grade_level=context['grade_level'],
                topic=context['topic'],
                curriculum_context=context.get('curriculum_context', ''),
                teaching_constraints=context.get('teaching_constraints', 'No constraints provided')
            )
        # Other content types remain the same
        return template.format(
            subject=context['subject'],
            grade_level=context['grade_level'],
            topic=context['topic'],
            curriculum_context=context.get('curriculum', '')
        )