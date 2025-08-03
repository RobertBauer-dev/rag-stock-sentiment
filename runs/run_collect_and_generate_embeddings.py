from app.data.reddit_client import collect
from app.embedding.embed_posts import generate_embeddings


if __name__ == "__main__":
    # Beispiel: "Tesla earnings", wird gespeichert als "tesla_2025q2"
    collect("Tesla earnings", "tesla_2025q2", limit=50)
    generate_embeddings("tesla_2025q2")
