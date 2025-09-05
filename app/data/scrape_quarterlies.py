from pathlib import Path
import requests
import os
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re
import logging
from typing import Optional, List, Dict, Any
import colorama
from colorama import Fore, Back, Style


ROOT_FOLDER = Path(__file__).resolve().parent.parent.parent
REPORT_FOLDER = ROOT_FOLDER / "data" / "10q_reports"
os.makedirs(REPORT_FOLDER, exist_ok=True)

# SEC verlangt Identifikation
HEADERS = {"User-Agent": "Dr. Robert Bauer dr.robert.bauer@icloud.com"}

# Initialize colorama for colored output
colorama.init(autoreset=True)

# Custom colored formatter for console output
class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for different log levels."""
    
    # Color mapping for different log levels
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Style.BRIGHT,
    }
    
    def format(self, record):
        # Get the original formatted message
        log_message = super().format(record)
        
        # Add color based on log level
        color = self.COLORS.get(record.levelname, '')
        if color:
            # Color the entire message
            colored_message = f"{color}{log_message}{Style.RESET_ALL}"
            return colored_message
        
        return log_message

# Logging Setup
def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None) -> logging.Logger:
    """
    Setup logging configuration for the script.
    
    Args:
        log_level (str): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file (str, optional): Path to log file. If None, logs only to console.
    
    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logger
    logger = logging.getLogger('scrape_quarterlies')
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Create formatters
    colored_formatter = ColoredFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    plain_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler with colored output
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_handler.setFormatter(colored_formatter)
    logger.addHandler(console_handler)
    
    # File handler (if specified) - use plain formatter for file
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)  # Always log everything to file
        file_handler.setFormatter(plain_formatter)
        logger.addHandler(file_handler)
    
    return logger

# Initialize logger
logger = setup_logging(
    log_level="INFO",
    log_file=str(REPORT_FOLDER / "scrape_quarterlies.log")
)

def get_cik_from_ticker(ticker: str) -> str:
    """
    Retrieves CIK (Central Index Key) for a given ticker symbol.
    
    Args:
        ticker (str): Stock ticker symbol (e.g., 'AAPL')
    
    Returns:
        str: 10-digit CIK string
    
    Raises:
        ValueError: If ticker is not found
        requests.RequestException: If API request fails
    """
    logger.info(f"Looking up CIK for ticker: {ticker}")
    
    try:
    url = "https://www.sec.gov/files/company_tickers.json"
        logger.debug(f"Making request to: {url}")
        
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        logger.debug(f"Retrieved {len(data)} company entries from SEC")
        
    for _, entry in data.items():
        if entry["ticker"].upper() == ticker.upper():
                cik = str(entry["cik_str"]).zfill(10)  # SEC braucht 10-stellig
                logger.info(f"Found CIK {cik} for ticker {ticker}")
                return cik
        
        logger.error(f"No CIK found for ticker {ticker}")
    raise ValueError(f"No CIK found for ticker {ticker}")

    except requests.RequestException as e:
        logger.error(f"Failed to retrieve CIK data: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error while looking up CIK for {ticker}: {e}")
        raise


def list_filing_documents(ticker: str, year: int, quarter: int) -> List[Dict[str, Any]]:
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
        cik = get_cik_from_ticker(ticker)
        subs_url = f"https://data.sec.gov/submissions/CIK{cik}.json"
        logger.debug(f"Fetching submissions from: {subs_url}")
        
        response = requests.get(subs_url, headers=HEADERS, timeout=30)
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
                        filing_response = requests.get(filing_index_url, headers=HEADERS, timeout=30)
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
        return []
    except Exception as e:
        logger.error(f"Unexpected error while listing documents: {e}")
        return []





