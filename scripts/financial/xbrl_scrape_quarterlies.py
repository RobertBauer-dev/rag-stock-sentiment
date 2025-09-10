#!/usr/bin/env python3
"""
XBRL-based SEC 10-Q Financial Document Scraper.
Uses SEC's structured XBRL data sets for the most reliable extraction.
"""

import sys
import argparse
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.financial.xbrl_scraper import XBRLFinancialScraper
from app.financial.data_warehouse import FinancialDataWarehouse
from app.financial.kpi_calculator import KPICalculator
from app.core.logging import get_logger

logger = get_logger(__name__)


def main():
    parser = argparse.ArgumentParser(description="XBRL-based SEC 10-Q Financial Document Scraper")
    parser.add_argument("ticker", help="Stock ticker symbol (e.g., AAPL, TSLA)")
    parser.add_argument("year", type=int, help="Year (e.g., 2024)")
    parser.add_argument("quarter", type=int, choices=[1, 2, 3, 4], help="Quarter (1-4)")
    parser.add_argument("--store-warehouse", action="store_true", help="Store results in data warehouse")
    parser.add_argument("--export-json", action="store_true", help="Export results to JSON file")
    parser.add_argument("--multiple-quarters", type=int, help="Scrape multiple quarters (e.g., 4 for last 4 quarters)")
    
    args = parser.parse_args()
    
    logger.info(f"📊 XBRL-based SEC scraping for {args.ticker}")
    logger.info(f"🎯 Target: {args.year}Q{args.quarter}")
    if args.multiple_quarters:
        logger.info(f"📈 Multiple quarters: {args.multiple_quarters}")
    
    try:
        # Initialize components
        xbrl_scraper = XBRLFinancialScraper()
        
        if args.store_warehouse:
            warehouse = FinancialDataWarehouse()
            kpi_calculator = KPICalculator()
        
        # Determine quarters to scrape
        quarters_to_scrape = []
        
        if args.multiple_quarters:
            # Scrape multiple quarters
            for i in range(args.multiple_quarters):
                q = args.quarter - i
                y = args.year
                
                # Handle year rollover
                while q <= 0:
                    q += 4
                    y -= 1
                
                quarters_to_scrape.append((y, q))
        else:
            # Single quarter
            quarters_to_scrape.append((args.year, args.quarter))
        
        logger.info(f"📋 Quarters to scrape: {quarters_to_scrape}")
        
        # Scrape each quarter
        successful_scrapes = 0
        total_scrapes = len(quarters_to_scrape)
        
        for year, quarter in quarters_to_scrape:
            logger.info(f"\n🔍 Scraping {args.ticker} {year}Q{quarter}...")
            
            try:
                # Scrape XBRL data
                financial_data = xbrl_scraper.scrape_quarterly_data(args.ticker, year, quarter)
                
                if not financial_data or not any(financial_data.get(key) for key in ['income_statement', 'balance_sheet', 'cash_flow']):
                    logger.info(f"⚠️ No financial data extracted for {args.ticker} {year}Q{quarter}")
                    continue
                
                # Display results
                income_items = len(financial_data.get('income_statement', {}))
                balance_items = len(financial_data.get('balance_sheet', {}))
                cashflow_items = len(financial_data.get('cash_flow', {}))
                
                logger.info(f"✅ XBRL extraction successful:")
                logger.info(f"   📈 Income Statement: {income_items} items")
                logger.info(f"   💰 Balance Sheet: {balance_items} items")
                logger.info(f"   💸 Cash Flow: {cashflow_items} items")
                
                # Store in warehouse if requested
                if args.store_warehouse:
                    logger.info(f"💾 Storing in data warehouse...")
                    
                    # Add company
                    warehouse.add_company(args.ticker, f"{args.ticker} Inc.", "0000000000")
                    
                    # Add filing
                    filing_id = warehouse.add_filing(
                        ticker=args.ticker,
                        quarter=quarter,
                        year=year,
                        report_date=f"{year}-{quarter*3:02d}-01",
                        filing_date=f"{year}-{quarter*3:02d}-01",
                        form_type="10-Q",
                        accession_number="XBRL-EXTRACTED",
                        source_file=f"{args.ticker}_{year}Q{quarter}_xbrl"
                    )
                    
                    # Add financial data
                    warehouse.add_financial_data(filing_id, financial_data)
                    
                    # Calculate and store KPIs
                    kpis = kpi_calculator.calculate_kpis(financial_data, args.ticker, year, quarter)
                    if kpis:
                        warehouse.add_kpis(filing_id, financial_data, args.ticker, year, quarter)
                        logger.info(f"📊 Calculated and stored {len(kpis)} KPIs")
                    else:
                        logger.info("⚠️ No KPIs calculated")
                    
                    logger.info(f"✅ Successfully stored in data warehouse")
                
                # Export JSON if requested
                if args.export_json:
                    json_filename = f"{args.ticker}_{year}Q{quarter}_xbrl_financial_data.json"
                    json_path = Path(json_filename)
                    
                    import json
                    with open(json_path, 'w', encoding='utf-8') as f:
                        json.dump(financial_data, f, indent=2, ensure_ascii=False)
                    
                    logger.info(f"💾 Exported to: {json_path}")
                
                successful_scrapes += 1
                
            except Exception as e:
                logger.error(f"❌ Failed to scrape {args.ticker} {year}Q{quarter}: {e}")
                logger.info(f"❌ Failed to scrape {args.ticker} {year}Q{quarter}: {e}")
                continue
        
        # Summary
        logger.info(f"\n📊 Scraping Summary:")
        logger.info(f"   ✅ Successful: {successful_scrapes}/{total_scrapes}")
        logger.info(f"   📈 Success rate: {successful_scrapes/total_scrapes*100:.1f}%")
        
        if successful_scrapes > 0:
            logger.info(f"🎉 XBRL scraping completed successfully!")
        else:
            logger.info(f"❌ No quarters were successfully scraped")
        
    except Exception as e:
        logger.error(f"Script execution failed: {e}")
        logger.info(f"❌ Script execution failed: {e}")
        sys.exit(1)
    
    logger.info("XBRL scraping script execution completed")


if __name__ == "__main__":
    main()
