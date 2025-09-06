#!/usr/bin/env python3
"""
Script to scrape SEC 10-Q financial documents.
Refactored from the original scrape_quarterlies.py with improved structure.
"""

import sys
import argparse
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent.parent.parent / "app"))

from app.financial.sec_scraper import SECScraper
from app.financial.parsers.financial_parser import FinancialParser
from app.core.logging import get_logger

logger = get_logger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Scrape SEC 10-Q financial documents")
    parser.add_argument("ticker", help="Stock ticker symbol (e.g., AAPL, TSLA)")
    parser.add_argument("year", type=int, help="Year (e.g., 2024)")
    parser.add_argument("quarter", type=int, choices=[1, 2, 3, 4], help="Quarter (1-4)")
    parser.add_argument("--list-docs", action="store_true", help="List available documents")
    parser.add_argument("--fetch-all", action="store_true", help="Fetch all financial documents")
    parser.add_argument("--extract", action="store_true", help="Extract financial statements from downloaded files")
    
    args = parser.parse_args()
    
    print(f"🔍 Scraping SEC data for {args.ticker} {args.year}Q{args.quarter}")
    
    try:
        scraper = SECScraper()
        
        if args.list_docs:
            print(f"📋 Listing available documents for {args.ticker} {args.year}Q{args.quarter}...")
            documents = scraper.list_filing_documents(args.ticker, args.year, args.quarter)
            
            if documents:
                print(f"✅ Found {len(documents)} documents")
            else:
                print("❌ No documents found")
            return
        
        if args.fetch_all:
            print(f"📊 Fetching all financial documents for {args.ticker} {args.year}Q{args.quarter}...")
            downloaded_files = scraper.fetch_all_financial_documents(args.ticker, args.year, args.quarter)
            
            if downloaded_files:
                print(f"✅ Successfully downloaded {len(downloaded_files)} files:")
                for file_path in downloaded_files:
                    print(f"   - {Path(file_path).name}")
            else:
                print("❌ No files downloaded")
        else:
            print(f"📄 Fetching main 10-Q document for {args.ticker} {args.year}Q{args.quarter}...")
            file_path = scraper.fetch_10q_by_quarter(args.ticker, args.year, args.quarter)
            
            if file_path:
                print(f"✅ Successfully downloaded: {Path(file_path).name}")
            else:
                print("❌ No file downloaded")
                return
        
        if args.extract:
            print(f"📈 Extracting financial statements...")
            parser = FinancialParser()
            
            # Find the main document for extraction
            if args.fetch_all:
                main_doc = None
                for file_path in downloaded_files:
                    if f"{args.ticker.lower()}-" in file_path and file_path.endswith('.htm'):
                        main_doc = file_path
                        break
                
                if not main_doc:
                    print("⚠️  No main document found for extraction")
                    return
            else:
                main_doc = file_path
            
            financial_data = parser.extract_financial_statements(main_doc)
            
            if financial_data:
                print(f"✅ Successfully extracted financial data:")
                print(f"   - Income Statement: {len(financial_data.get('income_statement', {}))} items")
                print(f"   - Balance Sheet: {len(financial_data.get('balance_sheet', {}))} items")
                print(f"   - Cash Flow: {len(financial_data.get('cash_flow', {}))} items")
            else:
                print("❌ No financial data extracted")
        
    except Exception as e:
        logger.error(f"Script execution failed: {e}")
        print(f"❌ Script execution failed: {e}")
        sys.exit(1)
    
    logger.info("Script execution completed")


if __name__ == "__main__":
    main()