def fetch_10q_by_quarter(ticker: str, year: int, quarter: int) -> Optional[str]:
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
        cik = get_cik_from_ticker(ticker)
        subs_url = f"https://data.sec.gov/submissions/CIK{cik}.json"
        logger.debug(f"Fetching submissions from: {subs_url}")
        
        response = requests.get(subs_url, headers=HEADERS, timeout=30)
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
                        filing_response = requests.get(filing_index_url, headers=HEADERS, timeout=30)
                        filing_response.raise_for_status()
                        filing_index = filing_response.json()
                        
                        # Suche Hauptdokument (oft endet auf .htm und enthält "10-q" im Namen)
                        for item in filing_index["directory"]["item"]:
                            if item["name"].endswith(".htm") and "10-q" in item["name"].lower():
                                doc_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession}/{item['name']}"
                                logger.info(f"Found main 10-Q document: {item['name']}")
                                
                                # Datei speichern mit Quartalsinformation
                                filename = f"{ticker}_10Q_{year}Q{quarter}_{report_date}.html"
                                file_path = os.path.join(REPORT_FOLDER, filename)
                                
                                logger.debug(f"Downloading document from: {doc_url}")
                                doc_response = requests.get(doc_url, headers=HEADERS, timeout=60)
                                doc_response.raise_for_status()
                                content = doc_response.text
                                
                                with open(file_path, "w", encoding="utf-8") as f:
                                    f.write(content)
                                
                                logger.info(f"Successfully saved {ticker} 10-Q {year}Q{quarter} to {file_path}")
                                print(f"✅ Saved {ticker} 10-Q {year}Q{quarter} to {file_path}")
                                print(f"   Report Date: {report_date}, Filing Date: {filing_date}")
                                return file_path
                        
                        # Falls kein 10-q Dokument gefunden, nimm das erste .htm Dokument
                        logger.warning("No main 10-Q document found, trying first .htm document")
                        for item in filing_index["directory"]["item"]:
                            if item["name"].endswith(".htm"):
                                doc_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession}/{item['name']}"
                                logger.info(f"Using fallback document: {item['name']}")
                                
                                # Datei speichern mit Quartalsinformation
                                filename = f"{ticker}_10Q_{year}Q{quarter}_{report_date}.html"
                                file_path = os.path.join(REPORT_FOLDER, filename)
                                
                                logger.debug(f"Downloading fallback document from: {doc_url}")
                                doc_response = requests.get(doc_url, headers=HEADERS, timeout=60)
                                doc_response.raise_for_status()
                                content = doc_response.text
                                
                                with open(file_path, "w", encoding="utf-8") as f:
                                    f.write(content)
                                
                                logger.info(f"Successfully saved {ticker} 10-Q {year}Q{quarter} to {file_path}")
                                print(f"✅ Saved {ticker} 10-Q {year}Q{quarter} to {file_path}")
                                print(f"   Report Date: {report_date}, Filing Date: {filing_date}")
                                return file_path
        
        logger.warning(f"No 10-Q filing found for {ticker} {year}Q{quarter}")
        return None
        
    except requests.RequestException as e:
        logger.error(f"Network error while fetching 10-Q for {ticker} {year}Q{quarter}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error while fetching 10-Q for {ticker} {year}Q{quarter}: {e}")
        return None


def fetch_latest_10q(ticker):
    """
    Lädt das neueste 10-Q Dokument herunter (für Rückwärtskompatibilität).
    """
    cik = get_cik_from_ticker(ticker)
    subs_url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    subs = requests.get(subs_url, headers=HEADERS).json()

    filings = subs["filings"]["recent"]
    for i, form in enumerate(filings["form"]):
        if form == "10-Q":
            accession = filings["accessionNumber"][i].replace("-", "")
            filing_index_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession}/index.json"
            filing_index = requests.get(filing_index_url, headers=HEADERS).json()
            
            # suche Hauptdokument (oft endet auf .htm)
            for item in filing_index["directory"]["item"]:
                if item["name"].endswith(".htm"):
                    doc_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession}/{item['name']}"
                    
                    # Datei speichern
                    file_path = os.path.join(REPORT_FOLDER, f"{ticker}_10Q_latest.html")
                    content = requests.get(doc_url, headers=HEADERS).text
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(content)
                    
                    print(f"✅ Saved latest {ticker} 10-Q to {file_path}")
                    return file_path
    return None


