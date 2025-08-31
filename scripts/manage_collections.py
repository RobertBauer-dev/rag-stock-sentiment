#!/usr/bin/env python3
"""
Script to manage Qdrant collections for stock sentiment data.
"""

import sys
import argparse
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent.parent / "app"))

from app.vector_store.client import (
    list_collections, 
    get_collection_info, 
    delete_collection,
    export_collection_to_csv
)


def main():
    parser = argparse.ArgumentParser(description="Manage Qdrant collections")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # List collections
    list_parser = subparsers.add_parser("list", help="List all collections")
    
    # Show collection info
    info_parser = subparsers.add_parser("info", help="Show collection information")
    info_parser.add_argument("collection_name", help="Name of the collection")
    
    # Export collection
    export_parser = subparsers.add_parser("export", help="Export collection to CSV")
    export_parser.add_argument("collection_name", help="Name of the collection")
    export_parser.add_argument("--output", help="Output CSV file path (optional)")
    
    # Delete collection
    delete_parser = subparsers.add_parser("delete", help="Delete a collection")
    delete_parser.add_argument("collection_name", help="Name of the collection")
    delete_parser.add_argument("--force", action="store_true", help="Force deletion without confirmation")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == "list":
            collections = list_collections()
            if collections:
                print("📋 Available collections:")
                for i, collection in enumerate(collections, 1):
                    print(f"  {i}. {collection}")
            else:
                print("❌ No collections found")
        
        elif args.command == "info":
            info = get_collection_info(args.collection_name)
            print(f"📊 Collection: {info['name']}")
            print(f"   Points: {info['points_count']}")
            print(f"   Vectors: {info['vectors_count']}")
            print(f"   Segments: {info['segments_count']}")
            print(f"   Vector size: {info['config']['vector_size']}")
            print(f"   Distance: {info['config']['distance']}")
        
        elif args.command == "export":
            output_path = export_collection_to_csv(args.collection_name, args.output)
            if output_path:
                print(f"✅ Exported to: {output_path}")
        
        elif args.command == "delete":
            if not args.force:
                confirm = input(f"⚠️  Are you sure you want to delete collection '{args.collection_name}'? (y/N): ")
                if confirm.lower() != 'y':
                    print("❌ Deletion cancelled")
                    return
            
            delete_collection(args.collection_name)
            print(f"✅ Collection '{args.collection_name}' deleted")
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
