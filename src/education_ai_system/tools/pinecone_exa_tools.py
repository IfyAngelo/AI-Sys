# src/education_ai_system/tools/pinecone_exa_tools.py

import os
import json
import torch
from transformers import AutoTokenizer, AutoModel
from pydantic import Field
from typing import List, Optional, Dict
from dotenv import load_dotenv
from exa_py import Exa
import pinecone
from pinecone import Pinecone, ServerlessSpec
from src.education_ai_system.utils.validators import validate_user_input, load_predefined_inputs

# Load environment variables
load_dotenv()

# Initialize Pinecone client and embedding model
api_key = os.getenv("PINECONE_API_KEY")
index_name = os.getenv("PINECONE_INDEX_NAME", "ai-teach")

if not api_key:
    raise ValueError("Error: Pinecone API key is missing. Check your environment variables.")

# Initialize Pinecone client
pc = Pinecone(api_key=api_key)

# Initialize tokenizer and model for embeddings
tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

class PineconeRetrievalTool(BaseTool):
    """Tool to retrieve relevant context from Pinecone vector database based on user query."""
    index: Optional[pinecone.Index] = Field(default=None)
    predefined_inputs: Dict = Field(default_factory=load_predefined_inputs)

    class Config:
        arbitrary_types_allowed = True  # Allow arbitrary types like Pinecone Index

    def __init__(self):
        name = "Pinecone Retrieval Tool"
        description = (
            "Fetches context from the Pinecone vector database based on a user query. "
            "Accepts a plain string query in the format 'subject, grade_level, topic', parses it internally, "
            "and validates the query against predefined inputs or available database records."
        )
        super().__init__(name=name, description=description)

        # Initialize Pinecone index
        try:
            available_indexes = pc.list_indexes().names()
            if index_name not in available_indexes:
                print(f"Index '{index_name}' does not exist. Creating it now...")
                spec = ServerlessSpec(cloud="aws", region="us-west-2")
                pc.create_index(
                    name=index_name,
                    dimension=384,
                    metric="cosine",
                    spec=spec
                )
                print(f"Index '{index_name}' created successfully.")
            else:
                print(f"Index '{index_name}' found.")

            self.index = pc.Index(index_name)
            print(f"Successfully connected to Pinecone index: {index_name}")
        except Exception as e:
            print(f"Error initializing Pinecone index '{index_name}': {e}")
            self.index = None

    def _parse_query(self, query: str) -> Optional[Dict[str, str]]:
        """
        Parses a plain string query into a structured dictionary with keys 'subject', 'grade_level', 'topic'.
        Args:
            query (str): Plain string query in the format 'subject, grade_level, topic'.
        Returns:
            dict: Parsed query with 'subject', 'grade_level', and 'topic', or None if parsing fails.
        """
        parts = query.split(",")
        if len(parts) != 3:
            return None
        return {
            "subject": parts[0].strip().lower(),
            "grade_level": parts[1].strip().lower(),
            "topic": parts[2].strip().lower()
        }

    def _validate_and_retrieve(self, query: Dict[str, str], num_results: int = 5) -> Dict:
        """
        Validates the query using predefined inputs and retrieves context from Pinecone.
        Args:
            query (dict): User input query dictionary with 'subject', 'grade_level', and 'topic'.
            num_results (int): Number of top matches to retrieve.
        Returns:
            dict: Validation and retrieval results.
        """
        # Validate user input
        if not validate_user_input(query, self.predefined_inputs):
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
            response = self.index.query(vector=query_vector, top_k=num_results, include_metadata=True)
            matches = response.get("matches", [])

            if not matches:
                return {"status": "invalid", "message": "No relevant data found.", "alternatives": []}

            # Process matches
            alternatives = [
                {
                    "subject": match["metadata"].get("subject", "Unknown"),
                    "grade_level": match["metadata"].get("grade_level", "Unknown"),
                    "topic": match["metadata"].get("text_chunk", "").split(".")[0]  # Extract topic from metadata
                }
                for match in matches
            ]

            return {"status": "valid", "metadata": matches[0]["metadata"], "alternatives": alternatives}

        except Exception as e:
            return {"status": "error", "message": f"Error querying Pinecone: {e}"}

    def _run(self, query: str) -> str:
        """
        Runs the tool with the provided plain string query.
        Args:
            query (str): The user query as a plain string in the format 'subject, grade_level, topic'.
        Returns:
            str: JSON string with results or error message.
        """
        try:
            # Parse and validate the query
            parsed_query = self._parse_query(query)
            if not parsed_query:
                return json.dumps({"status": "error", "message": "Query must be in the format 'subject, grade_level, topic'."})

            # Perform validation and retrieval
            result = self._validate_and_retrieve(parsed_query)
            return json.dumps(result, indent=2)

        except Exception as e:
            return json.dumps({"status": "error", "message": f"Unexpected error: {str(e)}"})

    def _get_query_embedding(self, text: str) -> List[float]:
        """Generates embeddings for a query text."""
        inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
        with torch.no_grad():
            query_embedding = model(**inputs).last_hidden_state.mean(dim=1).cpu().numpy().squeeze()
        return query_embedding.tolist()


class ExaSearchContextualTool(BaseTool):
    """Tool to perform an Exa web search using contextual information from Pinecone retrieval."""

    def __init__(self):
        # Initialize BaseTool with name and description
        name = "ExaSearchContextualTool"
        description = (
            "Uses the Exa API to perform a web search based on contextual information from Pinecone. "
            "Finds the most recent and relevant online materials aligned with the given context."
        )
        super().__init__(name=name, description=description)

    def _run(self, search_query: str) -> str:
        # Initialize the Exa API client with the provided key
        exa = Exa(os.getenv("EXASEARCH_API_KEY"))

        # Execute a search using the Exa API
        search_response = exa.search_and_contents(
            search_query,
            use_autoprompt=True,
            text={"include_html_tags": False, "max_characters": 8000},
        )
        
        # Process search results and safely access attributes
        try:
            # Assuming `results` is a list attribute in `search_response`
            results = [
                {
                    "title": getattr(result, "title", "No title available"),
                    "link": getattr(result, "url", "No URL available"),
                    "snippet": getattr(result, "snippet", "No snippet available"),
                }
                for result in getattr(search_response, "results", [])
            ]
        except AttributeError as e:
            return f"Error processing results: {e}"

        # Return the results as a JSON string for consistency
        return json.dumps(results, indent=2)
