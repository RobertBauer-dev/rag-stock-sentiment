# app/api/routes.py
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict
import asyncio
import threading
from datetime import datetime

from app.data.reddit_client import collect as collect_reddit_data
from app.rag.query_engine import search_similar_posts, generate_answer_from_context
from app.embedding.embed_posts import process_and_store_embeddings

router = APIRouter()

# Data models
class StockRequest(BaseModel):
    stock_symbol: str
    search_query: Optional[str] = None
    limit: Optional[int] = 50

class QueryRequest(BaseModel):
    stock_symbol: str
    question: str
    top_k: Optional[int] = 5

class PipelineResponse(BaseModel):
    status: str
    message: str
    collection_name: Optional[str] = None
    timestamp: str

# Global storage for pipeline status
pipeline_status = {}

@router.get("/")
async def root():
    return {"message": "RAG Stock Sentiment API is running."}

@router.post("/collect-data", response_model=PipelineResponse)
async def collect_stock_data(request: StockRequest, background_tasks: BackgroundTasks):
    """
    Start the data collection pipeline for a stock.
    This will fetch Reddit posts, process them, and store embeddings.
    """
    stock_symbol = request.stock_symbol.upper()
    search_query = request.search_query or f"{stock_symbol} stock"
    limit = request.limit or 50
    collection_name = f"{stock_symbol.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Update status
    pipeline_status[collection_name] = {
        "status": "starting",
        "message": f"Starting data collection for {stock_symbol}",
        "timestamp": datetime.now().isoformat()
    }
    
    # Start background task
    background_tasks.add_task(
        run_data_pipeline, 
        stock_symbol, 
        search_query, 
        limit, 
        collection_name
    )
    
    return PipelineResponse(
        status="started",
        message=f"Data collection pipeline started for {stock_symbol}",
        collection_name=collection_name,
        timestamp=datetime.now().isoformat()
    )

@router.get("/pipeline-status/{collection_name}")
async def get_pipeline_status(collection_name: str):
    """
    Get the status of a data collection pipeline.
    """
    if collection_name not in pipeline_status:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    
    return pipeline_status[collection_name]

@router.post("/query")
async def query_stock_sentiment(request: QueryRequest):
    """
    Query the sentiment analysis for a specific stock using the RAG system.
    """
    stock_symbol = request.stock_symbol.upper()
    question = request.question
    top_k = request.top_k or 5
    
    # Try to find the most recent collection for this stock
    collection_name = find_latest_collection(stock_symbol)
    if not collection_name:
        raise HTTPException(
            status_code=404, 
            detail=f"No data found for {stock_symbol}. Please run data collection first."
        )
    
    try:
        # Search for similar posts
        context = search_similar_posts(question, collection_name, top_k)
        
        # Generate answer
        answer = generate_answer_from_context(question, context)
        
        return {
            "stock_symbol": stock_symbol,
            "question": question,
            "answer": answer,
            "context_posts": len(context),
            "collection_name": collection_name,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@router.get("/collections")
async def list_collections():
    """
    List all available data collections.
    """
    # This would typically query your vector store for available collections
    # For now, return the pipeline status keys
    return {
        "collections": list(pipeline_status.keys()),
        "total": len(pipeline_status)
    }

def find_latest_collection(stock_symbol: str) -> Optional[str]:
    """
    Find the most recent collection for a given stock symbol.
    """
    stock_collections = [
        name for name in pipeline_status.keys() 
        if name.startswith(stock_symbol.lower())
    ]
    
    if not stock_collections:
        return None
    
    # Return the most recent one (assuming timestamp format)
    return sorted(stock_collections)[-1]

async def run_data_pipeline(stock_symbol: str, search_query: str, limit: int, collection_name: str):
    """
    Run the complete data pipeline in the background.
    """
    try:
        # Step 1: Update status
        pipeline_status[collection_name]["status"] = "collecting_data"
        pipeline_status[collection_name]["message"] = f"Collecting Reddit data for {stock_symbol}"
        
        # Step 2: Collect Reddit data
        collect_reddit_data(search_query, collection_name, limit)
        
        # Step 3: Update status
        pipeline_status[collection_name]["status"] = "processing_embeddings"
        pipeline_status[collection_name]["message"] = f"Processing embeddings for {stock_symbol}"
        
        # Step 4: Process and store embeddings
        process_and_store_embeddings(collection_name)
        
        # Step 5: Update status to completed
        pipeline_status[collection_name]["status"] = "completed"
        pipeline_status[collection_name]["message"] = f"Pipeline completed for {stock_symbol}"
        pipeline_status[collection_name]["timestamp"] = datetime.now().isoformat()
        
    except Exception as e:
        # Update status to failed
        pipeline_status[collection_name]["status"] = "failed"
        pipeline_status[collection_name]["message"] = f"Pipeline failed: {str(e)}"
        pipeline_status[collection_name]["timestamp"] = datetime.now().isoformat()
