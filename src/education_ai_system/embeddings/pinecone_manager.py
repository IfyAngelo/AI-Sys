import os
import torch
from pinecone import Pinecone
from transformers import AutoTokenizer, AutoModel
from dotenv import load_dotenv

load_dotenv()

class PineconeManager:
    def __init__(self):
        self.pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        self.index_name = os.getenv("PINECONE_INDEX", "curriculum-builder")
        self.tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
        self.model = AutoModel.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
        
        # Initialize index
        if self.index_name not in self.pc.list_indexes().names():
            self.pc.create_index(
                name=self.index_name,
                dimension=384,
                metric="cosine"
            )
            
        self.index = self.pc.Index(self.index_name)

    def upsert_content(self, chunks, metadata):
        embeddings = []
        for chunk, meta in zip(chunks, metadata):
            inputs = self.tokenizer(chunk, return_tensors="pt", padding=True, truncation=True)
            with torch.no_grad():
                embedding = self.model(**inputs).last_hidden_state.mean(dim=1).cpu().numpy()
            
            embeddings.append({
                "id": f"chunk-{hash(chunk)}",
                "values": embedding[0].tolist(),
                "metadata": {
                    "subject": meta[0],
                    "grade_level": meta[1],
                    "content": chunk
                }
            })
        
        self.index.upsert(embeddings)