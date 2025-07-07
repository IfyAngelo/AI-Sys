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
    """Robust week extraction from scheme content"""
    weeks = []
    
    # Method 1: Table-based extraction
    for line in scheme_content.split('\n'):
        if '|' in line:
            parts = [p.strip() for p in line.split('|') if p.strip()]
            if parts and parts[0].isdigit():
                weeks.append(parts[0])
    
    # Method 2: Pattern-based extraction
    if not weeks:
        import re
        week_pattern = r'\bweek\s*(\d+)\b|\b(\d+)\b'
        matches = re.findall(week_pattern, scheme_content, re.IGNORECASE)
        for match in matches:
            week_num = match[0] or match[1]  # Handle different capture groups
            if week_num not in weeks:
                weeks.append(week_num)
    
    # Ensure we have at least week 1
    if not weeks:
        weeks = ["1"]
    
    return sorted(weeks, key=int)

def extract_week_topic(scheme_content: str, week: str) -> str:
    """Extract topic for a specific week from scheme content with better parsing"""
    # Normalize week format by removing any non-digit characters
    clean_week = ''.join(filter(str.isdigit, week))
    
    # First try: table format parsing
    for line in scheme_content.split('\n'):
        if f"| {clean_week} |" in line or f"|{clean_week}|" in line:
            parts = [p.strip() for p in line.split('|') if p.strip()]
            if len(parts) >= 3:
                return parts[1]  # Main Topic column
    
    # Second try: flexible pattern matching
    for line in scheme_content.split('\n'):
        if clean_week in line:
            # Look for topic after the week number
            parts = line.split(clean_week, 1)
            if len(parts) > 1:
                # Extract text after week number
                topic_part = parts[1].strip()
                # Remove any trailing table characters
                if '|' in topic_part:
                    topic_part = topic_part.split('|')[0]
                if topic_part:
                    return topic_part
    
    # Fallback: return the main topic if week-specific not found
    if "TOPIC:" in scheme_content:
        topic_line = [line for line in scheme_content.split('\n') if "TOPIC:" in line]
        if topic_line:
            return topic_line[0].split("TOPIC:")[1].strip()
    
    # Final fallback
    return "General Topic"

def extract_week_content(content: str, week: str) -> str:
    """Extract content for a specific week from markdown content"""
    week_header = f"WEEK {week}"
    start_index = content.find(week_header)
    if start_index == -1:
        return "" 
    
    end_index = content.find("WEEK ", start_index + len(week_header))
    if end_index == -1:
        return content[start_index:]  # Return remaining content if last week
    
    return content[start_index:end_index]

def load_prompt(prompt_name: str) -> str:
    """Load prompt template from YAML files"""
    prompt_path = Path(__file__).parent.parent / "config" / "prompts" / f"{prompt_name}.yaml"
    with open(prompt_path) as f:
        prompt_data = yaml.safe_load(f)
    return prompt_data['system_prompt'] + "\n\n" + prompt_data['user_prompt_template']