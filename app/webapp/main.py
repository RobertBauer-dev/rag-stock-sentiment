#!/usr/bin/env python3
"""
FastAPI Web Application für Financial Data Visualization.
"""

from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import sys
import os
from pathlib import Path

# Add the data module to the path
sys.path.append(str(Path(__file__).parent.parent / "data"))

from app.data.warehouse_integration import ScrapingToWarehousePipeline
from app.financial.data_warehouse import FinancialDataWarehouse
import pandas as pd
import json
from typing import List, Dict, Any, Optional

# Initialize FastAPI app
app = FastAPI(title="Financial Data Visualization", version="1.0.0")

# Setup static files and templates
app.mount("/static", StaticFiles(directory="app/webapp/static"), name="static")
templates = Jinja2Templates(directory="app/webapp/templates")

# Initialize the data pipeline
pipeline = ScrapingToWarehousePipeline("data/financial_warehouse.db")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page with company selection."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/companies")
async def get_companies():
    """Get list of available companies."""
    try:
        with pipeline.warehouse.db_path.open() as conn:
            # This is a simplified version - in production you'd use proper SQLite connection
            pass
        
        # For now, return some example companies
        companies = [
            {"ticker": "AAPL", "name": "Apple Inc."},
            {"ticker": "MSFT", "name": "Microsoft Corporation"},
            {"ticker": "GOOGL", "name": "Alphabet Inc."},
            {"ticker": "TSLA", "name": "Tesla Inc."},
            {"ticker": "AMZN", "name": "Amazon.com Inc."}
        ]
        return JSONResponse(content={"companies": companies})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/company/{ticker}/revenue")
