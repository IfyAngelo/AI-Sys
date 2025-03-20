# src/project_name/data_processing/metadata_extractor.py

import re

def extract_metadata(chunk):
    subject = re.search(r"(Mathematics|Civic Education|Science|English)", chunk, re.IGNORECASE)
    grade_level = re.search(r"(Primary [One|Two|Three|Four|Five|Six])", chunk, re.IGNORECASE)
    return subject.group(0) if subject else "Unknown Subject", grade_level.group(0) if grade_level else "Unknown Grade Level"