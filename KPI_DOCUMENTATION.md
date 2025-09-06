# 📊 KPI Calculator Documentation

## 🎯 **Übersicht**

Der KPI Calculator extrahiert und berechnet automatisch wichtige Finanzkennzahlen (KPIs) aus den 10-Q Financial Statements. Das System ist vollständig in das Financial Data Warehouse integriert.

## ✅ **Implementierte KPIs**

### **💰 Profitability KPIs**
- **Revenue** - Gesamtumsatz
- **Gross Profit** - Bruttogewinn  
- **Gross Margin** - Bruttomarge (berechnet: Gross Profit / Revenue × 100)
- **Operating Income** - Betriebsergebnis
- **Operating Margin** - Betriebsmarge (berechnet: Operating Income / Revenue × 100)
- **Net Income** - Nettoeinkommen
- **Net Margin** - Nettomarge (berechnet: Net Income / Revenue × 100)

### **🏦 Balance Sheet KPIs**
- **Total Assets** - Gesamtvermögen
- **Total Liabilities** - Gesamtverbindlichkeiten
- **Shareholders Equity** - Eigenkapital
- **Current Assets** - Umlaufvermögen
- **Current Liabilities** - Kurzfristige Verbindlichkeiten

### **📈 Leverage KPIs**
- **Debt-to-Equity Ratio** - Verschuldungsgrad (berechnet: Total Liabilities / Shareholders Equity)

### **💧 Liquidity KPIs**
- **Current Ratio** - Liquiditätsgrad 1 (berechnet: Current Assets / Current Liabilities)

### **💸 Cash Flow KPIs**
- **Operating Cash Flow** - Betriebskassenzufluss
- **Free Cash Flow** - Freier Cashflow (berechnet: Operating Cash Flow - CapEx)

### **⚡ Efficiency KPIs**
- **Return on Assets (ROA)** - Gesamtkapitalrentabilität (berechnet: Net Income / Total Assets × 100)
- **Return on Equity (ROE)** - Eigenkapitalrentabilität (berechnet: Net Income / Shareholders Equity × 100)

## 🔧 **Technische Implementierung**

### **1. KPI Calculator (`app/data/kpi_calculator.py`)**
```python
from kpi_calculator import KPICalculator, KPIResult

# Calculator initialisieren
calculator = KPICalculator()

# KPIs berechnen
kpis = calculator.calculate_kpis(financial_data, ticker, year, quarter)
```

### **2. Data Warehouse Integration**
```python
# KPIs automatisch berechnen und speichern
warehouse.add_kpis(filing_id, financial_data, ticker, year, quarter)

# KPIs abrufen
kpis_df = warehouse.get_kpis(ticker)
kpi_trend = warehouse.get_kpi_trends(ticker, "Revenue", quarters=8)
```

### **3. Web API Endpoints**
```bash
# Alle KPIs für ein Unternehmen
GET /api/company/{ticker}/kpis?quarters=8

# Spezifischer KPI
GET /api/company/{ticker}/kpi/{kpi_name}?quarters=8
```

## 📊 **KPI-Kategorien**

| Kategorie | Beschreibung | KPIs |
|-----------|--------------|------|
| **profitability** | Rentabilitätskennzahlen | Revenue, Gross Margin, Operating Margin, Net Margin |
| **balance_sheet** | Bilanzkennzahlen | Total Assets, Total Liabilities, Shareholders Equity |
| **leverage** | Verschuldungskennzahlen | Debt-to-Equity Ratio |
| **liquidity** | Liquiditätskennzahlen | Current Ratio |
| **cash_flow** | Cashflow-Kennzahlen | Operating Cash Flow, Free Cash Flow |
| **efficiency** | Effizienzkennzahlen | ROA, ROE |

## 🚀 **Automatische Berechnung**

### **Pipeline Integration**
Die KPI-Berechnung ist vollständig in die Scraping-Pipeline integriert:

1. **Scraping** → Financial Statements extrahieren
2. **KPI Calculation** → Automatische Berechnung aller KPIs
3. **Storage** → Speicherung in SQLite Database
4. **API** → Verfügbarkeit über REST API

