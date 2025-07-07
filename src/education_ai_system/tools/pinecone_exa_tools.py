# src/education_ai_system/tools/pinecone_exa_tools.py

from langchain.tools import BaseTool
import os
import json
import torch
from transformers import AutoTokenizer, AutoModel
from pydantic import Field, ConfigDict
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv
import pinecone
from src.education_ai_system.utils.validators import validate_user_input, load_predefined_inputs

# Load environment variables
load_dotenv()

# Initialize tokenizer and model for embeddings
tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

class PineconeRetrievalTool(BaseTool):
    """Tool to retrieve relevant context from Pinecone vector database based on user query."""
    index: Optional[Any] = Field(default=None)  # Simplified type hint
    predefined_inputs: Dict = Field(default_factory=load_predefined_inputs)
    pc: Optional[Any] = Field(default=None)  # Pinecone client field
    stored_context: Optional[str] = None  # Store context for future use
    
    # Updated Pydantic config (v2 style)
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, **kwargs):
        # Initialize the tool FIRST
        name = "Pinecone Retrieval Tool"
        description = (
            "Fetches context from Pinecone. Accepts JSON input with keys: "
            "'subject', 'grade_level', 'topic'"
        )
        super().__init__(name=name, description=description, **kwargs)

        # Initialize Pinecone client AFTER super()
        api_key = os.getenv("PINECONE_API_KEY")
        index_name = os.getenv("PINECONE_INDEX_NAME", "ai-teach")
        
        if not api_key:
            raise ValueError("Error: Pinecone API key is missing. Check your environment variables.")

        self.pc = pinecone.Pinecone(api_key=api_key)

        # Initialize Pinecone index
        try:
            # Use Pinecone instance to list and create index if needed
            available_indexes = self.pc.list_indexes().names()
            if index_name not in available_indexes:
                print(f"Index '{index_name}' does not exist. Creating it now...")
                spec = pinecone.ServerlessSpec(cloud="aws", region="us-west-2")
                self.pc.create_index(
                    name=index_name,
                    dimension=384,
                    metric="cosine",
                    spec=spec
                )
                print(f"Index '{index_name}' created successfully.")
            else:
                print(f"Index '{index_name}' found.")

            self.index = self.pc.Index(index_name)
            print(f"Successfully connected to Pinecone index: {index_name}")
        except Exception as e:
            print(f"Error initializing Pinecone index '{index_name}': {e}")
            self.index = None

    def _parse_query(self, query: str) -> Optional[Dict[str, str]]:
        """Parses a plain string query into a structured dictionary"""
        parts = query.split(",")
        if len(parts) != 3:
            return None
        return {
            "subject": parts[0].strip().lower(),
            "grade_level": parts[1].strip().lower(),
            "topic": parts[2].strip().lower()
        }

    def _validate_and_retrieve(self, query: Dict[str, str], num_results: int = 3) -> Dict:
        """Validates the query and retrieves context from Pinecone"""
        # Validate user input
        if not validate_user_input(query):
            return {
                "status": "invalid",
                "message": "Invalid query. Ensure it matches the format and predefined inputs."
            }

        # Generate query text for embedding
        user_query_text = f"{query['subject']} {query['grade_level']} {query['topic']}"
        query_vector = self._get_query_embedding(user_query_text)

        # Query Pinecone
        try:
            if not self.index:
                raise ValueError("Pinecone index is not initialized.")
                
            # Updated query format for new SDK
            response = self.index.query(
                vector=query_vector,
                top_k=num_results,
                include_metadata=True
            )

            matches = response.get("matches", [])

            if not matches:
                return {"status": "invalid", "message": "No relevant data found.", "alternatives": []}

            # Build context from top matches (Extract relevant data from ScoredVector objects)
            context = "\n\n".join([
                match["metadata"].get("content", "")  # Extract content from metadata
                for match in matches
            ])
            
            # Process matches for alternatives (Extract relevant data from ScoredVector objects)
            alternatives = [
                {
                    "subject": match["metadata"].get("subject", "Unknown"),
                    "grade_level": match["metadata"].get("grade_level", "Unknown"),
                    "topic": match["metadata"].get("text_chunk", "").split(".")[0]  # Extract topic from text_chunk
                }
                for match in matches
            ]

            # Store context for future use (e.g., for evaluation)
            self.stored_context = context  # Store the context for later use

            # Prepare matches in a serializable format (without ScoredVector object)
            serializable_matches = [
                {
                    "id": match["id"],
                    "score": match["score"],  # Extract the score
                    "metadata": match["metadata"]  # Extract metadata
                }
                for match in matches
            ]

            return {
                "status": "valid",
                "context": context,  # The actual retrieved context
                "matches": serializable_matches,  # Serialized matches for JSON compatibility
                "alternatives": alternatives
            }

        except Exception as e:
            return {"status": "error", "message": f"Error querying Pinecone: {e}"}

    def _run(self, query: str) -> str:
        """Runs the tool with JSON input"""
        try:
            # Parse the JSON input directly
            parsed_query = json.loads(query)
            # Perform validation and retrieval
            result = self._validate_and_retrieve(parsed_query)
            return json.dumps(result, indent=2)
        except json.JSONDecodeError:
            return json.dumps({
                "status": "error",
                "message": "Query must be JSON with keys: subject, grade_level, topic"
            })
        except Exception as e:
            return json.dumps({"status": "error", "message": f"Unexpected error: {str(e)}"})

    def _get_query_embedding(self, text: str) -> List[float]:
        """Generates embeddings for a query text"""
        inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
        with torch.no_grad():
            query_embedding = model(**inputs).last_hidden_state.mean(dim=1).cpu().numpy().squeeze()
        return query_embedding.tolist()

# Rebuild the model to resolve Pydantic's forward references
PineconeRetrievalTool.model_rebuild()
