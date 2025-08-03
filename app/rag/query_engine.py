from qdrant_client import QdrantClient
from qdrant_client.http.models import Filter, FieldCondition, MatchValue
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv
import os

from sentence_transformers import SentenceTransformer

from app.embedding.embed_posts import EMBEDDING_MODEL

load_dotenv()
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
qdrant_client = QdrantClient(host="localhost", port=6333)


def search_similar_posts(query: str, collection_name: str = "tesla_2025q2", top_k: int = 5):
    # Query zu Embedding
    """embedding = openai_client.embeddings.create(
        input=query,
        model=EMBEDDING_MODEL
    ).data[0].embedding"""

    model = SentenceTransformer(EMBEDDING_MODEL)
    embedding = model.encode(query).tolist()

    # Ähnliche Einträge aus Qdrant holen
    search_result = qdrant_client.query_points(
        collection_name=collection_name,
        query=embedding,
        limit=top_k
    )

    return [hit.payload for hit in search_result.points]


def generate_answer_from_context(query: str, context_posts: list[dict]) -> str:
    context_text = "\n\n".join([
        f"{p['title']}\n{p.get('selftext', '')}" for p in context_posts
    ])

    prompt = f"""Du bist ein Finanzanalyst. Beantworte folgende Frage basierend auf Reddit-Posts:

Frage: {query}

Reddit-Kontext:
{context_text}

Antwort:"""

    response = openai_client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content
