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
- **R3.htm** - Part I, Item 1 (Financial Statements)
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
- **R14-R20** - Income Statement, Balance Sheet, Cash Flow Statement
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
3. **R3.htm** - Part I, Item 1 (Financial Statements)

### Priorität 2 (Strukturierte Abschnitte):
- **R14-R20** - Wahrscheinlich die Financial Statements Abschnitte
- **R21-R30** - Notes to Financial Statements

### Priorität 3 (Fallback):
- **R1.htm** - Cover Page (enthält oft Zusammenfassungen)
- **R4.htm** - Management's Discussion (enthält Financial Highlights)

## 🔧 Verwendung im Script

Das `scrape_quarterlies.py` Script priorisiert automatisch:

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

---

*Erstellt für das RAG Stock Sentiment Projekt - SEC 10-Q Financial Data Extraction*
