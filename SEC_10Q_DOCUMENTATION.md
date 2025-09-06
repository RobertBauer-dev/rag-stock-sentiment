# SEC 10-Q Filing Dokumentation

## 📋 Überblick

Dieses Dokument erklärt die Struktur von SEC 10-Q Filings und die verschiedenen verfügbaren Dokumenttypen, die beim Herunterladen von Quartalsberichten verfügbar sind.

## 🏗️ Dokumentstruktur eines 10-Q Filings

### Hauptdokumente

| Datei | Beschreibung |
|-------|-------------|
| `{ticker}-{date}.htm` | **Hauptdokument** des 10-Q Reports (enthält die vollständigen Financial Statements) |
| `a10-qexhibit311{date}.htm` | Exhibit 31.1 (CEO Certification) |
| `a10-qexhibit312{date}.htm` | Exhibit 31.2 (CFO Certification) |
| `a10-qexhibit321{date}.htm` | Exhibit 32 (Certification under Section 906) |

### Strukturierte Abschnitte (R1.htm bis R48.htm)

Die **R1.htm bis R48.htm** Dateien sind die strukturierten Abschnitte des 10-Q Reports:

#### Standard-Abschnitte:
- **R1.htm** - Cover Page (Titelseite)
- **R2.htm** - Table of Contents (Inhaltsverzeichnis)

