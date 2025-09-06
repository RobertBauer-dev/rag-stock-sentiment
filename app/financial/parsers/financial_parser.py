"""
Financial Statement Parser for SEC 10-Q documents.
Extracted from scrape_quarterlies.py for better modularity.
"""

import json
import re
from typing import Dict, Any, Optional
from bs4 import BeautifulSoup

from app.core.logging import get_logger
from app.core.exceptions import ProcessingError

logger = get_logger(__name__)


class FinancialParser:
    """
    Parser for extracting financial statements from SEC 10-Q HTML documents.
    """
    
    def __init__(self):
        """Initialize the financial parser."""
        logger.info("🧮 Initializing Financial Parser")
    
    def extract_financial_statements(self, file_path: str) -> Dict[str, Any]:
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
                    financial_data['income_statement'] = self._extract_table_data(table, 'income_statement')
                
                # Suche nach Balance Sheet
                elif any(keyword in table_text for keyword in ['assets', 'liabilities', 'equity', 'balance']):
                    logger.info(f"Found balance sheet in table {i+1}")
                    financial_data['balance_sheet'] = self._extract_table_data(table, 'balance_sheet')
                
                # Suche nach Cash Flow
                elif any(keyword in table_text for keyword in ['cash flow', 'operating activities', 'investing activities']):
                    logger.info(f"Found cash flow statement in table {i+1}")
                    financial_data['cash_flow'] = self._extract_table_data(table, 'cash_flow')
            
            logger.info(f"Extraction complete - Income: {len(financial_data['income_statement'])} items, "
                       f"Balance: {len(financial_data['balance_sheet'])} items, "
                       f"Cash Flow: {len(financial_data['cash_flow'])} items")
            
            return financial_data
            
        except Exception as e:
            logger.error(f"Error extracting financial statements from {file_path}: {e}")
            raise ProcessingError(f"Error extracting financial statements from {file_path}: {e}")
    
    def _extract_table_data(self, table, statement_type: str) -> Dict[str, Any]:
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
            raise ProcessingError(f"Error extracting data from {statement_type} table: {e}")
        
        return data
    
    def save_financial_data_to_json(self, financial_data: Dict[str, Any], output_path: str) -> None:
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
            raise ProcessingError(f"Error saving financial data to {output_path}: {e}")
    
    def process_10q_file(self, file_path: str) -> Dict[str, Any]:
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
            financial_data = self.extract_financial_statements(file_path)
            
            # Erstelle JSON-Datei
            json_path = file_path.replace('.html', '_financial_data.json')
            self.save_financial_data_to_json(financial_data, json_path)
            
            logger.info(f"Successfully processed {file_path}")
            return financial_data
            
        except Exception as e:
            logger.error(f"Error processing 10-Q file {file_path}: {e}")
            raise ProcessingError(f"Error processing 10-Q file {file_path}: {e}")


# Backward compatibility functions
def extract_financial_statements(file_path: str) -> Dict[str, Any]:
    """Backward compatibility function."""
    parser = FinancialParser()
    return parser.extract_financial_statements(file_path)


def extract_table_data(table, statement_type: str) -> Dict[str, Any]:
    """Backward compatibility function."""
    parser = FinancialParser()
    return parser._extract_table_data(table, statement_type)


def save_financial_data_to_json(financial_data: Dict[str, Any], output_path: str) -> None:
    """Backward compatibility function."""
    parser = FinancialParser()
    return parser.save_financial_data_to_json(financial_data, output_path)


def process_10q_file(file_path: str) -> Dict[str, Any]:
    """Backward compatibility function."""
    parser = FinancialParser()
    return parser.process_10q_file(file_path)
