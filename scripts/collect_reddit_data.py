#!/usr/bin/env python3
"""
Script to collect Reddit data for stock sentiment analysis.
"""

import sys
import argparse
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent.parent / "app"))

from app.data.reddit_client import collect as collect_reddit_data
from app.utils.datetime_utils import generate_dataset_name


def main():
    parser = argparse.ArgumentParser(description="Collect Reddit data for stock sentiment analysis")
    parser.add_argument("stock_symbol", help="Stock symbol (e.g., AAPL, TSLA)")
    parser.add_argument("--query", help="Search query (default: '{stock_symbol} stock')")
    parser.add_argument("--limit", type=int, default=50, help="Number of posts to collect (default: 50)")
    parser.add_argument("--dataset-name", help="Custom dataset name (default: auto-generated)")
    
    args = parser.parse_args()
    
    # Generate dataset name if not provided
    if not args.dataset_name:
        args.dataset_name = generate_dataset_name(args.stock_symbol)
    
    # Generate search query if not provided
    if not args.query:
        args.query = f"{args.stock_symbol} stock"
    
    print(f"🔍 Collecting Reddit data for {args.stock_symbol}")
    print(f"📝 Search query: {args.query}")
    print(f"📊 Dataset name: {args.dataset_name}")
    print(f"📈 Limit: {args.limit} posts")
    
    try:
        collect_reddit_data(args.query, args.dataset_name, args.limit)
        print(f"✅ Successfully collected data for {args.stock_symbol}")
        print(f"💾 Dataset saved as: {args.dataset_name}")
    except Exception as e:
        print(f"❌ Error collecting data: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
