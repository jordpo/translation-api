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

- `GET /health` - Health check endpoint
- API documentation available at `http://localhost:8000/docs`

### Development

The service uses:
- **FastAPI** for the web framework
- **Transformers** and **Torch** for translation models
- **Redis** for caching translations
- **Pydantic** for data validation