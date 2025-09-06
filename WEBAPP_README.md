# Financial Data Visualization Web Application

## 🚀 Überblick

Eine moderne Web-Anwendung zur Visualisierung von Financial Statements mit interaktiven Barcharts für Umsätze und andere Finanzkennzahlen mehrerer Quartale.

## 🏗️ Architektur

### **Frontend:**
- **HTML5** mit Bootstrap 5 für responsive Design
- **Chart.js** für interaktive Charts
- **Axios** für API-Kommunikation
- **Vanilla JavaScript** für App-Logik

### **Backend:**
- **FastAPI** für REST API
- **SQLite** Data Warehouse
- **Pandas** für Datenverarbeitung
- **Jinja2** für Template-Rendering

## 📊 Features

### **1. Interactive Charts:**
- **Revenue Barchart** - Quartalsumsätze mit Hover-Details
- **Financial Metrics Chart** - Mehrere Kennzahlen gleichzeitig
- **Responsive Design** - Funktioniert auf Desktop und Mobile

### **2. Data Management:**
- **Company Selection** - Dropdown mit verfügbaren Unternehmen
- **Quarter Selection** - 4, 8, 12 oder 16 Quartale
- **Real-time Scraping** - Neue Daten direkt von SEC
- **Database Statistics** - Übersicht über gespeicherte Daten

### **3. Data Visualization:**
- **Interactive Tooltips** - Detaillierte Informationen bei Hover
- **Smooth Animations** - Professionelle Chart-Animationen
- **Color-coded Metrics** - Verschiedene Farben für verschiedene Kennzahlen
- **Responsive Tables** - Übersichtliche Daten-Tabellen

## 🚀 Installation & Start

### **1. Dependencies installieren:**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### **2. Web-Anwendung starten:**
```bash
python start_webapp.py
```

### **3. Browser öffnen:**
```
http://localhost:8000
```

## 📱 Verwendung

### **1. Company Selection:**
- Wählen Sie ein Unternehmen aus dem Dropdown
- Wählen Sie die Anzahl der Quartale (4, 8, 12, 16)
- Klicken Sie auf "📈 Load Data"

### **2. Data Scraping:**
- Klicken Sie auf "📥 Scrape New Data" für neue Daten
- Das System lädt automatisch die neuesten 10-Q Reports
- Daten werden im Data Warehouse gespeichert

### **3. Chart Interaction:**
- **Hover** über Balken für detaillierte Informationen
- **Zoom** und **Pan** für bessere Analyse
- **Legend** zum Ein-/Ausblenden von Metriken

## 🔧 API Endpoints

### **GET /api/company/{ticker}/revenue**
```json
{
  "ticker": "AAPL",
  "data": [123456, 98765, 87654],
  "labels": ["2024 Q2", "2024 Q1", "2023 Q4"],
  "quarters": ["2024Q2", "2024Q1", "2023Q4"],
  "unit": "Millions USD"
}
```

### **GET /api/company/{ticker}/financials**
```json
{
  "ticker": "AAPL",
  "financials": {
    "Revenue": {
      "values": [123456, 98765],
      "labels": ["2024 Q2", "2024 Q1"]
    },
    "Net Income": {
      "values": [12345, 9876],
      "labels": ["2024 Q2", "2024 Q1"]
    }
  },
  "unit": "Millions USD"
}
```

### **POST /api/scrape**
```json
{
  "ticker": "AAPL",
  "quarters": 4,
  "results": {
    "2024Q2": true,
    "2024Q1": true,
    "2023Q4": false
  },
  "successful": 2,
  "total": 3
}
```

## 📊 Chart Types

### **1. Revenue Barchart:**
- **Type:** Bar Chart
- **Data:** Quartalsumsätze
- **Colors:** Blau (rgba(54, 162, 235, 0.8))
- **Animation:** 1000ms easeInOutQuart

### **2. Financial Metrics Chart:**
- **Type:** Multi-Bar Chart
- **Data:** Revenue, Net Income, Total Assets, Total Liabilities
- **Colors:** Verschiedene Farben für jede Metrik
- **Animation:** 1000ms easeInOutQuart

## 🎨 UI Components

### **1. Company Selection Card:**
- Dropdown für Ticker-Auswahl
- Quarter-Selection
- Load Data Button

### **2. Data Management Card:**
- Scrape New Data Button
- Database Stats Button

### **3. Chart Cards:**
- Revenue Chart mit Statistiken
- Financial Metrics Chart
- Responsive Design

### **4. Data Table:**
- Sortierbare Tabelle
- Responsive Scroll
- Hover-Effekte

## 🔄 Data Flow

```
1. User wählt Company & Quarters
2. Frontend sendet API-Request
3. Backend prüft Data Warehouse
4. Falls keine Daten: Scraping wird gestartet
5. Daten werden verarbeitet und zurückgesendet
6. Frontend erstellt interaktive Charts
7. User kann mit Charts interagieren
```

## 🚀 Erweiterte Features

### **1. Real-time Updates:**
- WebSocket-Integration für Live-Updates
- Auto-refresh bei neuen Daten
- Push-Notifications

### **2. Advanced Analytics:**
- Trend-Analyse
- Vergleich zwischen Unternehmen
- Predictive Charts

### **3. Export Functions:**
- PDF-Export der Charts
- Excel-Export der Daten
- Image-Export für Präsentationen

### **4. User Management:**
- Login/Logout
- Favoriten-System
- Personalisierte Dashboards

## 🛠️ Development

### **Frontend Development:**
```bash
# CSS anpassen
app/webapp/static/css/style.css

# JavaScript erweitern
app/webapp/static/js/app.js

# HTML-Templates
app/webapp/templates/index.html
```

### **Backend Development:**
```bash
# API-Endpoints
app/webapp/main.py

# Data Warehouse
app/financial/data_warehouse.py

# Integration
app/data/warehouse_integration.py
```

### **Hot Reload:**
Die Anwendung unterstützt Hot Reload für Development:
```bash
python start_webapp.py
# Änderungen werden automatisch geladen
```

## 📱 Mobile Support

- **Responsive Design** mit Bootstrap 5
- **Touch-friendly** Charts
- **Mobile-optimierte** Navigation
- **Adaptive Layout** für verschiedene Bildschirmgrößen

## 🔒 Security

- **Input Validation** für alle API-Endpoints
- **Error Handling** mit benutzerfreundlichen Nachrichten
- **Rate Limiting** für Scraping-Requests
- **CORS-Configuration** für Cross-Origin Requests

---

*Erstellt für das RAG Stock Sentiment Projekt - Financial Data Visualization Web Application*
