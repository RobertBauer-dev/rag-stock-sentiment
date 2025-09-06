#!/usr/bin/env python3
"""
Script to query the RAG system for stock sentiment analysis.
"""

import sys
import argparse
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent.parent / "app"))

from app.rag.query_engine import search_similar_posts, generate_answer_from_context
from app.utils.datetime_utils import parse_dataset_name


def main():
    parser = argparse.ArgumentParser(description="Query the RAG system for stock sentiment")
    parser.add_argument("question", help="Question to ask about the stock")
    parser.add_argument("--stock", help="Stock symbol (e.g., AAPL, TSLA)")
    parser.add_argument("--collection", help="Collection name to search in")
    parser.add_argument("--top-k", type=int, default=5, help="Number of similar posts to retrieve (default: 5)")
    parser.add_argument("--show-context", action="store_true", help="Show retrieved context posts")
    
    args = parser.parse_args()
    
    # Determine collection name
    if args.collection:
        collection_name = args.collection
    elif args.stock:
        # Try to find the most recent collection for this stock
        # This is a simplified version - in practice you'd query the vector store
        print(f"⚠️  Please specify --collection for stock {args.stock}")
        print("   Available collections can be found by querying the vector store")
        sys.exit(1)
    else:
        print("❌ Please specify either --stock or --collection")
        sys.exit(1)
    
    print(f"🔍 Querying RAG system")
    print(f"❓ Question: {args.question}")
    print(f"📊 Collection: {collection_name}")
    print(f"📈 Top-k: {args.top_k}")
    
    try:
        # Search for similar posts
        print("\n🔍 Searching for similar posts...")
        context_posts = search_similar_posts(args.question, collection_name, args.top_k)
        
        if args.show_context:
            print(f"\n📋 Retrieved {len(context_posts)} context posts:")
            for i, post in enumerate(context_posts, 1):
                print(f"\n{i}. {post['title']}")
                print(f"   Score: {post.get('score', 'N/A')}")
                print(f"   Text: {post.get('selftext', '')[:200]}...")
        
        # Generate answer
        print("\n🧠 Generating answer...")
        answer = generate_answer_from_context(args.question, context_posts)
        
        print(f"\n💡 Answer:")
        print(f"{answer}")
        
    except Exception as e:
        print(f"❌ Error querying RAG system: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
