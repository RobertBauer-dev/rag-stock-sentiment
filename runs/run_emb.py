from app.data.reddit_client import search_stock_posts
from app.embedding.embed_posts import generate_embeddings
import pandas as pd
import os


def collect_and_embed(search_query: str, dataset_name: str, limit: int = 50):
    print(f"🔍 Suche Reddit-Posts zu: '{search_query}'")
    posts = search_stock_posts(search_query, limit=limit)

    if not posts:
        raise ValueError("❌ Keine Posts gefunden – überprüfe deine Query oder Reddit-API!")

    # Ordnerstruktur sicherstellen
    os.makedirs("data/processed/csv", exist_ok=True)

    # CSV-Pfad definieren
    csv_path = f"data/processed/csv/{dataset_name}.csv"

    # Speichern als CSV
    df = pd.DataFrame(posts)
    df.to_csv(csv_path, index=False)
    print(f"✅ Reddit-Daten gespeichert unter {csv_path}")

    # Embeddings erzeugen
    generate_embeddings(dataset_name)


if __name__ == "__main__":
    # Beispiel: "Tesla earnings", wird gespeichert als "tesla_2025q2"
    collect_and_embed("Tesla earnings", "tesla_2025q2", limit=50)
