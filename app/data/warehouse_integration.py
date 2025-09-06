#!/usr/bin/env python3
"""
Integration zwischen scrape_quarterlies.py und FinancialDataWarehouse.
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any
import logging

from scrape_quarterlies import (
    fetch_all_financial_documents, 
    extract_financial_statements,
    get_cik_from_ticker,
    logger
)
from financial_data_warehouse import FinancialDataWarehouse

class ScrapingToWarehousePipeline:
    """
    Pipeline für das Scraping von Financial Data und Speicherung im Data Warehouse.
    """
    
    def __init__(self, warehouse_path: str = "data/financial_warehouse.db"):
        """
        Initialize the pipeline.
        
        Args:
            warehouse_path (str): Path to the data warehouse database
        """
        self.warehouse = FinancialDataWarehouse(warehouse_path)
        logger.info("🏗️ Initialized Scraping-to-Warehouse Pipeline")
    
    def scrape_and_store_company_quarter(self, ticker: str, year: int, quarter: int) -> bool:
        """
        Scrape financial data for a specific company quarter and store in warehouse.
        
        Args:
            ticker (str): Stock ticker symbol
            year (int): Year
            quarter (int): Quarter (1-4)
            
        Returns:
            bool: Success status
        """
        try:
            logger.info(f"🚀 Starting pipeline for {ticker} {year}Q{quarter}")
            
            # Step 1: Get company info
            cik = get_cik_from_ticker(ticker)
            company_name = f"{ticker} Inc."  # TODO: Get real company name from SEC
            
            # Step 2: Add company to warehouse
            self.warehouse.add_company(ticker, company_name, cik)
            
            # Step 3: Scrape financial documents
            logger.info(f"📥 Scraping financial documents for {ticker} {year}Q{quarter}")
            downloaded_files = fetch_all_financial_documents(ticker, year, quarter)
            
            if not downloaded_files:
                logger.warning(f"⚠️ No documents found for {ticker} {year}Q{quarter}")
                return False
            
            # Step 4: Process each document
            for file_path in downloaded_files:
                if file_path.endswith('.htm'):
                    logger.info(f"📊 Processing document: {os.path.basename(file_path)}")
                    
                    # Extract financial statements
                    financial_data = extract_financial_statements(file_path)
                    
                    if financial_data and any(financial_data.get(stmt_type) for stmt_type in 
                                            ['income_statement', 'balance_sheet', 'cash_flow']):
                        
                        # Extract metadata from filename
                        filename = os.path.basename(file_path)
                        parts = filename.split('_')
                        
                        if len(parts) >= 4:
                            report_date = parts[3].replace('.htm', '')
                            filing_date = report_date  # TODO: Get actual filing date
                            accession_number = "unknown"  # TODO: Extract from file
                            
                            # Add filing to warehouse
                            filing_id = self.warehouse.add_filing(
                                ticker=ticker,
                                quarter=quarter,
                                year=year,
                                report_date=report_date,
                                filing_date=filing_date,
                                form_type="10-Q",
                                accession_number=accession_number,
                                source_file=file_path
                            )
                            
                            # Add financial data to warehouse
                            self.warehouse.add_financial_data(filing_id, financial_data)
                            
                            # Calculate and add KPIs
                            self.warehouse.add_kpis(filing_id, financial_data, ticker, year, quarter)
                            
                            logger.info(f"✅ Successfully stored {ticker} {year}Q{quarter} data in warehouse")
                        else:
                            logger.warning(f"⚠️ Could not parse filename: {filename}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Pipeline failed for {ticker} {year}Q{quarter}: {e}")
            return False
    
    def scrape_multiple_quarters(self, ticker: str, quarters: List[Dict[str, int]]) -> Dict[str, bool]:
        """
        Scrape multiple quarters for a company.
        
        Args:
            ticker (str): Stock ticker symbol
            quarters (List[Dict[str, int]]): List of quarter dictionaries with 'year' and 'quarter' keys
            
        Returns:
            Dict[str, bool]: Results for each quarter
        """
        results = {}
        
        for quarter_info in quarters:
            year = quarter_info['year']
            quarter = quarter_info['quarter']
            key = f"{year}Q{quarter}"
            
            logger.info(f"🔄 Processing {ticker} {key}")
            success = self.scrape_and_store_company_quarter(ticker, year, quarter)
            results[key] = success
        
        successful = sum(results.values())
        total = len(results)
        logger.info(f"📊 Completed {ticker} scraping: {successful}/{total} quarters successful")
        
        return results
    
    def get_company_analysis(self, ticker: str) -> Dict[str, Any]:
        """
        Get comprehensive analysis for a company.
        
        Args:
            ticker (str): Stock ticker symbol
            
        Returns:
            Dict[str, Any]: Analysis results
        """
        try:
            # Get all filings
            filings_df = self.warehouse.get_company_filings(ticker)
            
            # Get financial data
            financial_df = self.warehouse.get_financial_data(ticker)
            
            # Get quarterly comparisons for key metrics
            key_metrics = ['Revenue', 'Net Income', 'Total Assets', 'Total Liabilities']
            quarterly_data = {}
            
            for metric in key_metrics:
                comparison_df = self.warehouse.get_quarterly_comparison(ticker, metric, quarters=8)
                if not comparison_df.empty:
                    quarterly_data[metric] = comparison_df
            
            analysis = {
                'ticker': ticker,
                'total_filings': len(filings_df),
                'total_data_points': len(financial_df),
                'statement_types': financial_df['statement_type'].value_counts().to_dict() if not financial_df.empty else {},
                'quarters_available': sorted(filings_df[['year', 'quarter']].drop_duplicates().to_dict('records')) if not filings_df.empty else [],
                'quarterly_trends': quarterly_data,
                'latest_filing': filings_df.iloc[0].to_dict() if not filings_df.empty else None
            }
            
            logger.info(f"📊 Generated analysis for {ticker}: {analysis['total_filings']} filings, {analysis['total_data_points']} data points")
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Analysis failed for {ticker}: {e}")
            return {}
    
    def export_company_data(self, ticker: str, output_dir: str = "data/exports"):
        """
        Export all data for a company.
        
        Args:
            ticker (str): Stock ticker symbol
            output_dir (str): Output directory
        """
        try:
            self.warehouse.export_to_csv(ticker, output_dir)
            
            # Also export analysis
            analysis = self.get_company_analysis(ticker)
            analysis_file = Path(output_dir) / f"{ticker}_analysis.json"
            with open(analysis_file, 'w') as f:
                json.dump(analysis, f, indent=2, default=str)
            
            logger.info(f"📁 Exported all data for {ticker} to {output_dir}")
            
        except Exception as e:
            logger.error(f"❌ Export failed for {ticker}: {e}")


# Example usage
if __name__ == "__main__":
    # Initialize pipeline
    pipeline = ScrapingToWarehousePipeline()
    
    # Example: Scrape AAPL for multiple quarters
    aapl_quarters = [
        {'year': 2024, 'quarter': 2},
        {'year': 2024, 'quarter': 1},
        {'year': 2023, 'quarter': 4},
        {'year': 2023, 'quarter': 3}
    ]
    
    # Scrape and store data
    results = pipeline.scrape_multiple_quarters("AAPL", aapl_quarters)
    print(f"AAPL scraping results: {results}")
    
    # Get analysis
    analysis = pipeline.get_company_analysis("AAPL")
    print(f"AAPL analysis: {analysis}")
    
    # Export data
    pipeline.export_company_data("AAPL")
    
    # Get warehouse stats
    stats = pipeline.warehouse.get_database_stats()
    print(f"Warehouse stats: {stats}")
