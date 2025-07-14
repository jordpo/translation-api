# Translation API

![Python](https://img.shields.io/badge/python-v3.13.1-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-green.svg)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?logo=docker&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

A high-performance translation API built with FastAPI and Facebook's NLLB-200 model. Supports 20+ languages with Redis caching for optimal performance.

## Features

- 🚀 **Fast**: Batch processing with optimized caching
- 🌍 **20+ Languages**: Powered by Facebook's NLLB-200 model
- 💾 **Redis Caching**: 30-day cache TTL for repeated translations
- 🐳 **Docker Ready**: Pre-built images with model included
- 📊 **Production Ready**: Health checks, monitoring, and scaling support
- 🔄 **Batch API**: Translate multiple texts in a single request

## Setup

### Prerequisites
- Python 3.8 or higher (3.13.1 recommended)
- Redis server (for caching)
- Docker and Docker Compose (for containerized deployment)

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

## Docker Deployment

### Quick Start with Docker Compose

1. Clone the repository and navigate to the project directory

2. First time setup (builds image and downloads model):
```bash
docker-compose up --build
```

3. Subsequent runs (uses existing image):
```bash
docker-compose up -d
```

This will:
- Build the translation service image with Python 3.13.1 (first time only)
- Pre-download the NLLB translation model (~2.4GB) during build
- Start Redis for caching
- Expose the service on port 8000

**Note**: Docker Desktop needs at least 8GB of memory allocated for the build process. Adjust in Docker Desktop → Settings → Resources.

### Docker Features

- **Pre-built Model**: The translation model is downloaded during Docker build, avoiding runtime delays
- **Persistent Volumes**: 
  - Model cache is persisted in `model-cache` volume
  - Redis data is persisted in `redis-data` volume
- **Health Checks**: Both services include health checks for reliability
- **Auto-restart**: Services automatically restart unless explicitly stopped

### Environment Variables

Create a `.env` file based on `.env.example`:
```bash
cp .env.example .env
```

Available environment variables:
- `REDIS_HOST`: Redis server hostname (default: `redis` in Docker)
- `REDIS_PORT`: Redis server port (default: `6379`)
- `MODEL_NAME`: Translation model to use (default: `facebook/nllb-200-distilled-600M`)
- `CACHE_TTL`: Cache time-to-live in seconds (default: `2592000` - 30 days)

### Docker Commands

```bash
# Start services in background
docker-compose up -d

# View logs
docker-compose logs -f translation-service

# Stop services
docker-compose down

# Stop and remove volumes (caution: removes cached model)
docker-compose down -v

# Rebuild after code changes
docker-compose up --build
```

### Production Considerations

For production deployment:
1. Use a reverse proxy (nginx/traefik) for SSL termination
2. Set up proper logging and monitoring
3. Configure resource limits in docker-compose.yml
4. Use Docker secrets for sensitive configuration
5. Consider using a managed Redis service for better reliability

## AWS EC2 Deployment

### Instance Requirements

**Minimum** (Development/Testing):
- **t3.large** (2 vCPU, 8GB RAM): ~$60/month
- **t3a.large** (2 vCPU, 8GB RAM): ~$54/month

**Recommended** (Production):
- **t3.xlarge** (4 vCPU, 16GB RAM): ~$120/month
- **m5a.xlarge** (4 vCPU, 16GB RAM): ~$124/month

**High Performance** (GPU):
- **g4dn.xlarge** (4 vCPU, 16GB RAM, GPU): ~$379/month
- 10-15x faster translation performance

### EC2 Setup Instructions

1. **Launch EC2 Instance**:
   ```bash
   # Use Amazon Linux 2023 or Ubuntu 22.04 AMI
   # Select t3.large or larger
   # Configure security group:
   # - Allow SSH (port 22) from your IP
   # - Allow HTTP (port 8000) from desired sources
   ```

2. **Connect to Instance**:
   ```bash
   ssh -i your-key.pem ec2-user@your-instance-ip
   ```

3. **Install Docker and Docker Compose**:
   ```bash
   # For Amazon Linux 2023
   sudo yum update -y
   sudo yum install -y docker git
   sudo systemctl start docker
   sudo systemctl enable docker
   sudo usermod -a -G docker ec2-user
   
   # Install Docker Compose
   sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   
   # Logout and login again for group changes
   exit
   ```

4. **Clone and Deploy**:
   ```bash
   git clone https://github.com/yourusername/translation-api.git
   cd translation-api
   
   # Create .env file
   cp .env.example .env
   
   # Build and start services
   docker-compose up -d --build
   ```

5. **Configure Nginx (Optional)**:
   ```bash
   sudo yum install -y nginx
   
   # Add reverse proxy configuration
   sudo tee /etc/nginx/conf.d/translation.conf << 'EOF'
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   EOF
   
   sudo systemctl restart nginx
   ```

### Cost Optimization

1. **Use Spot Instances** (up to 90% savings):
   - Good for non-critical workloads
   - May be interrupted with 2-minute notice

2. **Reserved Instances** (up to 72% savings):
   - 1-year: ~40% discount
   - 3-year: ~60% discount

3. **Auto-scaling**:
   - Scale based on CPU/memory usage
   - Use CloudWatch alarms

4. **Storage Optimization**:
   - Use gp3 instead of gp2 (20% cheaper)
   - 30GB should be sufficient

### Monitoring

Set up CloudWatch monitoring:
```bash
# Install CloudWatch agent
wget https://s3.amazonaws.com/amazoncloudwatch-agent/amazon_linux/amd64/latest/amazon-cloudwatch-agent.rpm
sudo rpm -U ./amazon-cloudwatch-agent.rpm

# Configure to monitor Docker containers
```

### Backup Strategy

1. **Docker Volumes**:
   ```bash
   # Backup Redis data
   docker run --rm -v translation-service_redis-data:/data -v $(pwd):/backup alpine tar czf /backup/redis-backup.tar.gz -C /data .
   
   # Backup model cache
   docker run --rm -v translation-service_model-cache:/models -v $(pwd):/backup alpine tar czf /backup/model-backup.tar.gz -C /models .
   ```

2. **Automated Backups**:
   - Use AWS Backup for EBS volumes
   - Schedule daily snapshots

## Development

### Tech Stack

- **FastAPI** - High-performance web framework
- **Transformers** - Hugging Face transformers for NLLB model
- **PyTorch** - Deep learning framework
- **Redis** - In-memory caching
- **Docker** - Containerization
- **Pydantic** - Data validation

### Running Tests

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Run with coverage
pytest --cov=app
```

### Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Facebook AI for the NLLB-200 model
- FastAPI community
- Contributors and maintainers