"""
Qdrant vector store client for managing embeddings and collections.
"""

import pandas as pd
from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance, PointStruct
import numpy as np
from typing import Optional


class VectorStoreClient:
    """Client for managing vector store operations with Qdrant."""
    
    def __init__(self, host: str = "localhost", port: int = 6333):
        self.client = QdrantClient(host=host, port=port)
    
    def upload_embeddings_with_payloads(
        self, 
        embeddings: np.ndarray, 
        csv_path: str, 
        collection_name: str = "stocks"
    ) -> None:
        """
        Upload embeddings with metadata payloads to Qdrant.
        
        Args:
            embeddings: Numpy array of embeddings
            csv_path: Path to CSV file with metadata
            collection_name: Name of the collection to store in
        """
        df = pd.read_csv(csv_path)
        dim = embeddings.shape[1]

        # Create collection if it doesn't exist
        if not self.client.collection_exists(collection_name):
            print(f"Collection {collection_name} does not exist. Creating...")
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
            )

        # Prepare points with payloads
        points = []
        for i in range(len(embeddings)):
            payload = {
                "title": df.iloc[i]["title"],
                "selftext": df.iloc[i].get("selftext", ""),
                "score": int(df.iloc[i].get("score", 0)),
                "source": "Reddit"
            }
            points.append(
                PointStruct(id=i, vector=embeddings[i].tolist(), payload=payload)
            )

        # Upload to collection
        self.client.upsert(collection_name=collection_name, points=points)
        print(f"✅ Uploaded: {len(points)} vectors → Collection '{collection_name}'")


# Global client instance
_default_client = VectorStoreClient()


def upload_embeddings_with_payloads(
    embeddings: np.ndarray, 
    csv_path: str, 
    collection_name: str = "stocks"
) -> None:
    """
    Convenience function to upload embeddings using the default client.
    
    Args:
        embeddings: Numpy array of embeddings
        csv_path: Path to CSV file with metadata
        collection_name: Name of the collection to store in
    """
    _default_client.upload_embeddings_with_payloads(embeddings, csv_path, collection_name)
