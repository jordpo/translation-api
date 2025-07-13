# Translation Service

A FastAPI-based translation service that will handle translation requests from Phoenix applications.

## Setup

### Prerequisites
- Python 3.8 or higher
- Redis server (for caching)

### Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the Service

Start the FastAPI server:
```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

The service will be available at `http://localhost:8000`

### API Endpoints

#### Health Check
- `GET /health` - Returns service status, model info, and supported languages

#### Translation Endpoint
- `POST /translate` - Translate multiple texts with caching support

**Request payload:**
```json
{
  "texts": ["Hello world", "Welcome"],
  "value_ids": [1, 2],
  "source_locale": "en",
  "target_locale": "es"
}
```

**Response:**
```json
{
  "translations": {
    "1": "Hola mundo",
    "2": "Bienvenido"
  },
  "cached_count": 0,
  "translated_count": 2
}
```

**Features:**
- Batch processing (up to 16 texts per batch)
- Redis caching with 30-day TTL
- Connection pooling for high performance
- Supports 20+ languages (see `/health` for full list)

**Supported language codes:**
`en`, `es`, `fr`, `de`, `it`, `pt`, `ru`, `zh`, `ja`, `ko`, `ar`, `hi`, `nl`, `pl`, `tr`, `vi`, `th`, `sv`, `cs`, `el`

- API documentation available at `http://localhost:8000/docs`

### Development

The service uses:
- **FastAPI** for the web framework
- **Transformers** and **Torch** for translation models
- **Redis** for caching translations
- **Pydantic** for data validation