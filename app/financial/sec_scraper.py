"""
SEC 10-Q Document Scraper.
Refactored from scrape_quarterlies.py with improved structure and centralized logging.
"""

import requests
import os
import json
from datetime import datetime
import re
from typing import Optional, List, Dict, Any
from bs4 import BeautifulSoup

from app.core.logging import get_logger
from app.core.config import AppConfig
from app.core.exceptions import APIError, DataCollectionError

logger = get_logger(__name__)


class SECScraper:
    """
    SEC 10-Q Document Scraper with improved error handling and structure.
    """
    
    def __init__(self):
        """Initialize the SEC scraper."""
        self.headers = AppConfig.SEC_HEADERS
        self.report_folder = AppConfig.SEC_REPORTS_DIR
        self.report_folder.mkdir(parents=True, exist_ok=True)
        logger.info(f"🏗️ Initialized SEC Scraper with report folder: {self.report_folder}")
    
    def get_cik_from_ticker(self, ticker: str) -> str:
        """
        Retrieves CIK (Central Index Key) for a given ticker symbol.
        
        Args:
            ticker (str): Stock ticker symbol (e.g., 'AAPL')
        
        Returns:
            str: 10-digit CIK string
        
        Raises:
            APIError: If ticker is not found or API request fails
        """
        logger.info(f"Looking up CIK for ticker: {ticker}")
        
        try:
            url = "https://www.sec.gov/files/company_tickers.json"
            logger.debug(f"Making request to: {url}")
            
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            logger.debug(f"Retrieved {len(data)} company entries from SEC")
                
            for _, entry in data.items():
                if entry["ticker"].upper() == ticker.upper():
                    cik = str(entry["cik_str"]).zfill(10)  # SEC braucht 10-stellig
                    logger.info(f"Found CIK {cik} for ticker {ticker}")
                    return cik
                
            logger.error(f"No CIK found for ticker {ticker}")
            raise APIError(f"No CIK found for ticker {ticker}")

        except requests.RequestException as e:
            logger.error(f"Failed to retrieve CIK data: {e}")
            raise APIError(f"Failed to retrieve CIK data: {e}")
        except Exception as e:
            logger.error(f"Unexpected error while looking up CIK for {ticker}: {e}")
            raise APIError(f"Unexpected error while looking up CIK for {ticker}: {e}")

    def list_filing_documents(self, ticker: str, year: int, quarter: int) -> List[Dict[str, Any]]:
        """
        Listet alle verfügbaren Dokumente in einem 10-Q Filing auf.
        
        Args:
            ticker (str): Aktiensymbol
            year (int): Jahr
            quarter (int): Quartal
        
        Returns:
            List[Dict[str, Any]]: Liste der verfügbaren Dokumente
        """
        logger.info(f"Listing filing documents for {ticker} {year}Q{quarter}")
        
        try:
            cik = self.get_cik_from_ticker(ticker)
            subs_url = f"https://data.sec.gov/submissions/CIK{cik}.json"
            logger.debug(f"Fetching submissions from: {subs_url}")
            
            response = requests.get(subs_url, headers=self.headers, timeout=30)
            response.raise_for_status()
            subs = response.json()

            filings = subs["filings"]["recent"]
            logger.debug(f"Found {len(filings['form'])} recent filings")
            
            quarter_months = {
                1: ["01", "02", "03"],
                2: ["04", "05", "06"],
                3: ["07", "08", "09"],
                4: ["10", "11", "12"]
            }
            
            target_months = quarter_months.get(quarter, [])
            if not target_months:
                logger.error(f"Invalid quarter: {quarter}")
                return []
            
            logger.debug(f"Looking for 10-Q filings in months: {target_months}")
            
            for i, form in enumerate(filings["form"]):
                if form == "10-Q":
                    report_date = filings["reportDate"][i]
                    logger.debug(f"Found 10-Q filing with report date: {report_date}")
                    
                    if report_date.startswith(str(year)):
                        month = report_date[5:7]
                        if month in target_months:
                            accession = filings["accessionNumber"][i].replace("-", "")
                            filing_index_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession}/index.json"
                            
                            logger.debug(f"Fetching filing index from: {filing_index_url}")
                            filing_response = requests.get(filing_index_url, headers=self.headers, timeout=30)
                            filing_response.raise_for_status()
                            filing_index = filing_response.json()
                            
                            documents = filing_index["directory"]["item"]
                            logger.info(f"Found {len(documents)} documents for {ticker} {year}Q{quarter}")
                            
                            print(f"📋 Available documents for {ticker} {year}Q{quarter}:")
                            for item in documents:
                                print(f"   - {item['name']}")
                                logger.debug(f"Document: {item['name']}")
                            
                            return documents
            
            logger.warning(f"No 10-Q filings found for {ticker} {year}Q{quarter}")
            return []
            
        except requests.RequestException as e:
            logger.error(f"Failed to retrieve filing documents: {e}")
            raise APIError(f"Failed to retrieve filing documents: {e}")
        except Exception as e:
            logger.error(f"Unexpected error while listing documents: {e}")
            raise DataCollectionError(f"Unexpected error while listing documents: {e}")

    def fetch_10q_by_quarter(self, ticker: str, year: int, quarter: int) -> Optional[str]:
        """
        Lädt ein 10-Q Dokument für ein spezifisches Jahr und Quartal herunter.
        
        Args:
            ticker (str): Aktiensymbol (z.B. 'AAPL')
            year (int): Jahr (z.B. 2024)
            quarter (int): Quartal (1, 2, 3, oder 4)
        
        Returns:
            Optional[str]: Pfad zur heruntergeladenen Datei oder None wenn nicht gefunden
        """
        logger.info(f"Fetching 10-Q for {ticker} {year}Q{quarter}")
        
        try:
            cik = self.get_cik_from_ticker(ticker)
            subs_url = f"https://data.sec.gov/submissions/CIK{cik}.json"
            logger.debug(f"Fetching submissions from: {subs_url}")
            
            response = requests.get(subs_url, headers=self.headers, timeout=30)
            response.raise_for_status()
            subs = response.json()

            filings = subs["filings"]["recent"]
            logger.debug(f"Found {len(filings['form'])} recent filings")
            
            # Erwartete Quartalsdaten basierend auf dem Jahr
            quarter_months = {
                1: ["01", "02", "03"],  # Q1: Jan, Feb, Mar
                2: ["04", "05", "06"],  # Q2: Apr, May, Jun
                3: ["07", "08", "09"],  # Q3: Jul, Aug, Sep
                4: ["10", "11", "12"]   # Q4: Oct, Nov, Dec
            }
            
            target_months = quarter_months.get(quarter, [])
            if not target_months:
                error_msg = f"Ungültiges Quartal: {quarter}. Muss 1, 2, 3 oder 4 sein."
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            logger.debug(f"Looking for 10-Q filings in months: {target_months}")
            
            for i, form in enumerate(filings["form"]):
                if form == "10-Q":
                    report_date = filings["reportDate"][i]
                    filing_date = filings["filingDate"][i]
                    logger.debug(f"Found 10-Q filing: report_date={report_date}, filing_date={filing_date}")
                    
                    # Prüfe ob das Datum im gewünschten Quartal liegt
                    if report_date.startswith(str(year)):
                        month = report_date[5:7]  # Extrahiere Monat (YYYY-MM-DD)
                        if month in target_months:
                            accession = filings["accessionNumber"][i].replace("-", "")
                            filing_index_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession}/index.json"
                            
                            logger.debug(f"Fetching filing index from: {filing_index_url}")
                            filing_response = requests.get(filing_index_url, headers=self.headers, timeout=30)
                            filing_response.raise_for_status()
                            filing_index = filing_response.json()
                            
                            # Priorisiere die besten Dokumente für Financial Statements
                            priority_docs = []
                            other_docs = []
                            
                            for item in filing_index["directory"]["item"]:
                                if item["name"].endswith(".htm"):
                                    # Höchste Priorität: Hauptdokument mit Ticker-Datum
                                    if item["name"].startswith(ticker.lower()) and report_date.replace("-", "") in item["name"]:
                                        priority_docs.insert(0, item)  # An den Anfang
                                    # Hohe Priorität: R3.htm (Financial Statements)
                                    elif item["name"] == "R3.htm":
                                        priority_docs.append(item)
                                    # Hohe Priorität: R14-R20 (Income Statement, Balance Sheet, Cash Flow)
                                    elif item["name"].startswith("R") and item["name"][1:3].isdigit():
                                        r_num = int(item["name"][1:3])
                                        if 14 <= r_num <= 20:
                                            priority_docs.append(item)
                                    # Mittlere Priorität: 10-q im Namen
                                    elif "10-q" in item["name"].lower():
                                        other_docs.insert(0, item)
                                    # Fallback: alle anderen .htm Dateien
                                    else:
                                        other_docs.append(item)
                            
                            # Versuche zuerst die priorisierten Dokumente
                            for item in priority_docs + other_docs:
                                doc_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession}/{item['name']}"
                                logger.info(f"Found priority document: {item['name']}")
                                
                                # Datei speichern mit Quartalsinformation
                                filename = f"{ticker}_10Q_{year}Q{quarter}_{report_date}_{item['name']}"
                                file_path = self.report_folder / filename
                                
                                logger.debug(f"Downloading document from: {doc_url}")
                                doc_response = requests.get(doc_url, headers=self.headers, timeout=60)
                                doc_response.raise_for_status()
                                content = doc_response.text
                                
                                with open(file_path, "w", encoding="utf-8") as f:
                                    f.write(content)
                                
                                logger.info(f"Successfully saved {ticker} 10-Q {year}Q{quarter} to {file_path}")
                                print(f"✅ Saved {ticker} 10-Q {year}Q{quarter} to {file_path}")
                                print(f"   Report Date: {report_date}, Filing Date: {filing_date}")
                                return str(file_path)
            
            logger.warning(f"No 10-Q filing found for {ticker} {year}Q{quarter}")
            return None
            
        except requests.RequestException as e:
            logger.error(f"Network error while fetching 10-Q for {ticker} {year}Q{quarter}: {e}")
            raise APIError(f"Network error while fetching 10-Q for {ticker} {year}Q{quarter}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error while fetching 10-Q for {ticker} {year}Q{quarter}: {e}")
            raise DataCollectionError(f"Unexpected error while fetching 10-Q for {ticker} {year}Q{quarter}: {e}")

    def fetch_all_financial_documents(self, ticker: str, year: int, quarter: int) -> List[str]:
        """
        Lädt alle wichtigen Financial Statement Dokumente für ein spezifisches Jahr und Quartal herunter.
        
        Args:
            ticker (str): Aktiensymbol (z.B. 'AAPL')
            year (int): Jahr (z.B. 2024)
            quarter (int): Quartal (1, 2, 3, oder 4)
        
        Returns:
            List[str]: Liste der Pfade zu den heruntergeladenen Dateien
        """
        logger.info(f"Fetching all financial documents for {ticker} {year}Q{quarter}")
        
        try:
            cik = self.get_cik_from_ticker(ticker)
            subs_url = f"https://data.sec.gov/submissions/CIK{cik}.json"
            logger.debug(f"Fetching submissions from: {subs_url}")
            
            response = requests.get(subs_url, headers=self.headers, timeout=30)
            response.raise_for_status()
            subs = response.json()

            filings = subs["filings"]["recent"]
            logger.debug(f"Found {len(filings['form'])} recent filings")
            
            # Erwartete Quartalsdaten basierend auf dem Jahr
            quarter_months = {
                1: ["01", "02", "03"],  # Q1: Jan, Feb, Mar
                2: ["04", "05", "06"],  # Q2: Apr, May, Jun
                3: ["07", "08", "09"],  # Q3: Jul, Aug, Sep
                4: ["10", "11", "12"]   # Q4: Oct, Nov, Dec
            }
            
            target_months = quarter_months.get(quarter, [])
            if not target_months:
                error_msg = f"Ungültiges Quartal: {quarter}. Muss 1, 2, 3 oder 4 sein."
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            logger.debug(f"Looking for 10-Q filings in months: {target_months}")
            
            for i, form in enumerate(filings["form"]):
                if form == "10-Q":
                    report_date = filings["reportDate"][i]
                    filing_date = filings["filingDate"][i]
                    logger.debug(f"Found 10-Q filing: report_date={report_date}, filing_date={filing_date}")
                    
                    # Prüfe ob das Datum im gewünschten Quartal liegt
                    if report_date.startswith(str(year)):
                        month = report_date[5:7]  # Extrahiere Monat (YYYY-MM-DD)
                        if month in target_months:
                            accession = filings["accessionNumber"][i].replace("-", "")
                            filing_index_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession}/index.json"
                            
                            logger.debug(f"Fetching filing index from: {filing_index_url}")
                            filing_response = requests.get(filing_index_url, headers=self.headers, timeout=30)
                            filing_response.raise_for_status()
                            filing_index = filing_response.json()
                            
                            # Definiere die wichtigsten Financial Statement Dokumente
                            priority_docs = [
                                # Hauptdokument
                                f"{ticker.lower()}-{report_date.replace('-', '')}.htm",
                                # Financial Statements Abschnitte
                                "R3.htm",  # Part I, Item 1 (Financial Statements)
                                "R14.htm", "R15.htm", "R16.htm", "R17.htm", "R18.htm", "R19.htm", "R20.htm",  # Income Statement, Balance Sheet, Cash Flow
                                # Excel Report
                                "Financial_Report.xlsx"
                            ]
                            
                            downloaded_files = []
                            
                            # Lade alle wichtigen Dokumente herunter
                            for doc_name in priority_docs:
                                for item in filing_index["directory"]["item"]:
                                    if item["name"] == doc_name:
                                        doc_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession}/{item['name']}"
                                        logger.info(f"Downloading financial document: {item['name']}")
                                        
                                        # Datei speichern
                                        filename = f"{ticker}_10Q_{year}Q{quarter}_{report_date}_{item['name']}"
                                        file_path = self.report_folder / filename
                                        
                                        logger.debug(f"Downloading from: {doc_url}")
                                        doc_response = requests.get(doc_url, headers=self.headers, timeout=60)
                                        doc_response.raise_for_status()
                                        content = doc_response.text if item["name"].endswith('.htm') else doc_response.content
                                        
                                        mode = "w" if item["name"].endswith('.htm') else "wb"
                                        encoding = "utf-8" if item["name"].endswith('.htm') else None
                                        
                                        with open(file_path, mode, encoding=encoding) as f:
                                            f.write(content)
                                        
                                        downloaded_files.append(str(file_path))
                                        logger.info(f"Successfully saved {item['name']} to {file_path}")
                                        print(f"✅ Downloaded {item['name']}")
                                        break
                            
                            if downloaded_files:
                                logger.info(f"Successfully downloaded {len(downloaded_files)} financial documents")
                                print(f"📊 Downloaded {len(downloaded_files)} financial documents for {ticker} {year}Q{quarter}")
                                return downloaded_files
                            else:
                                logger.warning(f"No priority financial documents found for {ticker} {year}Q{quarter}")
                                return []
            
            logger.warning(f"No 10-Q filing found for {ticker} {year}Q{quarter}")
            return []
            
        except requests.RequestException as e:
            logger.error(f"Network error while fetching financial documents for {ticker} {year}Q{quarter}: {e}")
            raise APIError(f"Network error while fetching financial documents for {ticker} {year}Q{quarter}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error while fetching financial documents for {ticker} {year}Q{quarter}: {e}")
            raise DataCollectionError(f"Unexpected error while fetching financial documents for {ticker} {year}Q{quarter}: {e}")


# Backward compatibility functions
def get_cik_from_ticker(ticker: str) -> str:
    """Backward compatibility function."""
    scraper = SECScraper()
    return scraper.get_cik_from_ticker(ticker)


def fetch_10q_by_quarter(ticker: str, year: int, quarter: int) -> Optional[str]:
    """Backward compatibility function."""
    scraper = SECScraper()
    return scraper.fetch_10q_by_quarter(ticker, year, quarter)


def fetch_all_financial_documents(ticker: str, year: int, quarter: int) -> List[str]:
    """Backward compatibility function."""
    scraper = SECScraper()
    return scraper.fetch_all_financial_documents(ticker, year, quarter)


def list_filing_documents(ticker: str, year: int, quarter: int) -> List[Dict[str, Any]]:
    """Backward compatibility function."""
    scraper = SECScraper()
    return scraper.list_filing_documents(ticker, year, quarter)
