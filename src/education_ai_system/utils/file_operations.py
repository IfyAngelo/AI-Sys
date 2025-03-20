# convert_logs_to_docx.py

import os
import json
from docx import Document
from docx.shared import Pt
from pathlib import Path
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT

# BASE_DIR = Path("/Users/libertyelectronics/Desktop/curriculum_builder/CB_Agent")
# LOGS_DIR = BASE_DIR / "logs"
# OUTPUT_DIR = BASE_DIR / "genai_output"
# OUTPUT_DIR.mkdir(exist_ok=True)

def load_inputs():
    """Load the user inputs from JSON file."""
    with open("user_inputs.json", "r") as f:
        inputs = json.load(f)
    return inputs

def convert_md_to_docx(md_path: Path, output_path: Path):
    """Convert markdown content to DOCX with proper formatting"""

    doc = Document()
    
    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Add custom styling
    style = doc.styles["Normal"]
    font = style.font
    font.name = "Calibri"
    font.size = Pt(11)
    
    # Parse markdown content
    for line in content.split("\n"):
        line = line.strip()
        
        if line.startswith("# "):
            heading = doc.add_heading(line[2:], level=1)
            heading.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        elif line.startswith("## "):
            doc.add_heading(line[3:], level=2)
        elif line.startswith("### "):
            doc.add_heading(line[4:], level=3)
        elif line.startswith("- **"):
            # Bold list items
            parts = line.split(":", 1)
            if len(parts) > 1:
                p = doc.add_paragraph()
                p.add_run(parts[0].strip("- ")).bold = True
                p.add_run(": " + parts[1].strip())
        elif "|" in line:
            # Tables
            cells = [c.strip() for c in line.split("|") if c.strip()]
            if cells:
                table = doc.add_table(rows=1, cols=len(cells))
                table.style = "Table Grid"
                hdr_cells = table.rows[0].cells
                for i, cell in enumerate(cells):
                    hdr_cells[i].text = cell
        else:
            doc.add_paragraph(line)
    
    doc.save(output_path)