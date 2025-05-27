import yaml
from typing import Dict, Optional
import os
from pathlib import Path

def load_predefined_inputs() -> Dict:
    try:
        config_path = Path(__file__).parent.parent / "config" / "predefined_input.yaml"
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    except Exception as e:
        raise RuntimeError(f"Failed to load predefined inputs: {str(e)}")

def parse_query(query: str) -> Optional[Dict[str, str]]:
    """
    Parses a plain string query into a structured dictionary.
    Args:
        query (str): Plain string query in the format 'subject, grade_level, topic'.
    Returns:
        dict: Parsed query with 'subject', 'grade_level', and 'topic' keys, or None if parsing fails.
    """
    parts = query.split(",")
    if len(parts) != 3:
        return None

    return {
        "subject": parts[0].strip().lower(),
        "grade_level": parts[1].strip().lower(),
        "topic": parts[2].strip().lower()
    }

def validate_user_input(query: Dict[str, str]) -> bool:
    predefined_inputs = load_predefined_inputs()
    print(f"Validating query: {query}")  # Debug log
    query = {key: value.strip().lower() for key, value in query.items()}
    
    print("Available subjects:", [s["name"].lower() for s in predefined_inputs["subjects"]])
    subject = next((s for s in predefined_inputs["subjects"] 
                  if s["name"].strip().lower() == query["subject"]), None)
    if not subject:
        print(f"Subject {query['subject']} not found")
        return False

    print("Available grade levels:", [g["name"].lower() for g in subject["grade_levels"]])
    grade_level = next((g for g in subject["grade_levels"] 
                      if g["name"].strip().lower() == query["grade_level"]), None)
    if not grade_level:
        print(f"Grade level {query['grade_level']} not found")
        return False

    print("Available topics:", [t.lower() for t in grade_level["topics"]])
    return query["topic"] in [t.strip().lower() for t in grade_level["topics"]]

def extract_weeks_from_scheme(scheme_content: str) -> list:
    """Extract weeks from markdown scheme content"""
    weeks = []
    lines = scheme_content.split('\n')
    for line in lines:
        if '|' in line and 'WEEK' in line.upper():
            parts = [p.strip() for p in line.split('|') if p.strip()]
            if len(parts) >= 2 and parts[0].isdigit():
                weeks.append(parts[0])
    return list(set(weeks))  # Return unique weeks

def load_prompt(prompt_name: str) -> str:
    """Load prompt template from YAML files"""
    prompt_path = Path(__file__).parent.parent / "config" / "prompts" / f"{prompt_name}.yaml"
    with open(prompt_path) as f:
        prompt_data = yaml.safe_load(f)
    return prompt_data['system_prompt'] + "\n\n" + prompt_data['user_prompt_template']