# RAG Stock Sentiment Analysis

Eine FastAPI-Anwendung zur Analyse von Aktien-Sentiment basierend auf Reddit-Posts mit RAG (Retrieval-Augmented Generation).

## 🏛️ Architektur

```mermaid
graph TD
    subgraph Frontend
        A["index.html<br/>(Web UI)"]
    end
    
    subgraph FastAPI Backend
        B["main.py<br/>(FastAPI App)"]
        C["api/routes.py<br/>(API Endpoints)"]
        D["data/reddit_client.py<br/>(Reddit Fetch)"]
        E["embedding/embed_posts.py<br/>(Embeddings)"]
        F["vector_store/client.py<br/>(Qdrant Client)"]
        G["rag/query_engine.py<br/>(RAG Engine)"]
        H["llm/generator.py<br/>(LLM Generator)"]
        I["utils/<br/>(Utilities)"]
    end
    
    subgraph Scripts
        J["scripts/collect_reddit_data.py<br/>(CLI Data Collection)"]
        K["scripts/process_embeddings.py<br/>(CLI Embedding Processing)"]
        L["scripts/query_rag.py<br/>(CLI RAG Queries)"]
    end
    
    subgraph External Services
        M["Reddit API"]
        N["Qdrant<br/>(Vector DB)"]
        O["OpenAI API<br/>(LLM)"]
    end
    
    subgraph Data Storage
        P["data/processed/csv<br/>(Temporary CSV)"]
        Q["Qdrant<br/>(Single Source of Truth)"]
    end

    %% Web Interface Flow
    A -- HTTP (Form/API) --> B
    B -- include_router --> C
    
    %% API Data Collection Flow
    C -- collect-data --> D
    D -- fetches --> M
    D -- saves CSV --> P
    C -- process-embeddings --> E
    E -- reads CSV --> P
    E -- generates embeddings --> F
    F -- uploads to Qdrant --> N
    F -- stores all data --> Q
    
    %% API Query Flow
    C -- query --> G
    G -- search vectors --> N
    G -- calls LLM --> H
    H -- OpenAI API --> O
    G -- returns answer --> C
    C -- API Response --> A
    
    %% CLI Scripts Flow
    J -- collects data --> D
    K -- processes embeddings --> E
    L -- queries RAG --> G
    
    %% Collection Management
    M2["manage_collections.py<br/>(Collection Management)"] -. manages .-> Q
    
    %% Utilities
    I -. utilities .-> D
    I -. utilities .-> E
    I -. utilities .-> G
```


## 🏗️ Projektstruktur

```
app/
├── api/                    # API-Endpunkte
│   ├── __init__.py
│   └── routes.py          # FastAPI Router
├── data/                   # Datenverarbeitung
│   ├── __init__.py
│   └── reddit_client.py   # Reddit API Client
├── embedding/              # Embedding-Verarbeitung
│   ├── __init__.py
│   └── embed_posts.py     # Embedding-Generierung
├── llm/                    # LLM-Integration
│   ├── __init__.py
│   └── generator.py       # OpenAI Integration
├── rag/                    # RAG-System
│   ├── __init__.py
│   └── query_engine.py    # RAG Query Engine
├── vector_store/           # Vector Store
│   ├── __init__.py
│   └── client.py          # Qdrant Client
├── utils/                  # Hilfsfunktionen
│   ├── __init__.py
│   ├── datetime_utils.py  # Datum/Zeit Utilities
│   └── file_utils.py      # Datei-Utilities
├── templates/              # HTML Templates
│   └── index.html         # Web Interface
└── main.py                # FastAPI App

scripts/                   # Ausführbare Scripts
├── collect_reddit_data.py # Reddit-Daten sammeln
├── process_embeddings.py  # Embeddings verarbeiten
├── query_rag.py          # RAG-Abfragen
└── manage_collections.py  # Qdrant-Collections verwalten

data/                      # Datenverzeichnis
├── processed/
│   └── csv/              # Temporäre CSV-Dateien (werden in Qdrant gespeichert)
```

