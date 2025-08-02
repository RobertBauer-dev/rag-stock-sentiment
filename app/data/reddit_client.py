# app/data/reddit_client.py

import os
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
