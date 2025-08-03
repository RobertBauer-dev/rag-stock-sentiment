from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance, PointStruct
import numpy as np


def upload_embeddings(embeddings: np.ndarray, collection_name: str = "stocks"):
    dim = embeddings.shape[1]

    client = QdrantClient(host="localhost", port=6333)

    if not client.collection_exists(collection_name):
        print(f"Collection {collection_name} does not exist. We create one ...")
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
        )

    # Daten in Qdrant einfügen
    points = [
        PointStruct(id=i, vector=embeddings[i].tolist(), payload={})
        for i in range(len(embeddings))
    ]

    client.upsert(collection_name=collection_name, points=points)

    print(f"✅ Hochgeladen: {len(points)} Vektoren → Collection '{collection_name}'")


"""
example payload
{
  "title": "Tesla Q2 results surprise Wall Street",
  "score": 138,
  "source": "Reddit"
}
"""