### **Beispiel Workflow**
```python
# 1. Scraping
results = pipeline.scrape_multiple_quarters("AAPL", quarters_to_scrape)

# 2. KPIs werden automatisch berechnet und gespeichert
# 3. Abrufen über API
kpis = warehouse.get_kpis("AAPL")
```

## 📈 **Trend-Analyse**

### **Quartalsvergleiche**
```python
# KPI-Trends über mehrere Quartale
kpi_trend = warehouse.get_kpi_trends("AAPL", "Revenue", quarters=8)

# Wachstumsraten berechnen
growth_data = calculator.calculate_quarterly_growth(kpis, "Revenue")
```

### **Verfügbare Trend-Funktionen**
- **Quarterly Growth Rate** - Quartalswachstum
- **Year-over-Year Growth** - Jahresvergleich
- **Moving Averages** - Gleitende Durchschnitte

## 🎨 **Web Dashboard Integration**

### **Chart.js Visualisierung**
```javascript
// KPI-Daten laden
const response = await axios.get(`/api/company/${ticker}/kpi/Revenue`);
const data = response.data;

// Chart erstellen
createKPIChart(data);
```

### **Verfügbare Charts**
- **Revenue Trends** - Umsatzentwicklung
- **Margin Analysis** - Marge-Analyse
- **Profitability Metrics** - Rentabilitätskennzahlen
- **Balance Sheet Overview** - Bilanzübersicht

## 🔍 **Account Name Matching**

Das System verwendet intelligentes Account Name Matching:

### **Revenue Matching**
```python
possible_names = ['Revenue', 'Total Revenue', 'Net Sales']
```

### **Gross Profit Matching**
```python
possible_names = ['Gross Profit', 'Gross Income']
```

### **Flexible Suche**
- **Case-insensitive** - Groß-/Kleinschreibung ignoriert
- **Partial matching** - Teilweise Übereinstimmung
- **Multiple variations** - Verschiedene Bezeichnungen

## 📋 **Datenbank Schema**

### **KPIs Tabelle**
```sql
CREATE TABLE kpis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filing_id INTEGER,
    kpi_name TEXT,
    value REAL,
    unit TEXT,
    category TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (filing_id) REFERENCES filings (id)
);
```

### **Indizes für Performance**
```sql
CREATE INDEX idx_kpis_filing_id ON kpis(filing_id);
CREATE INDEX idx_kpis_name ON kpis(kpi_name);
CREATE INDEX idx_kpis_category ON kpis(category);
```

## 🎯 **Verwendung in der Web-Anwendung**

### **1. KPI-Dashboard**
- **Übersicht** aller verfügbaren KPIs
- **Trend-Charts** für wichtige Kennzahlen
- **Vergleich** zwischen Quartalen

### **2. Spezifische KPI-Analyse**
- **Revenue Growth** - Umsatzwachstum
- **Margin Trends** - Marge-Entwicklung
- **Profitability Analysis** - Rentabilitätsanalyse

### **3. Export-Funktionen**
- **CSV Export** aller KPIs
- **JSON API** für externe Integration
- **Chart Export** als PNG/PDF

## 🚀 **Nächste Schritte**

### **Geplante Erweiterungen**
1. **Peer Comparison** - Vergleich mit Konkurrenten
2. **Industry Benchmarks** - Branchenvergleiche
3. **Forecasting** - Prognose-Modelle
4. **Alert System** - Benachrichtigungen bei Änderungen

### **Zusätzliche KPIs**
- **Price-to-Earnings (P/E) Ratio**
- **Earnings per Share (EPS)**
- **Book Value per Share**
- **Working Capital**

## 📞 **Support**

Bei Fragen oder Problemen mit dem KPI Calculator:

1. **Logs prüfen** - Detaillierte Logs in `logs/scrape_quarterlies.log`
2. **API testen** - Endpoints über `/api/company/{ticker}/kpis` testen
3. **Database prüfen** - SQLite Database in `data/financial_warehouse.db`

---

**🎉 Das KPI-System ist vollständig funktionsfähig und bereit für die Produktion!**
