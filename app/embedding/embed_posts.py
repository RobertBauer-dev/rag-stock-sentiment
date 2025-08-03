from pathlib import Path

from sentence_transformers import SentenceTransformer
import pandas as pd
import numpy as np
import os

from app.data.reddit_client import CSV_FOLDER

ROOT_FOLDER = Path(__file__).resolve().parent.parent.parent
NPY_FOLDER = ROOT_FOLDER / "data" / "processed" / "npy"
os.makedirs(NPY_FOLDER, exist_ok=True)


def generate_embeddings(dataset_name: str, model_name: str = "all-MiniLM-L6-v2"):
    csv_path = CSV_FOLDER / f"{dataset_name}.csv"
    npy_path = NPY_FOLDER / f"{dataset_name}.npy"

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"❌ CSV-Datei nicht gefunden: {csv_path}")

    print(f"📥 Lade CSV: {csv_path}")
    df = pd.read_csv(csv_path)

    texts = (df["title"].fillna("") + " " + df["selftext"].fillna("")).tolist()

    print(f"🧠 Lade Modell: {model_name}")
    model = SentenceTransformer(model_name)

    print(f"⚙️ Erzeuge {len(texts)} Embeddings ...")
    embeddings = model.encode(texts, show_progress_bar=True)

    os.makedirs("data/processed/npy", exist_ok=True)
    np.save(str(npy_path), embeddings)
    print(f"✅ Embeddings gespeichert unter {npy_path}")

    return embeddings, df
