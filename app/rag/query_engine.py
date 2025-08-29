"""
RAG query engine for searching similar posts and retrieving context.
"""

from qdrant_client import QdrantClient
from qdrant_client.http.models import Filter, FieldCondition, MatchValue
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict

from app.embedding.embed_posts import EMBEDDING_MODEL
from app.llm.generator import generate_answer_from_context


class RAGQueryEngine:
    """RAG query engine for stock sentiment analysis."""
    
    def __init__(self, host: str = "localhost", port: int = 6333):
        self.qdrant_client = QdrantClient(host=host, port=port)
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
    
    def search_similar_posts(
        self, 
        query: str, 
        collection_name: str = "tesla_2025q2", 
        top_k: int = 5
    ) -> List[Dict]:
        """
        Search for similar posts in the vector store.
        
        Args:
            query: Search query
            collection_name: Name of the collection to search in
            top_k: Number of similar posts to return
            
        Returns:
            List of similar posts with payloads
        """
        # Convert query to embedding
        embedding = self.embedding_model.encode(query).tolist()

        # Search for similar entries in Qdrant
        search_result = self.qdrant_client.query_points(
            collection_name=collection_name,
            query=embedding,
            limit=top_k
        )

        return [hit.payload for hit in search_result.points]
    
    def generate_answer_from_context(
        self, 
        query: str, 
        context_posts: List[Dict]
    ) -> str:
        """
        Generate an answer using the LLM based on context posts.
        
        Args:
            query: User's question
            context_posts: Relevant context posts
            
        Returns:
            Generated answer
        """
        return generate_answer_from_context(query, context_posts)


# Global query engine instance
_default_engine = RAGQueryEngine()


def search_similar_posts(
    query: str, 
    collection_name: str = "tesla_2025q2", 
    top_k: int = 5
) -> List[Dict]:
    """
    Convenience function to search similar posts using the default engine.
    
    Args:
        query: Search query
        collection_name: Name of the collection to search in
        top_k: Number of similar posts to return
        
    Returns:
        List of similar posts with payloads
    """
    return _default_engine.search_similar_posts(query, collection_name, top_k)


def generate_answer_from_context(query: str, context_posts: List[Dict]) -> str:
    """
    Convenience function to generate answers using the default engine.
    
    Args:
        query: User's question
        context_posts: Relevant context posts
        
    Returns:
        Generated answer
    """
    return _default_engine.generate_answer_from_context(query, context_posts)
