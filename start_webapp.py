#!/usr/bin/env python3
"""
Start script for the Financial Data Visualization Web Application.
"""

import uvicorn
import sys
import os
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent / "app"))

if __name__ == "__main__":
    print("🚀 Starting Financial Data Visualization Web Application...")
    print("📊 Access the application at: http://localhost:8000")
    print("🔄 Press Ctrl+C to stop the server")
    print("=" * 60)
    
    # Start the FastAPI application
    uvicorn.run(
        "webapp.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload for development
        log_level="info"
    )
