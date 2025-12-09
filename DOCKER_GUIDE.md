# 🐳 Docker Deployment Guide

This guide walks you through deploying the AI Meeting Demo application using Docker.

## 📋 Prerequisites

1. **Docker Desktop** - [Download here](https://www.docker.com/products/docker-desktop)
2. **Azure OpenAI Credentials** - Required for transcription and summarization
3. **Environment Configuration** - Copy `.env.example` to `.env` and configure

## 🚀 Quick Start

### 1. Configure Environment

Copy the example environment file and add your credentials:

```bash
cp .env.example .env
```

Edit `.env` and configure your Azure OpenAI settings:

```env
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
AZURE_OPENAI_WHISPER_DEPLOYMENT=whisper
```

### 2. Run Verification Script

The easiest way to get started:

```bash
verify_docker.bat
```

This script will:
- ✅ Check Docker installation
- ✅ Verify Docker daemon is running
- ✅ Build Docker images
- ✅ Start all services (app + Redis)
- ✅ Run health checks

### 3. Manual Setup (Alternative)

If you prefer manual control:

```bash
# Build the images
docker-compose build

# Start services in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 🏗️ Architecture

The Docker setup includes two services:

### 1. **App Service** (`ai-meeting-app`)
- Python 3.12 FastAPI application
- FFmpeg for audio processing
- Exposes port 8000
- Mounts volumes for persistent data

### 2. **Redis Service** (`ai-meeting-redis`)
- Redis 7 for job persistence
- Exposes port 6379
- Data persistence enabled

## 📁 Docker Files

### Dockerfile
Multi-stage build for optimized image size:
- **Builder stage**: Installs dependencies using UV (fast package installer)
- **Production stage**: Minimal runtime image with only necessary files

### docker-compose.yml
Orchestrates both services with:
- Network configuration
- Volume mounts for data persistence
- Environment variables
- Health checks
- Service dependencies

### .dockerignore
Excludes unnecessary files from build context to reduce image size.

## 🔧 Configuration

### Environment Variables

The application supports these environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `APP_NAME` | Application name | AI Meeting Participant |
| `ENVIRONMENT` | Environment (dev/prod) | production |
| `DEBUG` | Debug mode | false |
| `LOG_LEVEL` | Logging level | info |
| `REDIS_HOST` | Redis hostname | redis |
| `REDIS_PORT` | Redis port | 6379 |
| `AZURE_OPENAI_API_KEY` | Azure OpenAI API key | **Required** |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI endpoint | **Required** |
| `CORS_ORIGINS` | Allowed CORS origins | http://localhost:3000 |

### Volume Mounts

Data is persisted in these directories:

```yaml
./outputs  -> /app/outputs   # Transcription results
./logs     -> /app/logs       # Application logs
./uploads  -> /app/uploads    # Uploaded files
./temp     -> /app/temp       # Temporary processing files
```

## 🌐 Accessing the Application

Once started, access these endpoints:

- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Redis**: localhost:6379

## 📊 Managing the Container

### View Logs

```bash
# All services
docker-compose logs -f

# App only
docker-compose logs -f app

# Redis only
docker-compose logs -f redis
```

### Check Service Status

```bash
docker-compose ps
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart app
```

### Stop Services

```bash
# Stop containers (keep data)
docker-compose stop

# Stop and remove containers
docker-compose down

# Stop and remove everything including volumes
docker-compose down -v
```

### Execute Commands in Container

```bash
# Open shell in app container
docker-compose exec app /bin/bash

# Run Python script
docker-compose exec app python verify_setup.py

# Check Redis
docker-compose exec redis redis-cli ping
```

## 🐛 Troubleshooting

### Container won't start

1. **Check logs**: `docker-compose logs app`
2. **Verify .env file exists** and has valid credentials
3. **Ensure ports are available**: 8000 (app), 6379 (Redis)

### FFmpeg errors

FFmpeg is included in the Docker image. If you see FFmpeg errors:
- Check audio file format compatibility
- Review logs: `docker-compose logs -f app`

### Redis connection issues

```bash
# Test Redis connection
docker-compose exec redis redis-cli ping

# Should return: PONG
```

### Permission errors with volumes

On Windows, ensure Docker Desktop has access to the C: drive:
1. Docker Desktop → Settings → Resources → File Sharing
2. Add your project directory

### API not responding

```bash
# Check if container is running
docker-compose ps

# Check health
curl http://localhost:8000/health

# View recent logs
docker-compose logs --tail=50 app
```

## 🔄 Updating the Application

1. **Pull latest code**: `git pull`
2. **Rebuild images**: `docker-compose build`
3. **Restart services**: `docker-compose up -d`

## 🧪 Testing the Setup

After starting the containers, run a quick test:

```bash
# Test health endpoint
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","app_name":"AI Meeting Participant",...}
```

Or visit http://localhost:8000/docs to test the API interactively.

## 📦 Image Size Optimization

The multi-stage Dockerfile keeps the production image small:
- Build dependencies are discarded
- Only runtime dependencies included
- No source control files
- Optimized layer caching

## 🔐 Security Notes

- **Never commit .env files** to version control
- **Use secrets management** in production (Azure Key Vault, etc.)
- **Limit CORS origins** in production environment
- **Enable HTTPS** when deploying publicly

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/docker/)
- [Redis Documentation](https://redis.io/docs/)

## 💡 Tips

1. **Development mode**: Change `DEBUG=true` in docker-compose.yml for auto-reload
2. **Resource limits**: Add memory/CPU limits in production
3. **Monitoring**: Consider adding Prometheus + Grafana for production
4. **Backups**: Regularly backup the Redis volume and outputs directory
