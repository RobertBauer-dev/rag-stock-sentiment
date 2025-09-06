# 🏗️ Projektstruktur-Übersicht

## 📋 **Aktualisierte Struktur (Dezember 2024)**

Das Projekt wurde vollständig reorganisiert für bessere Wartbarkeit und Skalierbarkeit.

## 🎯 **Hauptverbesserungen**

### ✅ **Zentrales Logging-System**
- **115 Zeilen Logger-Code** aus `scrape_quarterlies.py` extrahiert
- Neues `app/core/logging.py` mit `ColoredFormatter`
- Alle Module verwenden `get_logger(__name__)`

### ✅ **Modulare Struktur nach Funktionalität**
- **RAG-System**: `app/rag/` (Reddit, Embeddings, Vector Store, LLM)
- **Financial-System**: `app/financial/` (SEC Scraper, Data Warehouse, KPI Calculator)
- **Core-Module**: `app/core/` (Logging, Config, Exceptions)

### ✅ **Zentrale Konfiguration**
- `app/core/config.py` mit allen Pfaden und Einstellungen
- Automatische Verzeichniserstellung
- Validierung der Konfiguration

## 📁 **Neue Verzeichnisstruktur**

```
rag-stock-sentiment/
├── app/
│   ├── core/                    # 🆕 ZENTRALE KERN-MODULE
│   │   ├── __init__.py
│   │   ├── config.py           # Zentrale Konfiguration
│   │   ├── logging.py          # Zentrales Logging (115 Zeilen extrahiert!)
│   │   └── exceptions.py       # Custom Exceptions
│   │
│   ├── rag/                    # 🔄 RAG-SYSTEM (bereinigt)
│   │   ├── __init__.py
│   │   ├── reddit_client.py    # Aus data/ verschoben
│   │   ├── embedding/          # Embedding-Verarbeitung
│   │   │   ├── __init__.py
│   │   │   └── embed_posts.py
│   │   ├── vector_store/       # Vector Store
│   │   │   ├── __init__.py
│   │   │   └── client.py
│   │   ├── query_engine.py     # RAG Query Engine
│   │   └── llm/               # LLM-Integration
│   │       ├── __init__.py
│   │       └── generator.py
│   │
│   ├── financial/              # 🆕 FINANCIAL DATA SYSTEM
│   │   ├── __init__.py
│   │   ├── sec_scraper.py      # Aus data/scrape_quarterlies.py
│   │   ├── data_warehouse.py   # Aus data/financial_data_warehouse.py
│   │   ├── kpi_calculator.py   # Aus data/kpi_calculator.py
│   │   └── parsers/           # 🆕 HTML/Financial Statement Parser
│   │       ├── __init__.py
│   │       └── financial_parser.py
│   │
│   ├── webapp/                 # 🔄 WEB APPLICATION
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI App
│   │   ├── static/            # CSS, JS, Images
│   │   └── templates/         # HTML Templates
│   │
│   └── utils/                  # 🔄 GEMEINSAME UTILITIES
│       ├── __init__.py
│       ├── datetime_utils.py  # Datum/Zeit Utilities
│       └── file_utils.py      # Datei-Utilities
│
├── scripts/                    # 🔄 CLI SCRIPTS (neu strukturiert)
│   ├── rag/                   # 🆕 RAG-spezifische Scripts
│   │   ├── collect_reddit_data.py
│   │   ├── process_embeddings.py
│   │   └── query_rag.py
│   └── financial/             # 🆕 Financial-spezifische Scripts
│       └── scrape_quarterlies.py
│
└── data/                      # 🔄 DATA STORAGE
    ├── rag/                   # 🆕 RAG-Daten
    │   └── processed/csv/
    ├── financial/             # 🆕 Financial-Daten
    │   ├── 10q_reports/
    │   └── financial_warehouse.db
    └── shared/                # 🆕 Gemeinsame Daten
        └── config/
```

## 🚀 **Neue Verwendung**

### **RAG-System (Reddit Sentiment Analysis):**
```bash
# Reddit-Daten sammeln
python scripts/rag/collect_reddit_data.py AAPL --limit 100

# Embeddings verarbeiten
python scripts/rag/process_embeddings.py aapl_20241201_143022

# RAG-Abfragen
python scripts/rag/query_rag.py "What is the sentiment around Tesla?"
```

### **Financial-System (SEC 10-Q Analysis):**
```bash
# SEC-Dokumente scrapen
python scripts/financial/scrape_quarterlies.py AAPL 2024 2 --fetch-all --extract

# Verfügbare Dokumente auflisten
python scripts/financial/scrape_quarterlies.py AAPL 2024 2 --list-docs
```

## 🔄 **Migration & Backward Compatibility**

### **Bestehender Code funktioniert weiterhin:**
- Backward-Compatibility-Funktionen in allen Modulen
- Alte Import-Pfade werden automatisch umgeleitet
- Schrittweise Migration möglich

### **Neue Imports (empfohlen):**
```python
# Alte Imports (funktionieren noch)
from app.data.reddit_client import collect
from app.data.financial_data_warehouse import FinancialDataWarehouse

# Neue Imports (empfohlen)
from app.rag.reddit_client import collect
from app.financial.data_warehouse import FinancialDataWarehouse
from app.core.logging import get_logger
from app.core.config import AppConfig
```

## 📊 **Vorteile der neuen Struktur**

### **✅ Wartbarkeit:**
- Klare Trennung von RAG und Financial Data
- Zentrale Konfiguration und Logging
- Modulare Architektur

### **✅ Skalierbarkeit:**
- Einfach neue Module hinzufügen
- Klare Verantwortlichkeiten
- Erweiterbare Struktur

### **✅ Testbarkeit:**
- Isolierte Module
- Zentrale Konfiguration
- Einfache Mock-Objekte

### **✅ Dokumentation:**
- Klare Verzeichnisstruktur
- Aktualisierte README-Dateien
- Strukturierte Dokumentation

## 🎯 **Nächste Schritte**

1. **Schrittweise Migration** auf neue Imports
2. **Tests schreiben** für neue Module
3. **Dokumentation erweitern** für neue Features
4. **Performance-Optimierung** der neuen Struktur

---

**🎉 Das Projekt ist jetzt besser strukturiert und bereit für zukünftige Erweiterungen!**
