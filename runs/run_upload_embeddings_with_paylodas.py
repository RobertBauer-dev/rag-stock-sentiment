import numpy as np

from app.data.reddit_client import CSV_FOLDER
from app.embedding.embed_posts import NPY_FOLDER
from app.vector_store import upload_embeddings_with_payloads

if __name__ == "__main__":
    collection_name = "tesla_2025q2"
    embeddings = np.load(NPY_FOLDER / f"{collection_name}.npy")
    print("Load NPY success", embeddings[0][0])
    upload_embeddings_with_payloads(embeddings,
                                    csv_path=CSV_FOLDER / f"{collection_name}.csv",
                                    collection_name=collection_name)
