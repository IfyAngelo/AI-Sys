# src/project_name/data_processing/pdf_extractor.py

import pdfplumber
import pandas as pd

def extract_text_and_tables(pdf_path):
    extracted_text = ""
    tables = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            extracted_text += page.extract_text() or ""
            for table in page.extract_tables():
                tables.append(pd.DataFrame(table[1:], columns=table[0]))
    return extracted_text, tables