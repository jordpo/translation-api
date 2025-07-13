from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import redis.asyncio as redis
from typing import Optional, List, Dict
import hashlib
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
import os

import config
from models import translation_model


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Global Redis client and thread pool
redis_client: Optional[redis.Redis] = None
thread_pool: Optional[ThreadPoolExecutor] = None
cache_semaphore = asyncio.Semaphore(100)  # Limit concurrent cache operations


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    global redis_client, thread_pool
    
    # Startup
    print("Loading translation model...")
    translation_model.load_model()
    
    # Create thread pool for CPU-bound operations
    thread_pool = ThreadPoolExecutor(max_workers=os.cpu_count() or 4)
    print(f"Thread pool created with {thread_pool._max_workers} workers")
    
    print("Connecting to Redis...")
    try:
        # Create Redis connection pool for better performance
        redis_client = redis.Redis(
            host=config.REDIS_HOST,
            port=config.REDIS_PORT,
            db=config.REDIS_DB,
            decode_responses=True,
            connection_pool=redis.ConnectionPool(
                host=config.REDIS_HOST,
                port=config.REDIS_PORT,
                db=config.REDIS_DB,
                max_connections=50,
                decode_responses=True
            )
        )
        await redis_client.ping()
        print("Redis connected successfully with connection pool")
    except Exception as e:
        print(f"Redis connection failed: {e}")
        print("WARNING: Running without Redis cache - translations will not be cached")
        redis_client = None
    
    yield
    
    # Shutdown
    if redis_client:
        await redis_client.close()
    if thread_pool:
        thread_pool.shutdown(wait=True)


app = FastAPI(
    title="Translation Service",
    version="1.0.0",
    lifespan=lifespan
)


# Request/Response models
class TranslationRequest(BaseModel):
    texts: List[str]
    value_ids: List[int]
    source_locale: str
    target_locale: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "texts": ["Hello world", "Welcome to our service"],
                "value_ids": [1, 2],
                "source_locale": "en",
                "target_locale": "es"
            }
        }


class TranslationResponse(BaseModel):
    translations: Dict[int, str]
    cached_count: int
    translated_count: int


# Pre-computed cache for hash keys to avoid repeated hashing
_cache_key_cache = {}

def get_cache_key(text: str, source_lang: str, target_lang: str) -> str:
    """Generate cache key for translation with memoization."""
    cache_tuple = (text, source_lang, target_lang)
    if cache_tuple not in _cache_key_cache:
        content = f"{text}:{source_lang}:{target_lang}"
        _cache_key_cache[cache_tuple] = f"translation:{hashlib.md5(content.encode()).hexdigest()}"
    return _cache_key_cache[cache_tuple]


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


@app.post("/translate", response_model=TranslationResponse)
async def translate(request: TranslationRequest):
    """Translate multiple texts with caching and batch processing."""
    # Validate input
    if len(request.texts) != len(request.value_ids):
        raise HTTPException(
            status_code=400,
            detail="Number of texts must match number of value_ids"
        )
    
    if request.source_locale not in config.SUPPORTED_LANGUAGES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported source language: {request.source_locale}"
        )
    
    if request.target_locale not in config.SUPPORTED_LANGUAGES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported target language: {request.target_locale}"
        )
    
    if not translation_model.is_loaded:
        raise HTTPException(
            status_code=503,
            detail="Translation model not loaded"
        )
    
    translations = {}
    cached_count = 0
    translated_count = 0
    
    # Items to translate (not found in cache)
    to_translate = []
    
    # Prepare cache keys and check Redis with pipelining for better performance
    cache_keys = []
    text_to_value_id = {}
    
    for text, value_id in zip(request.texts, request.value_ids):
        cache_key = get_cache_key(text, request.source_locale, request.target_locale)
        cache_keys.append(cache_key)
        text_to_value_id[text] = value_id
    
    # Batch cache check with Redis pipeline
    if redis_client:
        try:
            async with cache_semaphore:
                # Use mget for batch retrieval
                cached_results = await redis_client.mget(cache_keys)
                
                for idx, (text, value_id, cached_translation) in enumerate(zip(request.texts, request.value_ids, cached_results)):
                    if cached_translation:
                        translations[value_id] = cached_translation
                        cached_count += 1
                    else:
                        to_translate.append((idx, text, value_id))
        except Exception as e:
            logger.error(f"Redis batch error: {e}")
            # Fall back to adding all to translate queue
            to_translate = [(idx, text, value_id) for idx, (text, value_id) in enumerate(zip(request.texts, request.value_ids))]
    else:
        # No Redis, translate everything
        to_translate = [(idx, text, value_id) for idx, (text, value_id) in enumerate(zip(request.texts, request.value_ids))]
    
    # Translate in batches using the batch translation method
    batch_size = 16  # Smaller batches for better GPU memory management
    total_to_translate = len(to_translate)
    
    if total_to_translate > 0:
        logger.info(f"Translating {total_to_translate} texts in batches of {batch_size}")
    
    for i in range(0, total_to_translate, batch_size):
        batch = to_translate[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (total_to_translate + batch_size - 1) // batch_size
        
        logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} texts)")
        
        # Extract texts and value_ids for batch processing
        batch_texts = [item[1] for item in batch]
        batch_value_ids = [item[2] for item in batch]
        
        try:
            # Use batch translation for better performance
            batch_translations = await asyncio.to_thread(
                translation_model.translate_batch,
                batch_texts,
                request.source_locale,
                request.target_locale
            )
            
            # Process results and cache them
            cache_tasks = []
            for (idx, text, value_id), translated_text in zip(batch, batch_translations):
                translations[value_id] = translated_text
                translated_count += 1
                
                # Prepare cache tasks
                if redis_client and translated_text:
                    cache_key = get_cache_key(text, request.source_locale, request.target_locale)
                    cache_tasks.append(cache_translation(cache_key, translated_text, value_id))
            
            # Execute cache operations concurrently
            if cache_tasks:
                await asyncio.gather(*cache_tasks, return_exceptions=True)
                
        except Exception as e:
            logger.error(f"Batch translation error: {e}")
            # Fall back to individual translation for this batch
            for idx, text, value_id in batch:
                if value_id not in translations:
                    translations[value_id] = f"[Batch Error: {str(e)}]"
    
    return TranslationResponse(
        translations=translations,
        cached_count=cached_count,
        translated_count=translated_count
    )


async def cache_translation(cache_key: str, translated_text: str, value_id: int):
    """Cache a translation result."""
    if not redis_client:
        return
        
    try:
        async with cache_semaphore:
            await redis_client.setex(
                cache_key,
                30 * 24 * 3600,  # 30 days in seconds
                translated_text
            )
        logger.debug(f"Cached translation for value_id {value_id}")
    except Exception as e:
        logger.error(f"Failed to cache translation for value_id {value_id}: {e}")