## 🚀 Schnellstart

### 1. API starten

```bash
# Von Root-Verzeichnis
uvicorn app.main:app --reload

# Oder von app-Verzeichnis
cd app
uvicorn main:app --reload
```

### 2. Web-Interface öffnen

http://127.0.0.1:8000

### 3. Qdrant Server starten

```bash
docker run -p 6333:6333 qdrant/qdrant
```

## 📋 API-Endpunkte

- `GET /` - Web-Interface für Stock Sentiment Analysis
- `POST /api/collect-data` - Startet Daten-Sammlung für eine Aktie
- `GET /api/pipeline-status/{collection_name}` - Pipeline-Status abfragen
- `POST /api/query` - RAG-Abfrage für Stock Sentiment
- `GET /api/collections` - Verfügbare Datensammlungen auflisten

## 🛠️ Scripts verwenden

### Reddit-Daten sammeln

```bash
python scripts/collect_reddit_data.py AAPL --limit 100
python scripts/collect_reddit_data.py TSLA --query "Tesla earnings" --limit 50
```

### Embeddings verarbeiten

```bash
# Verfügbare Datasets auflisten
python scripts/process_embeddings.py --list-available

# Embeddings für Dataset verarbeiten
python scripts/process_embeddings.py aapl_20241201_143022
```

### Collections verwalten

```bash
# Alle Collections auflisten
python scripts/manage_collections.py list

# Collection-Informationen anzeigen
python scripts/manage_collections.py info aapl_20241201_143022

# Collection zu CSV exportieren
python scripts/manage_collections.py export aapl_20241201_143022

# Collection löschen
python scripts/manage_collections.py delete aapl_20241201_143022
```

### RAG-Abfragen

```bash
python scripts/query_rag.py "What is the sentiment around Tesla?" --collection tesla_20241201_143022 --show-context
```

## 📊 Verwendungsbeispiel

### 1. Daten sammeln

```bash
# Über Web-Interface oder API
curl -X POST "http://localhost:8000/api/collect-data" \
  -H "Content-Type: application/json" \
  -d '{
    "stock_symbol": "TSLA",
    "search_query": "Tesla earnings",
    "limit": 50
  }'
```

### 2. Sentiment abfragen

```bash
curl -X POST "http://localhost:8000/api/query" \
  -H "Content-Type: application/json" \
  -d '{
    "stock_symbol": "TSLA",
    "question": "What is the sentiment around Tesla'\''s recent earnings?",
    "top_k": 5
  }'
```

## 🔧 Konfiguration

### Umgebungsvariablen (.env)

```bash
# Reddit API
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=your_user_agent

# OpenAI API
OPENAI_API_KEY=your_openai_api_key
```

## 🛑 App beenden

```bash
# Port 8000 finden und beenden
lsof -i :8000
kill -9 <PID>

# Oder alle uvicorn Prozesse beenden
pkill -f "uvicorn"
```

## 📈 MLflow Tracking

Das Projekt verwendet MLflow für Experiment-Tracking:

- Embedding-Generierung wird automatisch getrackt
- Parameter und Metriken werden gespeichert
- Artefakte (CSV, Embeddings) werden geloggt

## 🔄 Workflow

1. **Daten sammeln**: Reddit-Posts zu einer Aktie abrufen (temporär als CSV)
2. **Embeddings generieren**: Posts in Vektoren umwandeln
3. **Qdrant speichern**: Embeddings + Metadaten in Qdrant als Single Source of Truth
4. **RAG-Abfragen**: Ähnliche Posts finden und LLM-Antworten generieren
5. **Daten exportieren**: Bei Bedarf Daten aus Qdrant exportieren

## 💾 Datenmanagement

**Qdrant als Single Source of Truth:**
- Alle Daten (Embeddings + Metadaten) werden in Qdrant gespeichert
- CSV-Dateien sind nur temporär für die Verarbeitung
- NPY-Dateien werden nicht mehr gespeichert (redundant)
- Bei Bedarf können Daten aus Qdrant exportiert werden
```
