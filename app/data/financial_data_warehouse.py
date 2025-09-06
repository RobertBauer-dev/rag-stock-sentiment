#!/usr/bin/env python3
"""
Financial Data Warehouse für strukturierte Speicherung von SEC 10-Q Financial Statements.
"""

import sqlite3
import json
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging
from dataclasses import dataclass

# Import the logger from scrape_quarterlies
from scrape_quarterlies import logger
from kpi_calculator import KPICalculator, KPIResult

@dataclass
class FinancialDataPoint:
    """Data class für einen Financial Data Point."""
    ticker: str
    quarter: int
    year: int
    report_date: str
    filing_date: str
    statement_type: str  # 'income_statement', 'balance_sheet', 'cash_flow'
    account_name: str
    values: List[float]
    periods: List[str]
    source_file: str

class FinancialDataWarehouse:
    """
    Data Warehouse für Financial Statements mit SQLite Backend.
    """
    
    def __init__(self, db_path: str = "data/financial_warehouse.db"):
        """
        Initialize the Financial Data Warehouse.
        
        Args:
            db_path (str): Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize KPI Calculator
        self.kpi_calculator = KPICalculator()
        
        logger.info(f"🏗️ Initializing Financial Data Warehouse at: {self.db_path}")
        self._create_tables()
    
    def _create_tables(self):
        """Create database tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Companies table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS companies (
                    ticker TEXT PRIMARY KEY,
                    company_name TEXT,
                    cik TEXT,
                    sector TEXT,
                    industry TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Filings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS filings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticker TEXT,
                    quarter INTEGER,
                    year INTEGER,
                    report_date DATE,
                    filing_date DATE,
                    form_type TEXT,
                    accession_number TEXT,
                    source_file TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (ticker) REFERENCES companies (ticker),
                    UNIQUE(ticker, quarter, year, form_type)
                )
            """)
            
            # Financial statements table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS financial_statements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filing_id INTEGER,
                    statement_type TEXT,  -- 'income_statement', 'balance_sheet', 'cash_flow'
                    account_name TEXT,
                    values_json TEXT,     -- JSON array of values
                    periods_json TEXT,    -- JSON array of period labels
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (filing_id) REFERENCES filings (id)
                )
            """)
            
            # Metadata table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS metadata (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filing_id INTEGER,
                    key TEXT,
                    value TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (filing_id) REFERENCES filings (id)
                )
            """)
            
            # KPIs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS kpis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filing_id INTEGER,
                    kpi_name TEXT,
                    value REAL,
                    unit TEXT,
                    category TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (filing_id) REFERENCES filings (id)
                )
            """)
            
            # Create indexes for better performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_filings_ticker_quarter_year ON filings(ticker, quarter, year)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_financial_statements_filing_id ON financial_statements(filing_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_financial_statements_type ON financial_statements(statement_type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_financial_statements_account ON financial_statements(account_name)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_kpis_filing_id ON kpis(filing_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_kpis_name ON kpis(kpi_name)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_kpis_category ON kpis(category)")
            
            conn.commit()
            logger.info("✅ Database tables created successfully")
    
    def add_company(self, ticker: str, company_name: str, cik: str, 
                   sector: str = None, industry: str = None):
        """
        Add a company to the warehouse.
        
        Args:
            ticker (str): Stock ticker symbol
            company_name (str): Company name
            cik (str): Central Index Key
            sector (str): Business sector
            industry (str): Industry
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO companies 
                (ticker, company_name, cik, sector, industry)
                VALUES (?, ?, ?, ?, ?)
            """, (ticker, company_name, cik, sector, industry))
            conn.commit()
            logger.info(f"✅ Added company: {ticker} - {company_name}")
    
    def add_filing(self, ticker: str, quarter: int, year: int, 
                  report_date: str, filing_date: str, form_type: str,
                  accession_number: str, source_file: str) -> int:
        """
        Add a filing to the warehouse.
        
        Args:
            ticker (str): Stock ticker symbol
            quarter (int): Quarter (1-4)
            year (int): Year
            report_date (str): Report date (YYYY-MM-DD)
            filing_date (str): Filing date (YYYY-MM-DD)
            form_type (str): Form type (e.g., '10-Q')
            accession_number (str): SEC accession number
            source_file (str): Source file path
            
        Returns:
            int: Filing ID
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO filings 
                (ticker, quarter, year, report_date, filing_date, form_type, accession_number, source_file)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (ticker, quarter, year, report_date, filing_date, form_type, accession_number, source_file))
            
            filing_id = cursor.lastrowid
            conn.commit()
            logger.info(f"✅ Added filing: {ticker} {year}Q{quarter} (ID: {filing_id})")
            return filing_id
    
    def add_financial_data(self, filing_id: int, financial_data: Dict[str, Any]):
        """
        Add financial statement data to the warehouse.
        
        Args:
            filing_id (int): Filing ID
            financial_data (Dict[str, Any]): Financial data dictionary
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            for statement_type, data in financial_data.items():
                if statement_type == 'metadata':
                    continue
                    
                if isinstance(data, dict) and data:
                    for account_name, values in data.items():
                        if isinstance(values, list) and values:
                            cursor.execute("""
                                INSERT INTO financial_statements 
                                (filing_id, statement_type, account_name, values_json, periods_json)
                                VALUES (?, ?, ?, ?, ?)
                            """, (
                                filing_id,
                                statement_type,
                                account_name,
                                json.dumps(values),
                                json.dumps([])  # TODO: Add period labels
                            ))
            
            conn.commit()
            logger.info(f"✅ Added financial data for filing ID: {filing_id}")
    
    def get_company_filings(self, ticker: str) -> pd.DataFrame:
        """
        Get all filings for a company.
        
        Args:
            ticker (str): Stock ticker symbol
            
        Returns:
            pd.DataFrame: Filings data
        """
        with sqlite3.connect(self.db_path) as conn:
            query = """
                SELECT f.*, c.company_name 
                FROM filings f
                JOIN companies c ON f.ticker = c.ticker
                WHERE f.ticker = ?
                ORDER BY f.year DESC, f.quarter DESC
            """
            df = pd.read_sql_query(query, conn, params=(ticker,))
            logger.info(f"📊 Retrieved {len(df)} filings for {ticker}")
            return df
    
    def get_financial_data(self, ticker: str, statement_type: str = None, 
                          year: int = None, quarter: int = None) -> pd.DataFrame:
        """
        Get financial data for a company.
        
        Args:
            ticker (str): Stock ticker symbol
            statement_type (str): Type of statement ('income_statement', 'balance_sheet', 'cash_flow')
            year (int): Year filter
            quarter (int): Quarter filter
            
        Returns:
            pd.DataFrame: Financial data
        """
        with sqlite3.connect(self.db_path) as conn:
            query = """
                SELECT fs.*, f.ticker, f.quarter, f.year, f.report_date, f.filing_date, c.company_name
                FROM financial_statements fs
                JOIN filings f ON fs.filing_id = f.id
                JOIN companies c ON f.ticker = c.ticker
                WHERE f.ticker = ?
            """
            params = [ticker]
            
            if statement_type:
                query += " AND fs.statement_type = ?"
                params.append(statement_type)
            
            if year:
                query += " AND f.year = ?"
                params.append(year)
            
            if quarter:
                query += " AND f.quarter = ?"
                params.append(quarter)
            
            query += " ORDER BY f.year DESC, f.quarter DESC, fs.account_name"
            
            df = pd.read_sql_query(query, conn, params=params)
            
            # Parse JSON columns
            if not df.empty:
                df['values'] = df['values_json'].apply(json.loads)
                df['periods'] = df['periods_json'].apply(json.loads)
                df = df.drop(['values_json', 'periods_json'], axis=1)
            
            logger.info(f"📊 Retrieved {len(df)} financial data points for {ticker}")
            return df
    
    def get_quarterly_comparison(self, ticker: str, account_name: str, 
                               quarters: int = 4) -> pd.DataFrame:
        """
        Get quarterly comparison for a specific account.
        
        Args:
            ticker (str): Stock ticker symbol
            account_name (str): Account name
            quarters (int): Number of quarters to compare
            
        Returns:
            pd.DataFrame: Quarterly comparison data
        """
        with sqlite3.connect(self.db_path) as conn:
            query = """
                SELECT f.ticker, f.quarter, f.year, f.report_date, 
                       fs.account_name, fs.values_json, c.company_name
                FROM financial_statements fs
                JOIN filings f ON fs.filing_id = f.id
                JOIN companies c ON f.ticker = c.ticker
                WHERE f.ticker = ? AND fs.account_name = ?
                ORDER BY f.year DESC, f.quarter DESC
                LIMIT ?
            """
            
            df = pd.read_sql_query(query, conn, params=(ticker, account_name, quarters))
            
            if not df.empty:
                df['values'] = df['values_json'].apply(json.loads)
                df = df.drop(['values_json'], axis=1)
            
            logger.info(f"📊 Retrieved quarterly comparison for {ticker} - {account_name}")
            return df
    
    def export_to_csv(self, ticker: str, output_dir: str = "data/exports"):
        """
        Export financial data to CSV files.
        
        Args:
            ticker (str): Stock ticker symbol
            output_dir (str): Output directory
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Export all financial data
        df = self.get_financial_data(ticker)
        if not df.empty:
            csv_file = output_path / f"{ticker}_financial_data.csv"
            df.to_csv(csv_file, index=False)
            logger.info(f"📁 Exported financial data to: {csv_file}")
        
        # Export quarterly comparison for key accounts
        key_accounts = ['Revenue', 'Net Income', 'Total Assets', 'Total Liabilities']
        for account in key_accounts:
            comparison_df = self.get_quarterly_comparison(ticker, account)
            if not comparison_df.empty:
                csv_file = output_path / f"{ticker}_{account.replace(' ', '_')}_quarterly.csv"
                comparison_df.to_csv(csv_file, index=False)
                logger.info(f"📁 Exported {account} quarterly data to: {csv_file}")
    
    def get_database_stats(self) -> Dict[str, Any]:
        """
        Get database statistics.
        
        Returns:
            Dict[str, Any]: Database statistics
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            stats = {}
            
            # Company count
            cursor.execute("SELECT COUNT(*) FROM companies")
            stats['companies'] = cursor.fetchone()[0]
            
            # Filing count
            cursor.execute("SELECT COUNT(*) FROM filings")
            stats['filings'] = cursor.fetchone()[0]
            
            # Financial data points count
            cursor.execute("SELECT COUNT(*) FROM financial_statements")
            stats['financial_data_points'] = cursor.fetchone()[0]
            
            # Statement types distribution
            cursor.execute("""
                SELECT statement_type, COUNT(*) 
                FROM financial_statements 
                GROUP BY statement_type
            """)
            stats['statement_types'] = dict(cursor.fetchall())
            
            # Top companies by data points
            cursor.execute("""
                SELECT f.ticker, COUNT(fs.id) as data_points
                FROM filings f
                JOIN financial_statements fs ON f.id = fs.filing_id
                GROUP BY f.ticker
                ORDER BY data_points DESC
                LIMIT 10
            """)
            stats['top_companies'] = dict(cursor.fetchall())
            
        logger.info(f"📊 Database stats: {stats}")
        return stats
    
    def add_kpis(self, filing_id: int, financial_data: Dict[str, Any], 
                 ticker: str, year: int, quarter: int):
        """
        Berechnet und speichert KPIs für ein Filing.
        
        Args:
            filing_id (int): Filing ID
            financial_data (Dict[str, Any]): Financial data
            ticker (str): Stock ticker symbol
            year (int): Year
            quarter (int): Quarter
        """
        try:
            # Berechne KPIs
            kpis = self.kpi_calculator.calculate_kpis(financial_data, ticker, year, quarter)
            
            if not kpis:
                logger.warning(f"No KPIs calculated for filing ID {filing_id}")
                return
            
            # Speichere KPIs in der Datenbank
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for kpi in kpis:
                    cursor.execute("""
                        INSERT INTO kpis (filing_id, kpi_name, value, unit, category)
                        VALUES (?, ?, ?, ?, ?)
                    """, (filing_id, kpi.kpi_name, kpi.value, kpi.unit, kpi.category))
                
                conn.commit()
                logger.info(f"✅ Added {len(kpis)} KPIs for filing ID {filing_id}")
                
        except Exception as e:
            logger.error(f"❌ Error adding KPIs for filing ID {filing_id}: {e}")
    
    def get_kpis(self, ticker: str, kpi_name: str = None, 
                 year: int = None, quarter: int = None) -> pd.DataFrame:
        """
        Holt KPIs für ein Unternehmen.
        
        Args:
            ticker (str): Stock ticker symbol
            kpi_name (str): Spezifischer KPI Name (optional)
            year (int): Jahr Filter (optional)
            quarter (int): Quartal Filter (optional)
            
        Returns:
            pd.DataFrame: KPI Daten
        """
        with sqlite3.connect(self.db_path) as conn:
            query = """
                SELECT k.*, f.ticker, f.quarter, f.year, f.report_date, c.company_name
                FROM kpis k
                JOIN filings f ON k.filing_id = f.id
                JOIN companies c ON f.ticker = c.ticker
                WHERE f.ticker = ?
            """
            params = [ticker]
            
            if kpi_name:
                query += " AND k.kpi_name = ?"
                params.append(kpi_name)
            
            if year:
                query += " AND f.year = ?"
                params.append(year)
            
            if quarter:
                query += " AND f.quarter = ?"
                params.append(quarter)
            
            query += " ORDER BY f.year DESC, f.quarter DESC, k.kpi_name"
            
            df = pd.read_sql_query(query, conn, params=params)
            logger.info(f"📊 Retrieved {len(df)} KPI records for {ticker}")
            return df
    
    def get_kpi_trends(self, ticker: str, kpi_name: str, quarters: int = 8) -> pd.DataFrame:
        """
        Holt KPI-Trends für ein Unternehmen.
        
        Args:
            ticker (str): Stock ticker symbol
            kpi_name (str): KPI Name
            quarters (int): Anzahl der Quartale
            
        Returns:
            pd.DataFrame: KPI Trend Daten
        """
        with sqlite3.connect(self.db_path) as conn:
            query = """
                SELECT k.value, k.unit, f.quarter, f.year, f.report_date
                FROM kpis k
                JOIN filings f ON k.filing_id = f.id
                WHERE f.ticker = ? AND k.kpi_name = ?
                ORDER BY f.year DESC, f.quarter DESC
                LIMIT ?
            """
            
            df = pd.read_sql_query(query, conn, params=(ticker, kpi_name, quarters))
            logger.info(f"📊 Retrieved {len(df)} trend points for {ticker} - {kpi_name}")
            return df


# Example usage
if __name__ == "__main__":
    # Initialize warehouse
    warehouse = FinancialDataWarehouse()
    
    # Add a company
    warehouse.add_company("AAPL", "Apple Inc.", "0000320193", "Technology", "Consumer Electronics")
    
    # Add a filing
    filing_id = warehouse.add_filing(
        ticker="AAPL",
        quarter=2,
        year=2024,
        report_date="2024-06-29",
        filing_date="2024-08-02",
        form_type="10-Q",
        accession_number="0000320193-24-000081",
        source_file="AAPL_10Q_2024Q2_2024-06-29.html"
    )
    
    # Example financial data
    sample_financial_data = {
        'income_statement': {
            'Revenue': [123456, 98765],
            'Net Income': [12345, 9876]
        },
        'balance_sheet': {
            'Total Assets': [500000, 450000],
            'Total Liabilities': [200000, 180000]
        }
    }
    
    # Add financial data
    warehouse.add_financial_data(filing_id, sample_financial_data)
    
    # Get database stats
    stats = warehouse.get_database_stats()
    print(f"Database Statistics: {stats}")