#### Part I - Financial Information:
- **<span style="color: #ff6b6b; font-weight: bold;">R3.htm - Part I, Item 1 (Financial Statements)</span>** 🎯
- **R4.htm** - Part I, Item 2 (Management's Discussion and Analysis)
- **R5.htm** - Part I, Item 3 (Quantitative and Qualitative Disclosures about Market Risk)
- **R6.htm** - Part I, Item 4 (Controls and Procedures)

#### Part II - Other Information:
- **R7.htm** - Part II, Item 1 (Legal Proceedings)
- **R8.htm** - Part II, Item 1A (Risk Factors)
- **R9.htm** - Part II, Item 2 (Unregistered Sales of Equity Securities)
- **R10.htm** - Part II, Item 3 (Defaults Upon Senior Securities)
- **R11.htm** - Part II, Item 4 (Mine Safety Disclosures)
- **R12.htm** - Part II, Item 5 (Other Information)
- **R13.htm** - Part II, Item 6 (Exhibits)

#### Financial Statements (R14-R48):
- **<span style="color: #4ecdc4; font-weight: bold;">R14-R20 - Income Statement, Balance Sheet, Cash Flow Statement</span>** 🎯
- **R21-R30** - Notes to Financial Statements
- **R31-R48** - Supplementary Information und zusätzliche Details

### Index- und Metadaten-Dateien

| Datei | Beschreibung |
|-------|-------------|
| `{cik}-{accession}-index.html` | Hauptindex des Filings |
| `{cik}-{accession}-index-headers.html` | Header-Informationen |
| `{cik}-{accession}.txt` | Vollständiger Text des Filings |
| `FilingSummary.xml` | Zusammenfassung des Filings |
| `MetaLinks.json` | Verknüpfungen zwischen Dokumenten |

### XBRL-Dateien (Strukturierte Daten)

| Datei | Beschreibung |
|-------|-------------|
| `{cik}-{accession}-xbrl.zip` | Maschinenlesbare Financial Data |
| `{ticker}-{date}_cal.xml` | XBRL Calculation Linkbase |
| `{ticker}-{date}_def.xml` | XBRL Definition Linkbase |
| `{ticker}-{date}_lab.xml` | XBRL Label Linkbase |
| `{ticker}-{date}_pre.xml` | XBRL Presentation Linkbase |
| `{ticker}-{date}_htm.xml` | XBRL HTML Mapping |
| `{ticker}-{date}.xsd` | XBRL Schema Definition |

### Excel-Report
- **`Financial_Report.xlsx`** - Financial Statements als Excel-Datei (oft die beste Quelle für strukturierte Daten)

### Styling und Scripts
- **`report.css`** - CSS-Styling für HTML-Dokumente
- **`Show.js`** - JavaScript für interaktive Funktionen

## 🎯 Empfohlene Dateien für Financial Statements Extraktion

### Priorität 1 (Beste Quellen):
1. **`{ticker}-{date}.htm`** - Vollständiges Hauptdokument
2. **`Financial_Report.xlsx`** - Bereits strukturierte Financial Data
3. **<span style="color: #ff6b6b; font-weight: bold;">R3.htm - Part I, Item 1 (Financial Statements)</span>** 🎯 **MUSS GESCRAPED WERDEN**

### Priorität 1.5 (Kritische Financial Statements):
4. **<span style="color: #4ecdc4; font-weight: bold;">R14-R20 - Income Statement, Balance Sheet, Cash Flow Statement</span>** 🎯 **MUSS GESCRAPED WERDEN**

### Priorität 2 (Strukturierte Abschnitte):
- **R14-R20** - Wahrscheinlich die Financial Statements Abschnitte
- **R21-R30** - Notes to Financial Statements

### Priorität 3 (Fallback):
- **R1.htm** - Cover Page (enthält oft Zusammenfassungen)
- **R4.htm** - Management's Discussion (enthält Financial Highlights)

## 🔧 Verwendung im Script

Das `scripts/financial/scrape_quarterlies.py` Script priorisiert automatisch:

1. **Hauptdokumente** mit "10-q" im Namen
2. **Fallback** auf das erste verfügbare .htm Dokument
3. **Liste aller verfügbaren Dokumente** für manuelle Auswahl

### Beispiel-Output:
```
📋 Available documents for AAPL 2024Q2:
   - aapl-20240629.htm                    ← Hauptdokument (beste Wahl)
   - Financial_Report.xlsx               ← Excel-Report (sehr gut)
   - R1.htm                              ← Cover Page
   - R3.htm                              ← Financial Statements
   - R14.htm                             ← Wahrscheinlich Income Statement
   - R15.htm                             ← Wahrscheinlich Balance Sheet
   - R16.htm                             ← Wahrscheinlich Cash Flow
   - a10-qexhibit31106292024.htm         ← CEO Certification
   - ...
```

## 📊 XBRL Alternative

Für maschinenlesbare Financial Data können Sie auch die XBRL-Dateien verwenden:
- **`{cik}-{accession}-xbrl.zip`** enthält strukturierte XML-Dateien
- Diese sind standardisiert und einfacher zu parsen
- Enthalten alle Financial Statement Items mit eindeutigen Tags

## 🚀 Nächste Schritte

1. **Script anpassen** um `aapl-{date}.htm` oder `Financial_Report.xlsx` zu bevorzugen
2. **XBRL-Parser** für strukturierte Daten implementieren
3. **Multiple Quellen** kombinieren für robuste Extraktion

## 🎨 Logging Features

Das Script verwendet ein erweiterte farbige Logging-System mit intelligenten Emojis:

### Farbkodierung der Log-Komponenten:
- **🔵 Timestamp** (Blau) - Zeitstempel der Log-Nachricht
- **🟣 Logger Name** (Magenta) - Name des Loggers (z.B. 'scrape_quarterlies')
- **🟢 INFO Level** (Grün) - Informations-Level
- **🟡 WARNING Level** (Gelb) - Warnungs-Level
- **🔴 ERROR Level** (Rot) - Fehler-Level
- **🔴 CRITICAL Level** (Hellrot) - Kritischer Fehler-Level
- **🔵 Function Info** (Cyan) - Funktionsname und Zeilennummer

### Intelligente Emoji-Zuordnung:
- **🔎 CIK/Ticker Lookup** - Suchen nach Firmen-IDs
- **✅ Success/Found/Saved** - Erfolgreiche Operationen
- **📥 Fetching/Downloading/Processing** - Datenübertragung
- **💰 Financial/Income/Balance/Cash Flow** - Finanzdaten
- **📊 Tables/Extracting/Parsing** - Datenverarbeitung
- **❌ Errors/Failed/Exceptions** - Fehler und Probleme
- **⚠️ Warnings/Cautions/Fallbacks** - Warnungen
- **🚀 Starting/Completed/Finished** - Prozess-Status
- **📋 Listing/Available/Documents** - Dokumenten-Listen
- **🌐 Network/Connection/Timeout** - Netzwerk-Operationen
- **📁 Files/Paths/Directories** - Dateisystem-Operationen
- **📄 JSON/Data/Metadata** - Datenstrukturen
- **🔍 Debug Information** - Debugging-Details
- **ℹ️ General Info** - Allgemeine Informationen
- **🚨 Critical Issues** - Kritische Probleme

### Beispiel-Logs:
```
2025-09-05 23:15:20 - scrape_quarterlies - INFO - get_cik_from_ticker:79 - 🔎 Looking up CIK for ticker: AAPL
2025-09-05 23:15:20 - scrape_quarterlies - INFO - fetch_10q_by_quarter:200 - 📥 Fetching 10-Q for AAPL 2024Q2
2025-09-05 23:15:20 - scrape_quarterlies - INFO - extract_financial_statements:544 - 💰 Found income statement in table 28
2025-09-05 23:15:20 - scrape_quarterlies - INFO - extract_table_data:475 - ✅ Successfully extracted 25 items from income_statement
```

### Log-Dateien:
- **Console**: Farbige Ausgabe mit Emojis für bessere Lesbarkeit
- **File**: `data/10q_reports/scrape_quarterlies.log` - Vollständige Logs ohne Farben/Emojis

---

*Erstellt für das RAG Stock Sentiment Projekt - SEC 10-Q Financial Data Extraction*
