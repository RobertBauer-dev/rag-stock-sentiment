from pathlib import Path

from sentence_transformers import SentenceTransformer
import pandas as pd
import numpy as np
import os

from app.data.reddit_client import CSV_FOLDER
from app.vector_store import upload_embeddings_with_payloads

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

EMBEDDING_MODEL = "all-MiniLM-L6-v2"

ROOT_FOLDER = Path(__file__).resolve().parent.parent.parent
NPY_FOLDER = ROOT_FOLDER / "data" / "processed" / "npy"
os.makedirs(NPY_FOLDER, exist_ok=True)


def generate_embeddings(dataset_name: str):  # model_name: str = "all-MiniLM-L6-v2"):
    """Indexing. Return
      EMB_TYPE = Tensor | ndarray | list[Tensor] | list[dict[str, Tensor]]"""
    csv_path = CSV_FOLDER / f"{dataset_name}.csv"
    npy_path = NPY_FOLDER / f"{dataset_name}.npy"

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"❌ CSV-Datei nicht gefunden: {csv_path}")

    print(f"📥 Lade CSV: {csv_path}")
    df = pd.read_csv(csv_path)

    texts = (df["title"].fillna("") + " " + df["selftext"].fillna("")).tolist()

    print(f"🧠 Lade Modell: {EMBEDDING_MODEL}")
    model = SentenceTransformer(EMBEDDING_MODEL)

    print(f"⚙️ Erzeuge {len(texts)} Embeddings ...")
    embeddings = model.encode(texts, show_progress_bar=True)

    os.makedirs("data/processed/npy", exist_ok=True)
    np.save(str(npy_path), embeddings)
    print(f"✅ Embeddings gespeichert unter {npy_path}")

    return embeddings, df


def process_and_store_embeddings(dataset_name: str):
    """
    Complete pipeline: generate embeddings and store them in vector store.
    """
    print(f"🔄 Processing embeddings for dataset: {dataset_name}")
    
    # Generate embeddings
    embeddings, df = generate_embeddings(dataset_name)
    
    # Get CSV path
    csv_path = CSV_FOLDER / f"{dataset_name}.csv"
    
    # Upload to vector store
    upload_embeddings_with_payloads(embeddings, str(csv_path), dataset_name)
    
    print(f"✅ Complete pipeline finished for {dataset_name}")
    return embeddings, df
