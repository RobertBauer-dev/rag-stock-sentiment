# Financial Data Warehouse

## 🏗️ Überblick

Das Financial Data Warehouse ist ein strukturiertes System zur Speicherung und Analyse von SEC 10-Q Financial Statements. Es verwendet SQLite als Backend und bietet eine vollständige Pipeline vom Scraping bis zur Analyse.

## 📊 Architektur

### **Komponenten:**
1. **FinancialDataWarehouse** - SQLite-basierte Datenbank
2. **ScrapingToWarehousePipeline** - Integration zwischen Scraping und Storage
3. **Strukturierte Schemas** - Normalisierte Tabellen für optimale Performance

### **Datenbank-Schema:**

#### **Companies Table**
```sql
CREATE TABLE companies (
    ticker TEXT PRIMARY KEY,
    company_name TEXT,
    cik TEXT,
    sector TEXT,
    industry TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

#### **Filings Table**
```sql
CREATE TABLE filings (
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
```

#### **Financial Statements Table**
```sql
CREATE TABLE financial_statements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filing_id INTEGER,
    statement_type TEXT,  -- 'income_statement', 'balance_sheet', 'cash_flow'
    account_name TEXT,
    values_json TEXT,     -- JSON array of values
    periods_json TEXT,    -- JSON array of period labels
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (filing_id) REFERENCES filings (id)
)
```

## 🚀 Verwendung

### **1. Einfache Verwendung:**

```python
from app.data.warehouse_integration import ScrapingToWarehousePipeline

# Pipeline initialisieren
pipeline = ScrapingToWarehousePipeline()

# Einzelnes Quartal scrapen und speichern
success = pipeline.scrape_and_store_company_quarter("AAPL", 2024, 2)

# Mehrere Quartale scrapen
quarters = [
    {'year': 2024, 'quarter': 2},
    {'year': 2024, 'quarter': 1},
    {'year': 2023, 'quarter': 4}
]
results = pipeline.scrape_multiple_quarters("AAPL", quarters)
```

### **2. Direkte Warehouse-Verwendung:**

```python
from app.financial.data_warehouse import FinancialDataWarehouse

# Warehouse initialisieren
warehouse = FinancialDataWarehouse()

# Company hinzufügen
warehouse.add_company("AAPL", "Apple Inc.", "0000320193", "Technology", "Consumer Electronics")

# Filing hinzufügen
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

# Financial Data hinzufügen
financial_data = {
    'income_statement': {
        'Revenue': [123456, 98765],
        'Net Income': [12345, 9876]
    }
}
warehouse.add_financial_data(filing_id, financial_data)
```

## 📈 Datenanalyse

### **1. Company Analysis:**
```python
# Vollständige Analyse für ein Unternehmen
analysis = pipeline.get_company_analysis("AAPL")
print(f"Total filings: {analysis['total_filings']}")
print(f"Data points: {analysis['total_data_points']}")
print(f"Available quarters: {analysis['quarters_available']}")
```

### **2. Quarterly Comparisons:**
```python
# Quartalsvergleich für spezifische Accounts
revenue_data = warehouse.get_quarterly_comparison("AAPL", "Revenue", quarters=8)
net_income_data = warehouse.get_quarterly_comparison("AAPL", "Net Income", quarters=8)
```

### **3. Financial Data Queries:**
```python
# Alle Financial Data für ein Unternehmen
all_data = warehouse.get_financial_data("AAPL")

# Spezifische Statement Types
income_data = warehouse.get_financial_data("AAPL", statement_type="income_statement")

# Spezifisches Jahr/Quartal
q2_2024_data = warehouse.get_financial_data("AAPL", year=2024, quarter=2)
```

## 📁 Export-Funktionen

### **1. CSV Export:**
```python
# Alle Daten für ein Unternehmen exportieren
pipeline.export_company_data("AAPL", output_dir="data/exports")
```

### **2. Database Statistics:**
```python
# Warehouse-Statistiken
stats = warehouse.get_database_stats()
print(f"Companies: {stats['companies']}")
print(f"Filings: {stats['filings']}")
print(f"Financial data points: {stats['financial_data_points']}")
```

## 🔧 Erweiterte Features

### **1. Multi-Company Scraping:**
```python
companies = ["AAPL", "MSFT", "GOOGL", "TSLA"]
quarters = [{'year': 2024, 'quarter': 2}]

for ticker in companies:
    results = pipeline.scrape_multiple_quarters(ticker, quarters)
    print(f"{ticker}: {results}")
```

### **2. Trend Analysis:**
```python
# Revenue-Trend über mehrere Quartale
revenue_trend = warehouse.get_quarterly_comparison("AAPL", "Revenue", quarters=12)
print(revenue_trend[['year', 'quarter', 'values']])
```

### **3. Comparative Analysis:**
```python
# Vergleich zwischen Unternehmen
companies = ["AAPL", "MSFT"]
for ticker in companies:
    analysis = pipeline.get_company_analysis(ticker)
    print(f"{ticker}: {analysis['total_data_points']} data points")
```

## 📊 Vorteile des Systems

### **✅ Strukturierte Speicherung:**
- Normalisierte Datenbank-Schemas
- Konsistente Datenformate
- Referentielle Integrität

### **✅ Performance:**
- SQLite mit optimierten Indizes
- Schnelle SQL-Abfragen
- Effiziente Datenstrukturen

### **✅ Skalierbarkeit:**
- Einfacher Wechsel zu PostgreSQL
- Modulare Architektur
- Erweiterbare Schemas

### **✅ Analytics-Ready:**
- Pandas-Integration
- Export-Funktionen
- Trend-Analyse-Tools

## 🚀 Nächste Schritte

### **1. Produktions-Upgrade:**
- Migration zu PostgreSQL
- Cloud-Deployment (AWS RDS, Google Cloud SQL)
- Backup-Strategien

### **2. Advanced Analytics:**
- Machine Learning Integration
- Predictive Analytics
- Automated Reporting

### **3. Real-time Updates:**
- Scheduled Scraping
- API-Integration
- Webhook-Support

### **4. Data Visualization:**
- Dashboard-Integration
- Chart-Generierung
- Interactive Reports

---

*Erstellt für das RAG Stock Sentiment Projekt - Financial Data Warehouse System*