async def get_company_revenue(ticker: str, quarters: int = 8):
    """
    Get revenue data for a company over multiple quarters.
    
    Args:
        ticker (str): Stock ticker symbol
        quarters (int): Number of quarters to retrieve (default: 8)
    
    Returns:
        JSONResponse: Revenue data for charting
    """
    try:
        # Get quarterly revenue data
        revenue_data = pipeline.warehouse.get_quarterly_comparison(ticker, "Revenue", quarters=quarters)
        
        if revenue_data.empty:
            # If no data found, return empty data instead of scraping
            return JSONResponse(content={
                "error": f"No revenue data found for {ticker}. Please use 'Scrape New Data' to fetch data first.",
                "data": [],
                "labels": [],
                "quarters": [],
                "ticker": ticker,
                "unit": "Millions USD"
            })
        
        # Process the data for charting
        chart_data = []
        labels = []
        quarters_list = []
        
        for _, row in revenue_data.iterrows():
            if row['values'] and len(row['values']) > 0:
                # Take the first value (most recent period)
                value = row['values'][0]
                if isinstance(value, (int, float)) and value > 0:
                    chart_data.append(value / 1000000)  # Convert to millions
                    labels.append(f"{row['year']} Q{row['quarter']}")
                    quarters_list.append(f"{row['year']}Q{row['quarter']}")
        
        # Reverse to show oldest to newest
        chart_data.reverse()
        labels.reverse()
        quarters_list.reverse()
        
        return JSONResponse(content={
            "ticker": ticker,
            "data": chart_data,
            "labels": labels,
            "quarters": quarters_list,
            "unit": "Millions USD"
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting revenue data for {ticker}: {e}")
        return JSONResponse(content={
            "error": f"Error retrieving data for {ticker}: {str(e)}",
            "data": [],
            "labels": [],
            "quarters": [],
            "ticker": ticker,
            "unit": "Millions USD"
        }, status_code=500)

@app.get("/api/company/{ticker}/financials")
async def get_company_financials(ticker: str, quarters: int = 4):
    """
    Get comprehensive financial data for a company.
    
    Args:
        ticker (str): Stock ticker symbol
        quarters (int): Number of quarters to retrieve
    
    Returns:
        JSONResponse: Comprehensive financial data
    """
    try:
        # Get key financial metrics
        metrics = ['Revenue', 'Net Income', 'Total Assets', 'Total Liabilities']
        financial_data = {}
        
        for metric in metrics:
            data = pipeline.warehouse.get_quarterly_comparison(ticker, metric, quarters=quarters)
            if not data.empty:
                values = []
                labels = []
                for _, row in data.iterrows():
                    if row['values'] and len(row['values']) > 0:
                        value = row['values'][0]
                        if isinstance(value, (int, float)):
                            values.append(value / 1000000)  # Convert to millions
                            labels.append(f"{row['year']} Q{row['quarter']}")
                
                financial_data[metric] = {
                    "values": values[::-1],  # Reverse for chronological order
                    "labels": labels[::-1]
                }
        
        return JSONResponse(content={
            "ticker": ticker,
            "financials": financial_data,
            "unit": "Millions USD"
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/scrape")
async def scrape_company_data(ticker: str = Form(...), quarters: int = Form(4)):
    """
    Scrape financial data for a company.
    
    Args:
        ticker (str): Stock ticker symbol
        quarters (int): Number of quarters to scrape
    
    Returns:
        JSONResponse: Scraping results
    """
    try:
        # Generate quarters to scrape (last N quarters)
        from datetime import datetime
        current_year = datetime.now().year
        quarters_to_scrape = []
        
        for year in [current_year, current_year - 1, current_year - 2]:
            for quarter in [4, 3, 2, 1]:
                quarters_to_scrape.append({'year': year, 'quarter': quarter})
                if len(quarters_to_scrape) >= quarters:
                    break
            if len(quarters_to_scrape) >= quarters:
                break
        
        # Scrape the data
        results = pipeline.scrape_multiple_quarters(ticker, quarters_to_scrape)
        
        successful = sum(results.values())
        total = len(results)
        
        return JSONResponse(content={
            "ticker": ticker,
            "results": results,
            "successful": successful,
            "total": total,
            "message": f"Scraped {successful}/{total} quarters successfully"
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/company/{ticker}/kpis")
async def get_company_kpis(ticker: str, quarters: int = 8):
    """
    Get KPIs for a company.
    
    Args:
        ticker (str): Stock ticker symbol
        quarters (int): Number of quarters to retrieve
    
    Returns:
        JSONResponse: KPI data
    """
    try:
        # Get all KPIs for the company
        kpis_df = pipeline.warehouse.get_kpis(ticker)
        
        if kpis_df.empty:
            return JSONResponse(content={
                "error": f"No KPI data found for {ticker}",
                "kpis": {},
                "ticker": ticker
            })
        
        # Group KPIs by name and create trend data
        kpi_data = {}
        for kpi_name in kpis_df['kpi_name'].unique():
            kpi_trend = pipeline.warehouse.get_kpi_trends(ticker, kpi_name, quarters)
            if not kpi_trend.empty:
                kpi_data[kpi_name] = {
                    "values": kpi_trend['value'].tolist()[::-1],  # Reverse for chronological order
                    "labels": [f"{row['year']} Q{row['quarter']}" for _, row in kpi_trend.iterrows()][::-1],
                    "unit": kpi_trend['unit'].iloc[0] if len(kpi_trend) > 0 else "USD"
                }
        
        return JSONResponse(content={
            "ticker": ticker,
            "kpis": kpi_data,
            "total_kpis": len(kpi_data)
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting KPIs for {ticker}: {e}")
        return JSONResponse(content={
            "error": f"Error retrieving KPIs for {ticker}: {str(e)}",
            "kpis": {},
            "ticker": ticker
        }, status_code=500)

@app.get("/api/company/{ticker}/kpi/{kpi_name}")
async def get_specific_kpi(ticker: str, kpi_name: str, quarters: int = 8):
    """
    Get a specific KPI for a company.
    
    Args:
        ticker (str): Stock ticker symbol
        kpi_name (str): KPI name (e.g., 'Revenue', 'Gross Margin')
        quarters (int): Number of quarters to retrieve
    
    Returns:
        JSONResponse: Specific KPI data
    """
    try:
        kpi_trend = pipeline.warehouse.get_kpi_trends(ticker, kpi_name, quarters)
        
        if kpi_trend.empty:
            return JSONResponse(content={
                "error": f"No {kpi_name} data found for {ticker}",
                "data": [],
                "labels": [],
                "ticker": ticker,
                "kpi_name": kpi_name
            })
        
        # Process the data for charting
        values = kpi_trend['value'].tolist()[::-1]  # Reverse for chronological order
        labels = [f"{row['year']} Q{row['quarter']}" for _, row in kpi_trend.iterrows()][::-1]
        unit = kpi_trend['unit'].iloc[0] if len(kpi_trend) > 0 else "USD"
        
        return JSONResponse(content={
            "ticker": ticker,
            "kpi_name": kpi_name,
            "data": values,
            "labels": labels,
            "unit": unit
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting {kpi_name} for {ticker}: {e}")
        return JSONResponse(content={
            "error": f"Error retrieving {kpi_name} for {ticker}: {str(e)}",
            "data": [],
            "labels": [],
            "ticker": ticker,
            "kpi_name": kpi_name
        }, status_code=500)

@app.get("/api/stats")
async def get_database_stats():
    """Get database statistics."""
    try:
        stats = pipeline.warehouse.get_database_stats()
        return JSONResponse(content=stats)
    except Exception as e:
        logger.error(f"❌ Error getting database stats: {e}")
        return JSONResponse(content={
            "error": f"Error retrieving database statistics: {str(e)}",
            "companies": 0,
            "filings": 0,
            "financial_data_points": 0
        }, status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
