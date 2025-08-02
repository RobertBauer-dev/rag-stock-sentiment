from app.data.reddit_client import search_stock_posts

if __name__ == "__main__":
    results = search_stock_posts("Tesla earnings", limit=5)
    for post in results:
        print(f"{post['title']} ({post['score']})")
        print(f"{post['selftext'][:100]}...\n")
