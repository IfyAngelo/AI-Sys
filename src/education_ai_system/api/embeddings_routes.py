from fastapi import APIRouter, UploadFile, File
from src.education_ai_system.services.pinecone_service import VectorizationService
import os

router = APIRouter()

@router.post("/process_pdf")
async def process_pdf(file: UploadFile = File(...)):
    try:
        file_path = f"temp_{file.filename}"
        with open(file_path, "wb") as f:
            f.write(await file.read())
        
        service = VectorizationService()
        service.process_and_store_pdf(file_path)
        
        os.remove(file_path)
        
        return {"status": "success", "message": "PDF processed and stored"}
    except Exception as e:
        return {"status": "error", "message": str(e)}