def extract_financial_statements(file_path: str) -> Dict[str, Any]:
    """
    Extrahiert Financial Statements aus einem 10-Q HTML Dokument.
    
    Args:
        file_path (str): Pfad zur HTML-Datei
    
    Returns:
        Dict[str, Any]: Dictionary mit extrahierten Financial Statements
    """
    logger.info(f"Extracting financial statements from: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        logger.debug(f"File size: {len(content)} characters")
        soup = BeautifulSoup(content, 'html.parser')
        
        # Dictionary für die extrahierten Daten
        financial_data = {
            'income_statement': {},
            'balance_sheet': {},
            'cash_flow': {},
            'metadata': {}
        }
        
        # Extrahiere Metadaten
        try:
            # Suche nach Firmenname
            company_name = soup.find('span', {'class': 'companyName'})
            if company_name:
                financial_data['metadata']['company_name'] = company_name.get_text().strip()
                logger.debug(f"Found company name: {financial_data['metadata']['company_name']}")
            
            # Suche nach Periodeninformationen
            period_elements = soup.find_all('td', string=re.compile(r'Three Months Ended|Nine Months Ended'))
            if period_elements:
                financial_data['metadata']['periods'] = [elem.get_text().strip() for elem in period_elements]
                logger.debug(f"Found periods: {financial_data['metadata']['periods']}")
        except Exception as e:
            logger.warning(f"Error extracting metadata: {e}")
        
        # Suche nach Financial Statements Tabellen
        tables = soup.find_all('table')
        logger.debug(f"Found {len(tables)} tables in document")
        
        for i, table in enumerate(tables):
            table_text = table.get_text().lower()
            logger.debug(f"Table {i+1} text preview: {table_text[:100]}...")
            
            # Suche nach Income Statement
            if any(keyword in table_text for keyword in ['revenue', 'sales', 'income', 'earnings']):
                logger.info(f"Found income statement in table {i+1}")
                financial_data['income_statement'] = extract_table_data(table, 'income_statement')
            
            # Suche nach Balance Sheet
            elif any(keyword in table_text for keyword in ['assets', 'liabilities', 'equity', 'balance']):
                logger.info(f"Found balance sheet in table {i+1}")
                financial_data['balance_sheet'] = extract_table_data(table, 'balance_sheet')
            
            # Suche nach Cash Flow
            elif any(keyword in table_text for keyword in ['cash flow', 'operating activities', 'investing activities']):
                logger.info(f"Found cash flow statement in table {i+1}")
                financial_data['cash_flow'] = extract_table_data(table, 'cash_flow')
        
        logger.info(f"Extraction complete - Income: {len(financial_data['income_statement'])} items, "
                   f"Balance: {len(financial_data['balance_sheet'])} items, "
                   f"Cash Flow: {len(financial_data['cash_flow'])} items")
        
        return financial_data
        
    except Exception as e:
        logger.error(f"Error extracting financial statements from {file_path}: {e}")
            return {
            'income_statement': {},
            'balance_sheet': {},
            'cash_flow': {},
            'metadata': {'error': str(e)}
        }

def extract_table_data(table, statement_type: str) -> Dict[str, Any]:
    """
    Extrahiert Daten aus einer Financial Statement Tabelle.
    
    Args:
        table: BeautifulSoup table element
        statement_type (str): Typ des Statements
    
    Returns:
        Dict[str, Any]: Extrahierte Tabellendaten
    """
    logger.debug(f"Extracting data from {statement_type} table")
    data = {}
    
    try:
        rows = table.find_all('tr')
        logger.debug(f"Found {len(rows)} rows in {statement_type} table")
        
        for i, row in enumerate(rows):
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 2:
                # Erste Zelle ist normalerweise der Kontoname
                account_name = cells[0].get_text().strip()
                
                # Entferne überflüssige Zeichen
                account_name = re.sub(r'[^\w\s\-&]', '', account_name)
                account_name = re.sub(r'\s+', ' ', account_name).strip()
                
                if account_name and len(account_name) > 2:  # Ignoriere sehr kurze Namen
                    values = []
                    
                    # Extrahiere Werte aus den anderen Zellen
                    for cell in cells[1:]:
                        cell_text = cell.get_text().strip()
                        # Entferne Klammern (negative Werte) und konvertiere zu Zahlen
                        if cell_text:
                            # Entferne Klammern und konvertiere zu negativen Zahlen
                            if '(' in cell_text and ')' in cell_text:
                                cell_text = '-' + cell_text.replace('(', '').replace(')', '')
                            
                            # Entferne Kommas und andere Formatierungszeichen
                            cell_text = re.sub(r'[,$]', '', cell_text)
                            
                            # Versuche zu konvertieren
                            try:
                                if cell_text.replace('-', '').replace('.', '').isdigit():
                                    values.append(float(cell_text))
                                else:
                                    values.append(cell_text)
                            except ValueError:
                                values.append(cell_text)
                    
                    if values:
                        data[account_name] = values
                        logger.debug(f"Extracted {account_name}: {values}")
        
        logger.info(f"Successfully extracted {len(data)} items from {statement_type}")
                        
    except Exception as e:
        logger.error(f"Error extracting data from {statement_type} table: {e}")
    
    return data


def save_financial_data_to_json(financial_data: Dict[str, Any], output_path: str) -> None:
    """
    Speichert die extrahierten Financial Data als JSON.
    
    Args:
        financial_data (Dict[str, Any]): Die extrahierten Daten
        output_path (str): Pfad für die JSON-Datei
    """
    logger.info(f"Saving financial data to: {output_path}")
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(financial_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Successfully saved financial data to {output_path}")
        print(f"✅ Financial data saved to {output_path}")
        
    except Exception as e:
        logger.error(f"Error saving financial data to {output_path}: {e}")
        raise


def process_10q_file(file_path: str) -> Dict[str, Any]:
    """
    Verarbeitet eine 10-Q Datei und extrahiert Financial Statements.
    
    Args:
        file_path (str): Pfad zur 10-Q HTML-Datei
    
    Returns:
        Dict[str, Any]: Extrahierte Financial Data
    """
    logger.info(f"Processing 10-Q file: {file_path}")
    print(f"📊 Processing 10-Q file: {file_path}")
    
    try:
        # Extrahiere Financial Statements
        financial_data = extract_financial_statements(file_path)
        
        # Erstelle JSON-Datei
        json_path = file_path.replace('.html', '_financial_data.json')
        save_financial_data_to_json(financial_data, json_path)
        
        logger.info(f"Successfully processed {file_path}")
        return financial_data
        
    except Exception as e:
        logger.error(f"Error processing 10-Q file {file_path}: {e}")
        raise


# Beispiel: Apple Q2 2024
if __name__ == "__main__":
    logger.info("Starting scrape_quarterlies script")
    
    # Demo der farbigen Log-Nachrichten
    print("\n🎨 Colored Logging Demo:")
    print("=" * 50)
    logger.debug("🔍 DEBUG: Detailed debugging information")
    logger.info("ℹ️  INFO: General program information")
    logger.warning("⚠️  WARNING: Something unexpected happened")
    logger.error("❌ ERROR: A serious problem occurred")
    logger.critical("🚨 CRITICAL: Very serious error occurred")
    print("=" * 50)
    print()
    
    try:
        # Erst schauen, welche Dokumente verfügbar sind
        print("Listing available documents for AAPL Q2 2024...")
        logger.info("Listing available documents for AAPL Q2 2024")
        documents = list_filing_documents("AAPL", 2024, 2)
        
        if documents:
            # Teste die neue Funktion mit einem verfügbaren Quartal
            print("\nTesting fetch_10q_by_quarter for AAPL Q2 2024...")
            logger.info("Testing fetch_10q_by_quarter for AAPL Q2 2024")
            file_path = fetch_10q_by_quarter("AAPL", 2024, 2)
            
            if file_path:
                # Verarbeite die Datei und extrahiere Financial Statements
                financial_data = process_10q_file(file_path)
                print(f"✅ Successfully processed {file_path}")
                print(f"📈 Found {len(financial_data['income_statement'])} income statement items")
                print(f"💰 Found {len(financial_data['balance_sheet'])} balance sheet items")
                print(f"💸 Found {len(financial_data['cash_flow'])} cash flow items")
                
                logger.info(f"Processing complete - Income: {len(financial_data['income_statement'])}, "
                           f"Balance: {len(financial_data['balance_sheet'])}, "
                           f"Cash Flow: {len(financial_data['cash_flow'])}")
            else:
                print("❌ No 10-Q file found for AAPL Q2 2024")
                logger.warning("No 10-Q file found for AAPL Q2 2024")
        else:
            print("❌ No documents found for AAPL Q2 2024")
            logger.warning("No documents found for AAPL Q2 2024")
            
    except Exception as e:
        logger.error(f"Script execution failed: {e}")
        print(f"❌ Script execution failed: {e}")
    
    logger.info("Script execution completed")

