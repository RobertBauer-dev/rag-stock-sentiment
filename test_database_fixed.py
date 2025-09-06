#!/usr/bin/env python3
"""
Fixed Test Script für Financial Data Warehouse und KPI Calculator.
"""

import sys
import os
import sqlite3
import pandas as pd
from pathlib import Path

# Add current directory to path
sys.path.append('.')

def test_database_connection():
    """Teste die Datenbankverbindung."""
    print("🔍 Testing Database Connection...")
    
    db_path = Path("data/financial_warehouse.db")
    if not db_path.exists():
        print("❌ Database file not found!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"✅ Database connected successfully!")
        print(f"📋 Tables found: {[table[0] for table in tables]}")
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def analyze_database_stats():
    """Analysiere die Datenbank-Statistiken."""
    print("\n📊 Database Statistics:")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect("data/financial_warehouse.db")
        
        # Companies
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM companies")
        companies_count = cursor.fetchone()[0]
        print(f"🏢 Companies: {companies_count}")
        
        # Filings
        cursor.execute("SELECT COUNT(*) FROM filings")
        filings_count = cursor.fetchone()[0]
        print(f"📄 Filings: {filings_count}")
        
        # Financial Statements
        cursor.execute("SELECT COUNT(*) FROM financial_statements")
        financial_count = cursor.fetchone()[0]
        print(f"💰 Financial Data Points: {financial_count}")
        
        # KPIs
        cursor.execute("SELECT COUNT(*) FROM kpis")
        kpis_count = cursor.fetchone()[0]
        print(f"📈 KPI Records: {kpis_count}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error analyzing database: {e}")

def analyze_googl_data():
    """Analysiere GOOGL-spezifische Daten."""
    print("\n🔍 GOOGL Data Analysis:")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect("data/financial_warehouse.db")
        
        # GOOGL Filings
        print("📄 GOOGL Filings:")
        filings_df = pd.read_sql_query("""
            SELECT ticker, year, quarter, report_date, filing_date, form_type
            FROM filings 
            WHERE ticker = 'GOOGL' 
            ORDER BY year DESC, quarter DESC
        """, conn)
        
        if len(filings_df) > 0:
            print(f"   Found {len(filings_df)} filings:")
            for _, row in filings_df.head().iterrows():
                print(f"   - {row['year']}Q{row['quarter']} ({row['report_date']}) - {row['form_type']}")
        else:
            print("   ❌ No GOOGL filings found!")
        
        # GOOGL Financial Data - FIXED SQL
        print("\n💰 GOOGL Financial Data:")
        financial_df = pd.read_sql_query("""
            SELECT fs.account_name, fs.statement_type, fs.values
            FROM financial_statements fs
            JOIN filings f ON fs.filing_id = f.id
            WHERE f.ticker = 'GOOGL'
            LIMIT 10
        """, conn)
        
        if len(financial_df) > 0:
            print(f"   Found {len(financial_df)} financial records:")
            for _, row in financial_df.head().iterrows():
                values = eval(row['values']) if row['values'] else []
                print(f"   - {row['account_name']} ({row['statement_type']}): {len(values)} values")
        else:
            print("   ❌ No GOOGL financial data found!")
        
        # GOOGL KPIs
        print("\n📈 GOOGL KPIs:")
        kpis_df = pd.read_sql_query("""
            SELECT k.kpi_name, k.value, k.unit, k.category, f.year, f.quarter
            FROM kpis k
            JOIN filings f ON k.filing_id = f.id
            WHERE f.ticker = 'GOOGL'
            ORDER BY f.year DESC, f.quarter DESC, k.kpi_name
        """, conn)
        
        if len(kpis_df) > 0:
            print(f"   Found {len(kpis_df)} KPI records:")
            for _, row in kpis_df.head().iterrows():
                print(f"   - {row['kpi_name']}: {row['value']:,.2f} {row['unit']} ({row['category']})")
        else:
            print("   ❌ No GOOGL KPIs found!")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error analyzing GOOGL data: {e}")

def test_kpi_calculator():
    """Teste den KPI Calculator."""
    print("\n🧮 Testing KPI Calculator:")
    print("=" * 50)
    
    try:
        # Import with proper path
        sys.path.append('app/data')
        from kpi_calculator import KPICalculator
        
        # Sample financial data
        sample_data = {
            'income_statement': {
                'Revenue': [123456000, 98765000],
                'Gross Profit': [45678000, 34567000],
                'Operating Income': [23456000, 18765000],
                'Net Income': [15678000, 12345000]
            },
            'balance_sheet': {
                'Total Assets': [500000000, 450000000],
                'Total Liabilities': [200000000, 180000000],
                'Shareholders Equity': [300000000, 270000000],
                'Current Assets': [150000000, 135000000],
                'Current Liabilities': [80000000, 72000000]
            },
            'cash_flow': {
                'Operating Cash Flow': [25000000, 23000000],
                'Capital Expenditures': [-5000000, -4000000]
            }
        }
        
        calculator = KPICalculator()
        kpis = calculator.calculate_kpis(sample_data, "TEST", 2024, 2)
        
        print(f"✅ KPI Calculator working! Calculated {len(kpis)} KPIs:")
        for kpi in kpis[:5]:  # Show first 5
            print(f"   - {kpi.kpi_name}: {kpi.value:,.2f} {kpi.unit} ({kpi.category})")
        
        return True
        
    except Exception as e:
        print(f"❌ KPI Calculator test failed: {e}")
        return False

def generate_kpis_for_existing_data():
    """Generiere KPIs für bestehende Daten."""
    print("\n🔄 Generating KPIs for Existing Data:")
    print("=" * 50)
    
    try:
        # Import with proper path
        sys.path.append('app/data')
        from financial_data_warehouse import FinancialDataWarehouse
        from kpi_calculator import KPICalculator
        
        warehouse = FinancialDataWarehouse("data/financial_warehouse.db")
        calculator = KPICalculator()
        
        # Get all GOOGL filings without KPIs
        conn = sqlite3.connect("data/financial_warehouse.db")
        
        # Find filings without KPIs
        cursor = conn.cursor()
        cursor.execute("""
            SELECT f.id, f.ticker, f.year, f.quarter
            FROM filings f
            WHERE f.ticker = 'GOOGL'
            AND f.id NOT IN (SELECT DISTINCT filing_id FROM kpis)
        """)
        
        filings_without_kpis = cursor.fetchall()
        print(f"📋 Found {len(filings_without_kpis)} filings without KPIs")
        
        if filings_without_kpis:
            print("🔄 Generating KPIs...")
            
            for filing_id, ticker, year, quarter in filings_without_kpis:
                # Get financial data for this filing
                financial_df = pd.read_sql_query("""
                    SELECT account_name, statement_type, values
                    FROM financial_statements
                    WHERE filing_id = ?
                """, conn, params=(filing_id,))
                
                if not financial_df.empty:
                    # Convert to the format expected by KPI calculator
                    financial_data = {}
                    for _, row in financial_df.iterrows():
                        statement_type = row['statement_type']
                        if statement_type not in financial_data:
                            financial_data[statement_type] = {}
                        
                        values = eval(row['values']) if row['values'] else []
                        financial_data[statement_type][row['account_name']] = values
                    
                    # Calculate KPIs
                    kpis = calculator.calculate_kpis(financial_data, ticker, year, quarter)
                    
                    # Add to database
                    warehouse.add_kpis(filing_id, financial_data, ticker, year, quarter)
                    
                    print(f"   ✅ Generated {len(kpis)} KPIs for {ticker} {year}Q{quarter}")
        
        conn.close()
        print("🎉 KPI generation completed!")
        
    except Exception as e:
        print(f"❌ Error generating KPIs: {e}")

def test_revenue_query():
    """Teste die Revenue-Abfrage direkt."""
    print("\n💰 Testing Revenue Query:")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect("data/financial_warehouse.db")
        
        # Test direct revenue query
        revenue_df = pd.read_sql_query("""
            SELECT fs.account_name, fs.values, f.year, f.quarter
            FROM financial_statements fs
            JOIN filings f ON fs.filing_id = f.id
            WHERE f.ticker = 'GOOGL' 
            AND fs.account_name LIKE '%Revenue%'
            ORDER BY f.year DESC, f.quarter DESC
        """, conn)
        
        if len(revenue_df) > 0:
            print(f"✅ Found {len(revenue_df)} revenue records:")
            for _, row in revenue_df.head().iterrows():
                values = eval(row['values']) if row['values'] else []
                print(f"   - {row['account_name']} ({row['year']}Q{row['quarter']}): {values}")
        else:
            print("❌ No revenue data found!")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error testing revenue query: {e}")

def main():
    """Hauptfunktion für alle Tests."""
    print("🚀 Financial Data Warehouse Test Suite (Fixed)")
    print("=" * 60)
    
    # Test 1: Database Connection
    if not test_database_connection():
        print("❌ Database connection failed. Exiting.")
        return
    
    # Test 2: Database Statistics
    analyze_database_stats()
    
    # Test 3: GOOGL Data Analysis
    analyze_googl_data()
    
    # Test 4: Revenue Query Test
    test_revenue_query()
    
    # Test 5: KPI Calculator
    if test_kpi_calculator():
        print("✅ KPI Calculator is working correctly!")
    else:
        print("❌ KPI Calculator has issues!")
    
    # Test 6: Generate KPIs for existing data
    print("\n" + "=" * 60)
    response = input("🔄 Do you want to generate KPIs for existing GOOGL data? (y/n): ")
    if response.lower() == 'y':
        generate_kpis_for_existing_data()
        
        # Re-analyze after KPI generation
        print("\n" + "=" * 60)
        print("📊 Updated Analysis After KPI Generation:")
        analyze_googl_data()
    
    print("\n🎉 Test Suite Completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()
