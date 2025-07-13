from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import redis.asyncio as redis
from typing import Optional
import hashlib
import json

import config
from models import translation_model


# Global Redis client
redis_client: Optional[redis.Redis] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    global redis_client
    
    # Startup
    print("Loading translation model...")
    translation_model.load_model()
    
    print("Connecting to Redis...")
    redis_client = redis.Redis(
        host=config.REDIS_HOST,
        port=config.REDIS_PORT,
        db=config.REDIS_DB,
        decode_responses=True
    )
    
    try:
        await redis_client.ping()
        print("Redis connected successfully")
    except Exception as e:
        print(f"Redis connection failed: {e}")
        redis_client = None
    
    yield
    
    # Shutdown
    if redis_client:
        await redis_client.close()


app = FastAPI(
    title="Translation Service",
    version="1.0.0",
    lifespan=lifespan
)


def get_cache_key(text: str, source_lang: str, target_lang: str) -> str:
    """Generate cache key for translation."""
    content = f"{text}:{source_lang}:{target_lang}"
    return f"translation:{hashlib.md5(content.encode()).hexdigest()}"


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    redis_status = "connected"
    if redis_client:
        try:
            await redis_client.ping()
        except:
            redis_status = "disconnected"
    else:
        redis_status = "not initialized"
    
    return {
        "status": "healthy",
        "service": "translation-service",
        "model": {
            "loaded": translation_model.is_loaded,
            "name": config.MODEL_NAME if translation_model.is_loaded else None
        },
        "redis": redis_status,
        "supported_languages": config.SUPPORTED_LANGUAGES
    }