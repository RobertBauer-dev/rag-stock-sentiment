"""
Embedding generation and processing for Reddit posts.
"""

from pathlib import Path
from sentence_transformers import SentenceTransformer
import pandas as pd
import numpy as np
import os
import mlflow
from typing import Tuple, Dict, Any

from app.data.reddit_client import CSV_FOLDER
from app.vector_store.client import upload_embeddings_with_payloads


class EmbeddingConfig:
    """Configuration for embedding models."""
    
    EMBEDDING_MODELS = {
        "all-MiniLM-L6-v2": {
            "provider": "sentence-transformers",
            "dim": 384,
            "cost": "free (local)",
            "description": "Kompakter, schneller Transformer für semantische Ähnlichkeit. Ideal für lokale RAG-Projekte."
        },
        "text-embedding-3-small": {
            "provider": "openai",
            "dim": 1536,
            "cost": "$0.00002 / 1k tokens",
            "description": "Schnelles, günstiges Embedding-Modell von OpenAI mit guter Qualität."
        },
        "text-embedding-3-large": {
            "provider": "openai",
            "dim": 3072,
            "cost": "$0.00013 / 1k tokens",
            "description": "Hochwertiges Embedding-Modell von OpenAI mit maximaler Genauigkeit für Such- und RAG-Anwendungen."
        },
        "multi-qa-MiniLM-L6-cos-v1": {
            "provider": "sentence-transformers",
            "dim": 384,
            "cost": "free (local)",
            "description": "Feinjustiert für Frage-Antwort-Szenarien mit besserem Kontextbezug."
        },
        "e5-base": {
            "provider": "sentence-transformers",
            "dim": 768,
            "cost": "free (local)",
            "description": "Neuere Modelle mit starker Retrieval-Performance, auch gut für multilingual."
        }
    }
    
    DEFAULT_MODEL = "all-MiniLM-L6-v2"


class EmbeddingProcessor:
    """Processor for generating and managing embeddings."""
    
    def __init__(self, model_name: str = None):
        self.model_name = model_name or EmbeddingConfig.DEFAULT_MODEL
        self.model = SentenceTransformer(self.model_name)
        
        # Setup paths
        self.root_folder = Path(__file__).resolve().parent.parent.parent
        self.npy_folder = self.root_folder / "data" / "processed" / "npy"
        os.makedirs(self.npy_folder, exist_ok=True)
    
    def generate_embeddings(self, dataset_name: str) -> Tuple[np.ndarray, pd.DataFrame]:
        """
        Generate embeddings for a dataset.
        
        Args:
            dataset_name: Name of the dataset to process
            
        Returns:
            Tuple of (embeddings, dataframe)
        """
        csv_path = CSV_FOLDER / f"{dataset_name}.csv"
        npy_path = self.npy_folder / f"{dataset_name}.npy"

        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"❌ CSV-Datei nicht gefunden: {csv_path}")

        print(f"📥 Lade CSV: {csv_path}")
        df = pd.read_csv(csv_path)

        # Combine title and text for embedding
        texts = (df["title"].fillna("") + " " + df["selftext"].fillna("")).tolist()

        print(f"🧠 Lade Modell: {self.model_name}")
        print(f"⚙️ Erzeuge {len(texts)} Embeddings ...")
        embeddings = self.model.encode(texts, show_progress_bar=True)

        # Save embeddings
        np.save(str(npy_path), embeddings)
        print(f"✅ Embeddings gespeichert unter {npy_path}")

        return embeddings, df
    
    def process_and_store_embeddings(self, dataset_name: str) -> Tuple[np.ndarray, pd.DataFrame]:
        """
        Complete pipeline: generate embeddings and store them in vector store.
        With MLflow tracking.
        
        Args:
            dataset_name: Name of the dataset to process
            
        Returns:
            Tuple of (embeddings, dataframe)
        """
        try:
            with mlflow.start_run(run_name=f"embeddings_{dataset_name}"):
                print(f"🔄 Processing embeddings for dataset: {dataset_name}")
                
                # Generate embeddings
                print("📥 Loading and processing data...")
                embeddings, df = self.generate_embeddings(dataset_name)
                
                # Get CSV path
                csv_path = CSV_FOLDER / f"{dataset_name}.csv"
                
                # Log parameters
                print("📊 Logging parameters to MLflow...")
                mlflow.log_param("embedding_model", self.model_name)
                mlflow.log_param("dataset_name", dataset_name)
                mlflow.log_param("num_posts", len(df))
                mlflow.log_param("csv_path", str(csv_path))
                
                # Log artifacts
                print("💾 Logging artifacts to MLflow...")
                npy_path = f"data/processed/npy/{dataset_name}.npy"
                if os.path.exists(csv_path):
                    mlflow.log_artifact(str(csv_path))
                if os.path.exists(npy_path):
                    mlflow.log_artifact(npy_path)
                
                # Upload to vector store
                print("🚀 Uploading to vector store...")
                upload_embeddings_with_payloads(embeddings, str(csv_path), dataset_name)
                
                print(f"✅ Complete pipeline finished for {dataset_name}")
                return embeddings, df
                
        except Exception as e:
            print(f"❌ Error in process_and_store_embeddings: {str(e)}")
            # Log error to MLflow if run is still active
            try:
                mlflow.log_param("error", str(e))
            except:
                pass
            raise e


# Global processor instance
_default_processor = EmbeddingProcessor()


def generate_embeddings(dataset_name: str) -> Tuple[np.ndarray, pd.DataFrame]:
    """
    Convenience function to generate embeddings using the default processor.
    
    Args:
        dataset_name: Name of the dataset to process
        
    Returns:
        Tuple of (embeddings, dataframe)
    """
    return _default_processor.generate_embeddings(dataset_name)


def process_and_store_embeddings(dataset_name: str) -> Tuple[np.ndarray, pd.DataFrame]:
    """
    Convenience function to process and store embeddings using the default processor.
    
    Args:
        dataset_name: Name of the dataset to process
        
    Returns:
        Tuple of (embeddings, dataframe)
    """
    return _default_processor.process_and_store_embeddings(dataset_name)


# For backward compatibility
EMBEDDING_MODEL = EmbeddingConfig.DEFAULT_MODEL
