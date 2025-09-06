"""
Centralized configuration for the application.
"""

import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class AppConfig:
    """Centralized application configuration."""
    
    # Project paths
    ROOT_DIR = Path(__file__).resolve().parent.parent.parent
    APP_DIR = ROOT_DIR / "app"
    DATA_DIR = ROOT_DIR / "data"
    SCRIPTS_DIR = ROOT_DIR / "scripts"
    
    # Data subdirectories
    RAG_DATA_DIR = DATA_DIR / "rag" / "processed" / "csv"
    FINANCIAL_DATA_DIR = DATA_DIR / "financial"
    SEC_REPORTS_DIR = FINANCIAL_DATA_DIR / "10q_reports"
    WAREHOUSE_DB_PATH = FINANCIAL_DATA_DIR / "financial_warehouse.db"
    
    # Reddit API Configuration
    REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
    REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
    REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT")
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # SEC API Configuration
    SEC_HEADERS = {"User-Agent": "Dr. Robert Bauer dr.robert.bauer@icloud.com"}
    
    # Qdrant Configuration
    QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
    QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
    
    # Embedding Configuration
    DEFAULT_EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    
    # Web App Configuration
    WEBAPP_HOST = os.getenv("WEBAPP_HOST", "0.0.0.0")
    WEBAPP_PORT = int(os.getenv("WEBAPP_PORT", "8000"))
    
    # Logging Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = DATA_DIR / "app.log"
    
    @classmethod
    def ensure_directories(cls):
        """Ensure all required directories exist."""
        directories = [
            cls.DATA_DIR,
            cls.RAG_DATA_DIR,
            cls.FINANCIAL_DATA_DIR,
            cls.SEC_REPORTS_DIR,
            cls.DATA_DIR / "shared" / "config"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def get_reddit_config(cls) -> Dict[str, str]:
        """Get Reddit API configuration."""
        return {
            "client_id": cls.REDDIT_CLIENT_ID,
            "client_secret": cls.REDDIT_CLIENT_SECRET,
            "user_agent": cls.REDDIT_USER_AGENT
        }
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate that required configuration is present."""
        required_vars = [
            cls.REDDIT_CLIENT_ID,
            cls.REDDIT_CLIENT_SECRET,
            cls.REDDIT_USER_AGENT,
            cls.OPENAI_API_KEY
        ]
        
        missing_vars = [var for var in required_vars if not var]
        
        if missing_vars:
            print(f"❌ Missing required environment variables: {missing_vars}")
            return False
        
        return True


# Initialize directories on import
AppConfig.ensure_directories()
