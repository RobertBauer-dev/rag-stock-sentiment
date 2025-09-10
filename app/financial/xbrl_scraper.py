"""
XBRL-based Financial Data Scraper using SEC's structured data sets.
This is the most reliable approach as it uses pre-extracted structured data from SEC.
"""

import requests
import zipfile
import xml.etree.ElementTree as ET
import json
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import io

from app.core.logging import get_logger
from app.core.config import AppConfig
from app.core.exceptions import APIError, ProcessingError

logger = get_logger(__name__)


class XBRLFinancialScraper:
    """
    XBRL-based scraper that uses SEC's structured financial data sets.
    This is the most reliable approach as it uses pre-extracted structured data.
    """
    
    def __init__(self):
        """Initialize the XBRL Financial Scraper."""
        self.base_url = "https://www.sec.gov/Archives/edgar/data"
        self.headers = AppConfig.SEC_HEADERS
        self.xbrl_folder = AppConfig.FINANCIAL_DATA_DIR / "xbrl_data"
        self.xbrl_folder.mkdir(parents=True, exist_ok=True)
        logger.info(f"🏗️ Initialized XBRL Financial Scraper with folder: {self.xbrl_folder}")
    
    def get_cik_from_ticker(self, ticker: str) -> str:
        """
        Retrieves CIK (Central Index Key) for a given ticker symbol.
        
        Args:
            ticker (str): Stock ticker symbol (e.g., 'AAPL')
        
        Returns:
            str: 10-digit CIK string
        """
        logger.info(f"🔎 Looking up CIK for ticker: {ticker}")
        
        try:
            url = "https://www.sec.gov/files/company_tickers.json"
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            for _, entry in data.items():
                if entry["ticker"].upper() == ticker.upper():
                    cik = str(entry["cik_str"]).zfill(10)
                    logger.info(f"✅ Found CIK {cik} for ticker {ticker}")
                    return cik
            
            raise APIError(f"No CIK found for ticker {ticker}")
            
        except requests.RequestException as e:
            logger.error(f"❌ Failed to retrieve CIK data: {e}")
            raise APIError(f"Failed to retrieve CIK data: {e}")
    
    def find_xbrl_filing(self, ticker: str, year: int, quarter: int) -> Optional[Dict[str, Any]]:
        """
        Find XBRL filing for a specific ticker, year, and quarter.
        
        Args:
            ticker (str): Stock ticker symbol
            year (int): Year
            quarter (int): Quarter (1-4)
        
        Returns:
            Optional[Dict[str, Any]]: Filing information or None
        """
        logger.info(f"🔍 Finding XBRL filing for {ticker} {year}Q{quarter}")
        
        try:
            cik = self.get_cik_from_ticker(ticker)
            subs_url = f"https://data.sec.gov/submissions/CIK{cik}.json"
            
            response = requests.get(subs_url, headers=self.headers, timeout=30)
            response.raise_for_status()
            subs = response.json()
            
            filings = subs["filings"]["recent"]
            
            # Quarter months mapping
            quarter_months = {
                1: ["01", "02", "03"],
                2: ["04", "05", "06"],
                3: ["07", "08", "09"],
                4: ["10", "11", "12"]
            }
            
            target_months = quarter_months.get(quarter, [])
            if not target_months:
                logger.error(f"Invalid quarter: {quarter}")
                return None
            
            for i, form in enumerate(filings["form"]):
                if form == "10-Q":
                    report_date = filings["reportDate"][i]
                    filing_date = filings["filingDate"][i]
                    
                    if report_date.startswith(str(year)):
                        month = report_date[5:7]
                        if month in target_months:
                            accession = filings["accessionNumber"][i].replace("-", "")
                            
                            filing_info = {
                                "cik": cik,
                                "accession": accession,
                                "report_date": report_date,
                                "filing_date": filing_date,
                                "form_type": form
                            }
                            
                            logger.info(f"✅ Found XBRL filing: {accession}")
                            return filing_info
            
            logger.warning(f"No 10-Q filing found for {ticker} {year}Q{quarter}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error finding XBRL filing: {e}")
            raise ProcessingError(f"Error finding XBRL filing: {e}")
    
    def download_xbrl_data(self, filing_info: Dict[str, Any]) -> Optional[str]:
        """
        Download XBRL data for a filing.
        
        Args:
            filing_info (Dict[str, Any]): Filing information
            
        Returns:
            Optional[str]: Path to downloaded XBRL file or None
        """
        logger.info(f"📥 Downloading XBRL data for {filing_info['accession']}")
        
        try:
            cik = filing_info["cik"]
            accession = filing_info["accession"]
            
            # Try to find XBRL files
            xbrl_urls = [
                f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession}/{accession}-xbrl.zip",
                f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession}/xbrl.zip"
            ]
            
            for xbrl_url in xbrl_urls:
                try:
                    logger.debug(f"Trying XBRL URL: {xbrl_url}")
                    response = requests.get(xbrl_url, headers=self.headers, timeout=60)
                    
                    if response.status_code == 200:
                        # Save XBRL zip file
                        zip_filename = f"{filing_info['accession']}_xbrl.zip"
                        zip_path = self.xbrl_folder / zip_filename
                        
                        with open(zip_path, 'wb') as f:
                            f.write(response.content)
                        
                        logger.info(f"✅ Downloaded XBRL data to: {zip_path}")
                        return str(zip_path)
                    
                except requests.RequestException as e:
                    logger.debug(f"Failed to download from {xbrl_url}: {e}")
                    continue
            
            logger.warning(f"No XBRL data found for {accession}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error downloading XBRL data: {e}")
            raise ProcessingError(f"Error downloading XBRL data: {e}")
    
    def extract_financial_statements_xbrl(self, zip_path: str, ticker: str) -> Dict[str, Any]:
        """
        Extract financial statements from XBRL zip file.
        
        Args:
            zip_path (str): Path to XBRL zip file
            ticker (str): Stock ticker symbol
            
        Returns:
            Dict[str, Any]: Extracted financial data
        """
        logger.info(f"📊 Extracting financial statements from XBRL: {zip_path}")
        
        try:
            financial_data = {
                'income_statement': {},
                'balance_sheet': {},
                'cash_flow': {},
                'metadata': {
                    'company_name': ticker,
                    'extraction_method': 'xbrl',
                    'source_file': zip_path
                }
            }
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # List all files in the zip
                file_list = zip_ref.namelist()
                logger.debug(f"XBRL files: {file_list}")
                
                # Look for instance document
                instance_files = [f for f in file_list if f.endswith('.xml') and 'instance' in f.lower()]
                
                if not instance_files:
                    # Fallback: look for any XML file
                    instance_files = [f for f in file_list if f.endswith('.xml')]
                
                if not instance_files:
                    logger.warning("No XML instance files found in XBRL zip")
                    return financial_data
                
                # Process the first instance file
                instance_file = instance_files[0]
                logger.info(f"Processing XBRL instance file: {instance_file}")
                
                with zip_ref.open(instance_file) as xml_file:
                    content = xml_file.read()
                    financial_data = self._parse_xbrl_xml(content, ticker)
            
            logger.info(f"✅ XBRL extraction complete - Income: {len(financial_data.get('income_statement', {}))} items, "
                       f"Balance: {len(financial_data.get('balance_sheet', {}))} items, "
                       f"Cash Flow: {len(financial_data.get('cash_flow', {}))} items")
            
            return financial_data
            
        except Exception as e:
            logger.error(f"❌ Error extracting XBRL data: {e}")
            raise ProcessingError(f"Error extracting XBRL data: {e}")
    
    def _parse_xbrl_xml(self, xml_content: bytes, ticker: str) -> Dict[str, Any]:
        """
        Parse XBRL XML content to extract financial statements.
        
        Args:
            xml_content (bytes): XBRL XML content
            ticker (str): Stock ticker symbol
            
        Returns:
            Dict[str, Any]: Parsed financial data
        """
        try:
            # Parse XML
            root = ET.fromstring(xml_content)
            
            # Define namespaces
            namespaces = {
                'xbrli': 'http://www.xbrl.org/2003/instance',
                'us-gaap': 'http://fasb.org/us-gaap/2023-01-31',
                'dei': 'http://xbrl.sec.gov/dei/2023-01-31'
            }
            
            financial_data = {
                'income_statement': {},
                'balance_sheet': {},
                'cash_flow': {},
                'metadata': {
                    'company_name': ticker,
                    'extraction_method': 'xbrl_xml',
                    'periods': []
                }
            }
            
            # Extract all facts (financial data points)
            facts = root.findall('.//xbrli:fact', namespaces)
            
            for fact in facts:
                # Get the concept name
                concept_elem = fact.find('xbrli:concept', namespaces)
                if concept_elem is not None:
                    concept_name = concept_elem.text
                    
                    # Get the value
                    value_elem = fact.find('xbrli:value', namespaces)
                    if value_elem is not None:
                        try:
                            value = float(value_elem.text)
                            
                            # Categorize based on concept name
                            if self._is_income_statement_item(concept_name):
                                financial_data['income_statement'][concept_name] = [value]
                            elif self._is_balance_sheet_item(concept_name):
                                financial_data['balance_sheet'][concept_name] = [value]
                            elif self._is_cash_flow_item(concept_name):
                                financial_data['cash_flow'][concept_name] = [value]
                                
                        except ValueError:
                            # Skip non-numeric values
                            continue
            
            logger.info(f"📊 Parsed {len(financial_data['income_statement']) + len(financial_data['balance_sheet']) + len(financial_data['cash_flow'])} financial items")
            
            return financial_data
            
        except ET.ParseError as e:
            logger.error(f"❌ XML parsing error: {e}")
            return {
                'income_statement': {},
                'balance_sheet': {},
                'cash_flow': {},
                'metadata': {'error': f'XML parsing error: {e}'}
            }
    
    def _is_income_statement_item(self, concept_name: str) -> bool:
        """Check if concept is an income statement item."""
        income_keywords = [
            'revenue', 'sales', 'income', 'earnings', 'profit', 'expense',
            'cost', 'operating', 'gross', 'net', 'ebitda'
        ]
        return any(keyword in concept_name.lower() for keyword in income_keywords)
    
    def _is_balance_sheet_item(self, concept_name: str) -> bool:
        """Check if concept is a balance sheet item."""
        balance_keywords = [
            'asset', 'liability', 'equity', 'debt', 'cash', 'inventory',
            'receivable', 'payable', 'stock', 'share'
        ]
        return any(keyword in concept_name.lower() for keyword in balance_keywords)
    
    def _is_cash_flow_item(self, concept_name: str) -> bool:
        """Check if concept is a cash flow item."""
        cashflow_keywords = [
            'cash', 'flow', 'operating', 'investing', 'financing',
            'depreciation', 'amortization'
        ]
        return any(keyword in concept_name.lower() for keyword in cashflow_keywords)
    
    def scrape_quarterly_data(self, ticker: str, year: int, quarter: int) -> Dict[str, Any]:
        """
        Complete pipeline: find, download, and extract XBRL data.
        
        Args:
            ticker (str): Stock ticker symbol
            year (int): Year
            quarter (int): Quarter (1-4)
        
        Returns:
            Dict[str, Any]: Extracted financial data
        """
        logger.info(f"🚀 Starting XBRL scraping for {ticker} {year}Q{quarter}")
        
        try:
            # Find filing
            filing_info = self.find_xbrl_filing(ticker, year, quarter)
            if not filing_info:
                logger.warning(f"No XBRL filing found for {ticker} {year}Q{quarter}")
                return {}
            
            # Download XBRL data
            zip_path = self.download_xbrl_data(filing_info)
            if not zip_path:
                logger.warning(f"No XBRL data downloaded for {ticker} {year}Q{quarter}")
                return {}
            
            # Extract financial statements
            financial_data = self.extract_financial_statements_xbrl(zip_path, ticker)
            
            logger.info(f"✅ XBRL scraping completed for {ticker} {year}Q{quarter}")
            return financial_data
            
        except Exception as e:
            logger.error(f"❌ XBRL scraping failed for {ticker} {year}Q{quarter}: {e}")
            raise ProcessingError(f"XBRL scraping failed for {ticker} {year}Q{quarter}: {e}")


# Backward compatibility functions
def scrape_quarterly_data_xbrl(ticker: str, year: int, quarter: int) -> Dict[str, Any]:
    """Backward compatibility function."""
    scraper = XBRLFinancialScraper()
    return scraper.scrape_quarterly_data(ticker, year, quarter)
