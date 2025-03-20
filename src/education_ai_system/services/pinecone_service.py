from src.education_ai_system.embeddings.pinecone_manager import PineconeManager
from src.education_ai_system.data_processing import (
    pdf_extractor,
    text_chunker,
    metadata_extractor
)

class VectorizationService:
    def __init__(self):
        self.pinecone_manager = PineconeManager()

    # Remove @staticmethod decorator
    def process_and_store_pdf(self, pdf_path: str):  # Add 'self' parameter
        text, _ = pdf_extractor.extract_text_and_tables(pdf_path)
        chunks = text_chunker.split_text_into_chunks(text)
        metadata = [metadata_extractor.extract_metadata(chunk) for chunk in chunks]
        self.pinecone_manager.upsert_content(chunks, metadata)