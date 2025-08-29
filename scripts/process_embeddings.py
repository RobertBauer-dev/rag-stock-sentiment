#!/usr/bin/env python3
"""
Script to process embeddings for collected Reddit data.
"""

import sys
import argparse
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent.parent / "app"))

from app.embedding.embed_posts import process_and_store_embeddings
from app.utils.file_utils import list_files_by_pattern


def main():
    parser = argparse.ArgumentParser(description="Process embeddings for Reddit data")
    parser.add_argument("dataset_name", help="Dataset name to process (e.g., aapl_20241201_143022)")
    parser.add_argument("--model", help="Embedding model to use (default: all-MiniLM-L6-v2)")
    parser.add_argument("--list-available", action="store_true", help="List available datasets")
    
    args = parser.parse_args()
    
    if args.list_available:
        # List available CSV files
        csv_files = list_files_by_pattern("*.csv", "data/processed/csv")
        if csv_files:
            print("📋 Available datasets:")
            for csv_file in sorted(csv_files):
                dataset_name = Path(csv_file).stem
                print(f"  - {dataset_name}")
        else:
            print("❌ No datasets found in data/processed/csv/")
        return
    
    print(f"🔄 Processing embeddings for dataset: {args.dataset_name}")
    
    if args.model:
        print(f"🧠 Using embedding model: {args.model}")
    
    try:
        embeddings, df = process_and_store_embeddings(args.dataset_name)
        print(f"✅ Successfully processed embeddings for {args.dataset_name}")
        print(f"📊 Processed {len(df)} posts")
        print(f"🔢 Embedding dimensions: {embeddings.shape[1]}")
    except Exception as e:
        print(f"❌ Error processing embeddings: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
