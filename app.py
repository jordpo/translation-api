from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Translation Service", version="1.0.0")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "translation-service"}