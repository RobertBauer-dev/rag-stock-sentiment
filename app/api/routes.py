# app/api/routes.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def root():
    return {"message": "RAG Stock Sentiment API is running."}
