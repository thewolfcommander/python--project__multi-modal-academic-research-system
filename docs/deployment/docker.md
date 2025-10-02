# Docker Deployment Guide

This guide covers containerizing the Multi-Modal Academic Research System using Docker and Docker Compose for easy deployment and management.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Docker Setup](#docker-setup)
4. [Docker Compose Setup](#docker-compose-setup)
5. [Building and Running](#building-and-running)
6. [Volume Management](#volume-management)
7. [Container Orchestration](#container-orchestration)
8. [Networking](#networking)
9. [Troubleshooting](#troubleshooting)

## Overview

### Benefits of Docker Deployment

- **Consistency**: Same environment across development, testing, and production
- **Isolation**: Dependencies contained within containers
- **Portability**: Deploy anywhere Docker runs
- **Scalability**: Easy to scale services independently
- **Version Control**: Infrastructure as code

### Architecture

```
┌─────────────────────────────────────────────┐
│           Docker Compose Stack              │
├─────────────────────────────────────────────┤
│                                             │
│  ┌──────────────────┐  ┌──────────────────┐│
│  │                  │  │                  ││
│  │   Research App   │←→│   OpenSearch    ││
│  │   (Port 7860)    │  │   (Port 9200)   ││
│  │                  │  │                  ││
│  └──────────────────┘  └──────────────────┘│
│           ↓                      ↓          │
│  ┌──────────────────┐  ┌──────────────────┐│
│  │  App Data Volume │  │  OS Data Volume  ││
│  └──────────────────┘  └──────────────────┘│
│                                             │
└─────────────────────────────────────────────┘
```

## Prerequisites

### Required Software

1. **Docker Engine** (version 20.10+)
   ```bash
   docker --version
   # Docker version 20.10.x or higher
   ```

2. **Docker Compose** (version 2.0+)
   ```bash
   docker-compose --version
   # Docker Compose version 2.x.x or higher
   ```

### Installation

**macOS:**
```bash
# Install Docker Desktop
brew install --cask docker

# Or download from: https://www.docker.com/products/docker-desktop
```

**Linux (Ubuntu/Debian):**
```bash
# Update package index
sudo apt-get update

# Install dependencies
sudo apt-get install ca-certificates curl gnupg lsb-release

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Set up repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

**Windows:**
```bash
# Download and install Docker Desktop from:
# https://www.docker.com/products/docker-desktop
```

## Docker Setup

### 1. Create Dockerfile for Application

Create `Dockerfile` in project root:

```dockerfile
# Use official Python runtime as base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data/papers data/videos data/podcasts data/processed logs configs

# Set permissions
RUN chmod -R 755 data logs configs

# Expose Gradio port
EXPOSE 7860

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:7860/ || exit 1

# Run application
CMD ["python", "main.py"]
```

### 2. Create .dockerignore

Create `.dockerignore` to exclude unnecessary files:

```
# Virtual environments
venv/
env/
ENV/
*.pyc
__pycache__/

# IDE files
.vscode/
.idea/
*.swp
*.swo

# Git
.git/
.gitignore

# Data directories (will use volumes)
data/
logs/

# Environment files with secrets
.env

# Documentation
docs/
*.md
!README.md

# Test files
tests/
*.pytest_cache/

# OS files
.DS_Store
Thumbs.db

# Build artifacts
build/
dist/
*.egg-info/
```

### 3. Build Docker Image

```bash
# Build image with tag
docker build -t research-assistant:latest .

# Build with specific version
docker build -t research-assistant:v1.0.0 .

# Build with no cache (clean build)
docker build --no-cache -t research-assistant:latest .

# Verify image
docker images | grep research-assistant
```

### 4. Run Single Container

```bash
# Run with environment variables
docker run -d \
  --name research-assistant \
  -p 7860:7860 \
  -e GEMINI_API_KEY=your_api_key_here \
  -e OPENSEARCH_HOST=opensearch \
  -e OPENSEARCH_PORT=9200 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  research-assistant:latest

# Check logs
docker logs -f research-assistant

# Stop container
docker stop research-assistant

# Remove container
docker rm research-assistant
```

## Docker Compose Setup

### 1. Create docker-compose.yml

Create `docker-compose.yml` in project root:

```yaml
version: '3.8'

services:
  # OpenSearch service
  opensearch:
    image: opensearchproject/opensearch:2.11.0
    container_name: opensearch-node
    environment:
      - discovery.type=single-node
      - OPENSEARCH_INITIAL_ADMIN_PASSWORD=MyStrongPassword123!
      - bootstrap.memory_lock=true
      - "OPENSEARCH_JAVA_OPTS=-Xms1g -Xmx1g"
      - cluster.name=research-cluster
      - node.name=opensearch-node
      - plugins.security.disabled=true  # Disable for development
    ulimits:
      memlock:
        soft: -1
        hard: -1
      nofile:
        soft: 65536
        hard: 65536
    volumes:
      - opensearch-data:/usr/share/opensearch/data
    ports:
      - "9200:9200"
      - "9600:9600"
    networks:
      - research-network
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:9200/_cluster/health || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 60s

  # Research Assistant application
  research-app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: research-assistant-app
    depends_on:
      opensearch:
        condition: service_healthy
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - OPENSEARCH_HOST=opensearch
      - OPENSEARCH_PORT=9200
      - OPENSEARCH_USER=admin
      - OPENSEARCH_PASSWORD=MyStrongPassword123!
      - OPENSEARCH_USE_SSL=false
      - OPENSEARCH_VERIFY_CERTS=false
      - GRADIO_SERVER_NAME=0.0.0.0
      - GRADIO_SERVER_PORT=7860
      - GRADIO_SHARE=true
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./configs:/app/configs
    ports:
      - "7860:7860"
    networks:
      - research-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:7860/ || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

networks:
  research-network:
    driver: bridge

volumes:
  opensearch-data:
    driver: local
```

### 2. Create docker-compose.override.yml (Optional)

For development-specific settings:

```yaml
version: '3.8'

services:
  research-app:
    environment:
      - LOG_LEVEL=DEBUG
      - GRADIO_SHARE=false
    volumes:
      - .:/app  # Mount entire directory for live code updates
    command: python main.py --debug
```

### 3. Create Production docker-compose.prod.yml

```yaml
version: '3.8'

services:
  opensearch:
    environment:
      - "OPENSEARCH_JAVA_OPTS=-Xms4g -Xmx4g"  # More memory
      - plugins.security.disabled=false  # Enable security
      - plugins.security.ssl.http.enabled=true
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          memory: 2G

  research-app:
    environment:
      - LOG_LEVEL=INFO
      - GRADIO_SHARE=false
    deploy:
      replicas: 2  # Run 2 instances
      resources:
        limits:
          cpus: '1'
          memory: 2G
        reservations:
          memory: 1G
    restart: always
```

## Building and Running

### Development Environment

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f research-app
docker-compose logs -f opensearch

# Stop services
docker-compose stop

# Start stopped services
docker-compose start

# Restart services
docker-compose restart

# Stop and remove containers
docker-compose down

# Stop and remove containers, networks, volumes
docker-compose down -v
```

### Production Environment

```bash
# Build and start with production config
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Scale application
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --scale research-app=3

# View status
docker-compose ps

# Stop production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml down
```

### Rebuild After Code Changes

```bash
# Rebuild and restart
docker-compose up -d --build

# Rebuild specific service
docker-compose build research-app
docker-compose up -d research-app

# Force rebuild (no cache)
docker-compose build --no-cache
docker-compose up -d
```

## Volume Management

### Understanding Volumes

Volumes persist data outside containers:

1. **opensearch-data**: OpenSearch indices and data
2. **./data**: Application data (papers, videos, podcasts)
3. **./logs**: Application logs
4. **./configs**: Configuration files

### Volume Operations

```bash
# List volumes
docker volume ls

# Inspect volume
docker volume inspect multi-modal-academic-research-system_opensearch-data

# Backup volume
docker run --rm \
  -v multi-modal-academic-research-system_opensearch-data:/data \
  -v $(pwd)/backups:/backup \
  alpine tar czf /backup/opensearch-backup-$(date +%Y%m%d).tar.gz -C /data .

# Restore volume
docker run --rm \
  -v multi-modal-academic-research-system_opensearch-data:/data \
  -v $(pwd)/backups:/backup \
  alpine tar xzf /backup/opensearch-backup-20240101.tar.gz -C /data

# Remove unused volumes
docker volume prune

# Remove specific volume (WARNING: deletes data)
docker volume rm multi-modal-academic-research-system_opensearch-data
```

### Bind Mounts vs Named Volumes

**Bind Mounts** (./data:/app/data):
- Direct mapping to host directory
- Easy access from host
- Good for development and logs

**Named Volumes** (opensearch-data):
- Managed by Docker
- Better performance
- Good for databases

## Container Orchestration

### Managing Container Lifecycle

```bash
# Start containers
docker-compose start

# Stop containers (preserves containers)
docker-compose stop

# Pause containers (freeze processes)
docker-compose pause

# Unpause containers
docker-compose unpause

# Restart containers
docker-compose restart

# Remove stopped containers
docker-compose rm

# Stop and remove containers, networks
docker-compose down
```

### Scaling Services

```bash
# Scale to 3 instances
docker-compose up -d --scale research-app=3

# Scale with load balancer (requires nginx)
docker-compose up -d --scale research-app=3 nginx
```

### Health Checks

```bash
# Check container health
docker ps --format "table {{.Names}}\t{{.Status}}"

# Inspect health check
docker inspect --format='{{json .State.Health}}' research-assistant-app | jq

# View health check logs
docker inspect research-assistant-app | jq '.[0].State.Health.Log'
```

### Resource Management

**Limit CPU and Memory:**

```yaml
services:
  research-app:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 1G
```

**Monitor Resource Usage:**

```bash
# Real-time stats
docker stats

# Specific container
docker stats research-assistant-app

# Export stats to file
docker stats --no-stream > stats.txt
```

## Networking

### Network Configuration

```bash
# List networks
docker network ls

# Inspect network
docker network inspect multi-modal-academic-research-system_research-network

# Test connectivity between containers
docker exec research-assistant-app ping opensearch

# Check DNS resolution
docker exec research-assistant-app nslookup opensearch
```

### Expose Additional Ports

```yaml
services:
  research-app:
    ports:
      - "7860:7860"  # Main app
      - "7861:7861"  # Admin interface (if added)
      - "8080:8080"  # Health check endpoint
```

### Use Host Network (Not Recommended)

```yaml
services:
  research-app:
    network_mode: "host"
```

## Troubleshooting

### Common Issues

#### 1. Container Won't Start

```bash
# Check logs
docker-compose logs research-app

# Check last 100 lines
docker-compose logs --tail=100 research-app

# Follow logs in real-time
docker-compose logs -f research-app

# Check container status
docker-compose ps
```

#### 2. OpenSearch Unhealthy

```bash
# Check OpenSearch logs
docker-compose logs opensearch

# Check cluster health
docker exec opensearch-node curl http://localhost:9200/_cluster/health?pretty

# Increase memory
# Edit docker-compose.yml:
environment:
  - "OPENSEARCH_JAVA_OPTS=-Xms2g -Xmx2g"

# Restart
docker-compose restart opensearch
```

#### 3. Permission Denied Errors

```bash
# Fix host directory permissions
sudo chown -R $USER:$USER data/ logs/ configs/
chmod -R 755 data/ logs/ configs/

# Fix container permissions
docker exec -u root research-assistant-app chown -R nobody:nogroup /app/data
```

#### 4. Port Already in Use

```bash
# Find process using port
lsof -i :7860

# Change port in docker-compose.yml
ports:
  - "7861:7860"  # Host:Container

# Or stop conflicting service
docker stop <container_name>
```

#### 5. Cannot Connect to OpenSearch

```bash
# Test from host
curl http://localhost:9200

# Test from container
docker exec research-assistant-app curl http://opensearch:9200

# Check network connectivity
docker network inspect multi-modal-academic-research-system_research-network

# Verify service names in docker-compose.yml match environment variables
```

#### 6. Out of Disk Space

```bash
# Check disk usage
docker system df

# Remove unused data
docker system prune

# Remove all unused images, containers, volumes
docker system prune -a --volumes

# Remove specific items
docker image prune
docker container prune
docker volume prune
```

#### 7. Build Fails

```bash
# Clean build
docker-compose build --no-cache

# Check Docker logs
docker-compose logs --tail=50

# Verify Dockerfile syntax
docker build --dry-run -t test .

# Build with verbose output
docker-compose build --progress=plain
```

#### 8. Container Exits Immediately

```bash
# Check exit code
docker-compose ps

# View last container logs
docker logs $(docker ps -lq)

# Run interactive shell to debug
docker run -it --rm research-assistant:latest /bin/bash

# Override entrypoint
docker run -it --rm --entrypoint /bin/bash research-assistant:latest
```

#### 9. Volume Mount Issues

```bash
# Verify volume exists
docker volume ls | grep opensearch-data

# Check mount points
docker inspect research-assistant-app | jq '.[0].Mounts'

# Test volume permissions
docker run --rm -v $(pwd)/data:/test alpine ls -la /test
```

#### 10. Network Issues

```bash
# Recreate network
docker-compose down
docker network prune
docker-compose up -d

# Check DNS resolution
docker exec research-assistant-app cat /etc/hosts
docker exec research-assistant-app nslookup opensearch

# Test connectivity
docker exec research-assistant-app telnet opensearch 9200
```

### Debug Commands

```bash
# Shell into container
docker exec -it research-assistant-app /bin/bash

# Run as root
docker exec -u root -it research-assistant-app /bin/bash

# Copy files from container
docker cp research-assistant-app:/app/logs/research_assistant.log ./

# Copy files to container
docker cp config.json research-assistant-app:/app/configs/

# View container processes
docker top research-assistant-app

# View container resource usage
docker stats research-assistant-app --no-stream

# Inspect container details
docker inspect research-assistant-app

# View container environment variables
docker exec research-assistant-app env
```

### Performance Optimization

```bash
# Optimize Docker Desktop (macOS)
# Increase resources in Docker Desktop settings:
# - CPUs: 4+
# - Memory: 8GB+
# - Swap: 2GB+

# Enable BuildKit for faster builds
export DOCKER_BUILDKIT=1
docker-compose build

# Use multi-stage builds
# Add to Dockerfile:
# FROM python:3.11-slim as builder
# ... build steps ...
# FROM python:3.11-slim
# COPY --from=builder ...

# Layer caching optimization
# Order Dockerfile commands from least to most frequently changing
```

### Logging Best Practices

```bash
# Configure log rotation in docker-compose.yml
services:
  research-app:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

# View logs with timestamps
docker-compose logs -f -t research-app

# Export logs
docker-compose logs research-app > app-logs.txt
```

## Next Steps

- Review [OpenSearch Setup](opensearch.md) for advanced OpenSearch configuration
- See [Production Considerations](production.md) for production deployment
- Check [Local Deployment](local.md) for development workflow
