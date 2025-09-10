#!/usr/bin/env python3
"""
AI-Powered SEC 10-Q Financial Document Scraper.
Uses LLM for intelligent financial statement extraction with high accuracy.
"""

import sys
import argparse
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent.parent.parent / "app"))

from app.financial.sec_scraper import SECScraper
from app.financial.ai_scraper import AIFinancialScraper
from app.financial.data_warehouse import FinancialDataWarehouse
from app.financial.kpi_calculator import KPICalculator
from app.core.logging import get_logger

logger = get_logger(__name__)


def main():
    parser = argparse.ArgumentParser(description="AI-Powered SEC 10-Q Financial Document Scraper")
    parser.add_argument("ticker", help="Stock ticker symbol (e.g., AAPL, TSLA)")
    parser.add_argument("year", type=int, help="Year (e.g., 2024)")
    parser.add_argument("quarter", type=int, choices=[1, 2, 3, 4], help="Quarter (1-4)")
    parser.add_argument("--list-docs", action="store_true", help="List available documents")
    parser.add_argument("--fetch-all", action="store_true", help="Fetch all financial documents")
    parser.add_argument("--ai-extract", action="store_true", help="Use AI for financial statement extraction")
    parser.add_argument("--confidence-threshold", type=float, default=0.7, help="Minimum confidence threshold (0.0-1.0)")
    parser.add_argument("--model", default="gpt-4o", help="OpenAI model to use (default: gpt-4o)")
    parser.add_argument("--store-warehouse", action="store_true", help="Store results in data warehouse")
    
    args = parser.parse_args()
    
    print(f"🤖 AI-Powered SEC scraping for {args.ticker} {args.year}Q{args.quarter}")
    print(f"🎯 Model: {args.model}")
    print(f"📊 Confidence threshold: {args.confidence_threshold}")
    
    try:
        # Initialize components
        sec_scraper = SECScraper()
        ai_scraper = AIFinancialScraper(model=args.model)
        
        if args.store_warehouse:
            warehouse = FinancialDataWarehouse()
            kpi_calculator = KPICalculator()
        
        if args.list_docs:
            print(f"📋 Listing available documents for {args.ticker} {args.year}Q{args.quarter}...")
            documents = sec_scraper.list_filing_documents(args.ticker, args.year, args.quarter)
            
            if documents:
                print(f"✅ Found {len(documents)} documents")
            else:
                print("❌ No documents found")
            return
        
        # Fetch documents
        if args.fetch_all:
            print(f"📊 Fetching all financial documents for {args.ticker} {args.year}Q{args.quarter}...")
            downloaded_files = sec_scraper.fetch_all_financial_documents(args.ticker, args.year, args.quarter)
        else:
            print(f"📄 Fetching main 10-Q document for {args.ticker} {args.year}Q{args.quarter}...")
            file_path = sec_scraper.fetch_10q_by_quarter(args.ticker, args.year, args.quarter)
            downloaded_files = [file_path] if file_path else []
        
        if not downloaded_files:
            print("❌ No files downloaded")
            return
        
        print(f"✅ Successfully downloaded {len(downloaded_files)} files")
        
        # AI extraction
        if args.ai_extract:
            print(f"🤖 Starting AI-powered financial statement extraction...")
            
            best_extraction = None
            best_confidence = 0.0
            best_file = None
            
            for file_path in downloaded_files:
                if file_path.endswith('.htm'):
                    print(f"🔍 AI-analyzing: {Path(file_path).name}")
                    
                    try:
                        financial_data, confidence = ai_scraper.extract_with_confidence(file_path, args.ticker)
                        
                        print(f"📊 Confidence: {confidence:.2f} - Income: {len(financial_data.get('income_statement', {}))} items, "
                              f"Balance: {len(financial_data.get('balance_sheet', {}))} items, "
                              f"Cash Flow: {len(financial_data.get('cash_flow', {}))} items")
                        
                        if confidence > best_confidence:
                            best_confidence = confidence
                            best_extraction = financial_data
                            best_file = file_path
                            
                    except Exception as e:
                        logger.error(f"❌ AI extraction failed for {file_path}: {e}")
                        continue
            
            if best_extraction and best_confidence >= args.confidence_threshold:
                print(f"🎯 Best extraction: {Path(best_file).name} (confidence: {best_confidence:.2f})")
                
                # Store in warehouse if requested
                if args.store_warehouse:
                    print(f"💾 Storing in data warehouse...")
                    
                    # Add company
                    warehouse.add_company(args.ticker, f"{args.ticker} Inc.", "0000000000")
                    
                    # Add filing
                    filing_id = warehouse.add_filing(
                        ticker=args.ticker,
                        quarter=args.quarter,
                        year=args.year,
                        report_date=f"{args.year}-{args.quarter*3:02d}-01",
                        filing_date=f"{args.year}-{args.quarter*3:02d}-01",
                        form_type="10-Q",
                        accession_number="AI-EXTRACTED",
                        source_file=Path(best_file).name
                    )
                    
                    # Add financial data
                    warehouse.add_financial_data(filing_id, best_extraction)
                    
                    # Calculate and store KPIs
                    kpis = kpi_calculator.calculate_kpis(best_extraction, args.ticker, args.year, args.quarter)
                    if kpis:
                        warehouse.add_kpis(filing_id, best_extraction, args.ticker, args.year, args.quarter)
                        print(f"📈 Calculated and stored {len(kpis)} KPIs")
                    else:
                        print("⚠️ No KPIs calculated")
                    
                    print(f"✅ Successfully stored in data warehouse")
                
                # Save JSON file
                json_path = best_file.replace('.htm', '_ai_financial_data.json')
                import json
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(best_extraction, f, indent=2, ensure_ascii=False)
                print(f"💾 Saved AI extraction to: {json_path}")
                
            else:
                print(f"❌ No extraction met confidence threshold ({args.confidence_threshold})")
                if best_extraction:
                    print(f"⚠️ Best confidence was: {best_confidence:.2f}")
        
    except Exception as e:
        logger.error(f"Script execution failed: {e}")
        print(f"❌ Script execution failed: {e}")
        sys.exit(1)
    
    logger.info("AI scraping script execution completed")


if __name__ == "__main__":
    main()
