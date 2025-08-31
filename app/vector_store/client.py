"""
Qdrant vector store client for managing embeddings and collections.
"""

import pandas as pd
from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance, PointStruct
import numpy as np
from typing import Optional, List, Dict, Tuple
from pathlib import Path
import os


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
                "url": df.iloc[i].get("url", ""),
                "created_utc": df.iloc[i].get("created_utc", 0),
                "num_comments": df.iloc[i].get("num_comments", 0),
                "source": "Reddit",
                "dataset_name": collection_name
            }
            points.append(
                PointStruct(id=i, vector=embeddings[i].tolist(), payload=payload)
            )

        # Upload to collection
        self.client.upsert(collection_name=collection_name, points=points)
        print(f"✅ Uploaded: {len(points)} vectors → Collection '{collection_name}'")
    
    def export_collection_to_csv(
        self, 
        collection_name: str, 
        output_path: Optional[str] = None
    ) -> str:
        """
        Export a collection's data to CSV format.
        
        Args:
            collection_name: Name of the collection to export
            output_path: Path to save CSV file (optional)
            
        Returns:
            Path to the exported CSV file
        """
        if not self.client.collection_exists(collection_name):
            raise ValueError(f"Collection '{collection_name}' does not exist")
        
        # Get all points from collection
        points = self.client.scroll(
            collection_name=collection_name,
            limit=10000,  # Adjust based on your needs
            with_payload=True,
            with_vectors=False  # Don't include vectors in CSV
        )[0]
        
        if not points:
            print(f"⚠️ Collection '{collection_name}' is empty")
            return ""
        
        # Convert to DataFrame
        data = []
        for point in points:
            payload = point.payload
            data.append({
                "title": payload.get("title", ""),
                "selftext": payload.get("selftext", ""),
                "score": payload.get("score", 0),
                "url": payload.get("url", ""),
                "created_utc": payload.get("created_utc", 0),
                "num_comments": payload.get("num_comments", 0),
                "source": payload.get("source", "Reddit"),
                "dataset_name": payload.get("dataset_name", collection_name)
            })
        
        df = pd.DataFrame(data)
        
        # Save to CSV
        if output_path is None:
            output_path = f"data/processed/csv/{collection_name}_export.csv"
        
        os.makedirs(Path(output_path).parent, exist_ok=True)
        df.to_csv(output_path, index=False)
        print(f"✅ Exported {len(data)} records to {output_path}")
        
        return output_path
    
    def list_collections(self) -> List[str]:
        """
        List all available collections.
        
        Returns:
            List of collection names
        """
        collections = self.client.get_collections()
        return [col.name for col in collections.collections]
    
    def get_collection_info(self, collection_name: str) -> Dict:
        """
        Get information about a collection.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Dictionary with collection information
        """
        if not self.client.collection_exists(collection_name):
            raise ValueError(f"Collection '{collection_name}' does not exist")
        
        info = self.client.get_collection(collection_name)
        return {
            "name": info.name,
            "vectors_count": info.vectors_count,
            "points_count": info.points_count,
            "segments_count": info.segments_count,
            "config": {
                "vector_size": info.config.params.vectors.size,
                "distance": info.config.params.vectors.distance
            }
        }
    
    def delete_collection(self, collection_name: str) -> None:
        """
        Delete a collection.
        
        Args:
            collection_name: Name of the collection to delete
        """
        if self.client.collection_exists(collection_name):
            self.client.delete_collection(collection_name)
            print(f"✅ Deleted collection: {collection_name}")
        else:
            print(f"⚠️ Collection '{collection_name}' does not exist")


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


def export_collection_to_csv(collection_name: str, output_path: Optional[str] = None) -> str:
    """
    Convenience function to export collection data using the default client.
    
    Args:
        collection_name: Name of the collection to export
        output_path: Path to save CSV file (optional)
        
    Returns:
        Path to the exported CSV file
    """
    return _default_client.export_collection_to_csv(collection_name, output_path)


def list_collections() -> List[str]:
    """
    Convenience function to list collections using the default client.
    
    Returns:
        List of collection names
    """
    return _default_client.list_collections()


def get_collection_info(collection_name: str) -> Dict:
    """
    Convenience function to get collection info using the default client.
    
    Args:
        collection_name: Name of the collection
        
    Returns:
        Dictionary with collection information
    """
    return _default_client.get_collection_info(collection_name)
