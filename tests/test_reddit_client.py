# tests/test_reddit_client.py
from app.data.reddit_client import search_stock_posts


def test_post_retrieval():
    results = search_stock_posts("Tesla", limit=2)
    assert isinstance(results, list)
    assert len(results) > 0
    assert "title" in results[0]
