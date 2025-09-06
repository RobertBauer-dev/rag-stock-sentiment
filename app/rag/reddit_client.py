# app/data/reddit_client.py

import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv  # load vars from .env into env vars
import praw  # Python Reddit API Wrapper
from typing import List, Dict

load_dotenv()

# Konfiguration aus .env
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT")

print(f"client_id={REDDIT_CLIENT_ID}, secret={'✓' if REDDIT_CLIENT_SECRET else '❌'}, agent={REDDIT_USER_AGENT}")

# Reddit API-Client mit PRAW
reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=REDDIT_USER_AGENT
)

print("Verbindung erfolgreich. Reddit user:", reddit.user.me())


def search_stock_posts(keyword: str, limit: int = 20) -> List[Dict]:
    """
    Sucht nach Reddit-Posts zu einem bestimmten Aktien-Stichwort.
    """
    posts = []
    subreddit = reddit.subreddit("stocks+investing+wallstreetbets")

    for submission in subreddit.search(keyword, sort="new", limit=limit):
        post_data = {
            "title": submission.title,
            "score": submission.score,
            "url": submission.url,
            "created_utc": submission.created_utc,
            "num_comments": submission.num_comments,
            "selftext": submission.selftext
        }
        posts.append(post_data)

    return posts


from app.core.config import AppConfig

# Use centralized configuration
CSV_FOLDER = AppConfig.RAG_DATA_DIR
CSV_FOLDER.mkdir(parents=True, exist_ok=True)


def collect(search_query: str, dataset_name: str, limit: int = 50):
    print(f"🔍 Suche Reddit-Posts zu: '{search_query}'")
    posts = search_stock_posts(search_query, limit=limit)

    if not posts:
        raise ValueError("❌ Keine Posts gefunden – überprüfe deine Query oder Reddit-API!")

    csv_path = CSV_FOLDER / f"{dataset_name}.csv"

    # Speichern als CSV
    df = pd.DataFrame(posts)
    df.to_csv(csv_path, index=False)
    print(f"✅ Reddit-Daten gespeichert unter {csv_path}")
