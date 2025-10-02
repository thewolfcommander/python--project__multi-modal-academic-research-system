# Production Deployment Guide

This comprehensive guide covers production deployment considerations, best practices, and optimization strategies for the Multi-Modal Academic Research System.

## Table of Contents

1. [Production Architecture](#production-architecture)
2. [Scaling Strategies](#scaling-strategies)
3. [Performance Optimization](#performance-optimization)
4. [Security Hardening](#security-hardening)
5. [Monitoring and Logging](#monitoring-and-logging)
6. [Backup Strategies](#backup-strategies)
7. [High Availability Setup](#high-availability-setup)
8. [Load Balancing](#load-balancing)
9. [Cost Optimization](#cost-optimization)
10. [Deployment Checklist](#deployment-checklist)

## Production Architecture

### Reference Architecture

```
                        ┌──────────────────┐
                        │   Load Balancer  │
                        │   (Nginx/HAProxy)│
                        └────────┬─────────┘
                                 │
                ┌────────────────┼────────────────┐
                │                │                │
        ┌───────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐
        │  App Server 1 │ │ App Server 2│ │ App Server 3│
        │  (Gradio)     │ │  (Gradio)   │ │  (Gradio)   │
        └───────┬───────┘ └──────┬──────┘ └──────┬──────┘
                │                │                │
                └────────────────┼────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   OpenSearch Cluster    │
                    │  ┌────┐  ┌────┐  ┌────┐│
                    │  │ N1 │  │ N2 │  │ N3 ││
                    │  └────┘  └────┘  └────┘│
                    └─────────────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   Shared File Storage   │
                    │  (NFS/S3/EFS/GCS)      │
                    └─────────────────────────┘
```

### Infrastructure Components

**1. Application Tier:**
- Multiple application instances (3+ for HA)
- Containerized deployment (Docker/Kubernetes)
- Auto-scaling based on load
- Health checks and automatic recovery

**2. Search Tier:**
- OpenSearch cluster (minimum 3 nodes)
- Dedicated master nodes
- Hot/warm architecture for data
- Automated snapshots

**3. Storage Tier:**
- Shared file storage (NFS, S3, EFS)
- Separate storage for papers, videos, podcasts
- CDN for static assets
- Object storage for processed data

**4. Load Balancing:**
- Layer 7 load balancer
- SSL/TLS termination
- Health checks
- Session affinity (if needed)

**5. Monitoring:**
- Centralized logging (ELK, Splunk)
- Metrics collection (Prometheus)
- Alerting (PagerDuty, Opsgenie)
- APM (Application Performance Monitoring)

## Scaling Strategies

### Vertical Scaling

**Application Servers:**

```yaml
# docker-compose.prod.yml
services:
  research-app:
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 8G
        reservations:
          cpus: '2'
          memory: 4G
```

**OpenSearch Nodes:**

```yaml
# Increase heap size
environment:
  - "OPENSEARCH_JAVA_OPTS=-Xms8g -Xmx8g"

# Add more resources
deploy:
  resources:
    limits:
      cpus: '8'
      memory: 16G
```

### Horizontal Scaling

**Application Scaling:**

```bash
# Docker Swarm
docker service scale research-app=5

# Kubernetes
kubectl scale deployment research-app --replicas=5

# Docker Compose
docker-compose up -d --scale research-app=5
```

**OpenSearch Scaling:**

Add more data nodes to the cluster:

```yaml
# Add node-4 to docker-compose
opensearch-node4:
  image: opensearchproject/opensearch:2.11.0
  environment:
    - cluster.name=opensearch-cluster
    - node.name=opensearch-node4
    - discovery.seed_hosts=opensearch-node1,opensearch-node2,opensearch-node3
    - cluster.initial_master_nodes=opensearch-node1,opensearch-node2,opensearch-node3
    - node.roles=[data]
```

### Auto-Scaling Configuration

**Kubernetes HPA (Horizontal Pod Autoscaler):**

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: research-app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: research-app
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 100
        periodSeconds: 30
```

**AWS Auto Scaling:**

```json
{
  "AutoScalingGroupName": "research-app-asg",
  "MinSize": 3,
  "MaxSize": 10,
  "DesiredCapacity": 3,
  "HealthCheckType": "ELB",
  "HealthCheckGracePeriod": 300,
  "TargetGroupARNs": ["arn:aws:elasticloadbalancing:..."],
  "Tags": [
    {
      "Key": "Name",
      "Value": "research-app"
    }
  ]
}
```

## Performance Optimization

### Application Optimization

**1. Caching Strategy:**

```python
# Implement Redis caching
import redis
from functools import wraps

redis_client = redis.Redis(
    host='redis',
    port=6379,
    decode_responses=True
)

def cache_result(ttl=3600):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            result = func(*args, **kwargs)
            redis_client.setex(cache_key, ttl, json.dumps(result))
            return result
        return wrapper
    return decorator

@cache_result(ttl=1800)
def search_papers(query):
    # Expensive search operation
    pass
```

**2. Connection Pooling:**

```python
# OpenSearch connection pool
from opensearchpy import OpenSearch, ConnectionPool

opensearch_client = OpenSearch(
    hosts=[
        {'host': 'opensearch-1', 'port': 9200},
        {'host': 'opensearch-2', 'port': 9200},
        {'host': 'opensearch-3', 'port': 9200}
    ],
    connection_class=ConnectionPool,
    maxsize=25,  # Connection pool size
    timeout=30,
    max_retries=3,
    retry_on_timeout=True
)
```

**3. Async Processing:**

```python
# Use async for I/O operations
import asyncio
import aiohttp

async def fetch_multiple_papers(paper_ids):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_paper(session, pid) for pid in paper_ids]
        return await asyncio.gather(*tasks)

async def fetch_paper(session, paper_id):
    async with session.get(f'/api/papers/{paper_id}') as response:
        return await response.json()
```

**4. Background Tasks:**

```python
# Use Celery for background processing
from celery import Celery

celery_app = Celery('research_assistant',
                    broker='redis://redis:6379/0',
                    backend='redis://redis:6379/0')

@celery_app.task
def process_pdf_async(pdf_path):
    processor = PDFProcessor()
    return processor.process(pdf_path)

# Queue task
task = process_pdf_async.delay('/path/to/paper.pdf')
result = task.get(timeout=300)
```

**5. Optimize Gradio:**

```python
# Production Gradio configuration
app.queue(
    concurrency_count=10,  # Number of concurrent workers
    max_size=100,  # Max queue size
    api_open=False  # Disable API for security
)

app.launch(
    server_name="0.0.0.0",
    server_port=7860,
    share=False,  # Disable public sharing in production
    enable_queue=True,
    show_error=False,  # Don't show errors to users
    ssl_certfile="/path/to/cert.pem",
    ssl_keyfile="/path/to/key.pem"
)
```

### Database Optimization

**OpenSearch Performance Tuning:**

```yaml
# Production opensearch.yml
indices.memory.index_buffer_size: 30%
indices.queries.cache.size: 15%
indices.fielddata.cache.size: 25%

# Thread pools
thread_pool.search.size: 16
thread_pool.search.queue_size: 2000
thread_pool.write.size: 8
thread_pool.write.queue_size: 1000

# Bulk settings
bulk.queue_size: 500

# Circuit breakers
indices.breaker.total.limit: 70%
indices.breaker.request.limit: 45%
indices.breaker.fielddata.limit: 40%
```

**Index Optimization:**

```python
# Optimize index settings for production
production_settings = {
    "number_of_shards": 4,
    "number_of_replicas": 2,
    "refresh_interval": "30s",
    "codec": "best_compression",
    "max_result_window": 10000,
    "translog": {
        "durability": "async",
        "sync_interval": "30s",
        "flush_threshold_size": "1gb"
    },
    "merge": {
        "policy": {
            "max_merged_segment": "5gb",
            "segments_per_tier": 10
        }
    }
}
```

### CDN Integration

**Cloudflare Configuration:**

```nginx
# Cache static assets via CDN
location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
    add_header X-Content-Type-Options nosniff;
}

# Cache API responses (short TTL)
location /api/papers {
    proxy_pass http://backend;
    proxy_cache api_cache;
    proxy_cache_valid 200 5m;
    proxy_cache_key "$request_uri";
    add_header X-Cache-Status $upstream_cache_status;
}
```

## Security Hardening

### Application Security

**1. Environment Variables:**

```bash
# Use secrets management (AWS Secrets Manager, Vault)
export GEMINI_API_KEY=$(aws secretsmanager get-secret-value \
    --secret-id research-app/gemini-key \
    --query SecretString \
    --output text)
```

**2. Input Validation:**

```python
from pydantic import BaseModel, validator, Field

class SearchQuery(BaseModel):
    query: str = Field(..., min_length=3, max_length=500)
    filters: dict = Field(default_factory=dict)
    page: int = Field(default=1, ge=1, le=100)

    @validator('query')
    def validate_query(cls, v):
        # Prevent injection attacks
        if any(char in v for char in ['<', '>', ';', '--']):
            raise ValueError('Invalid characters in query')
        return v.strip()
```

**3. Rate Limiting:**

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.route("/api/search")
@limiter.limit("100/hour")
def search():
    # API endpoint with rate limiting
    pass
```

**4. Authentication & Authorization:**

```python
# Implement JWT authentication
from jose import JWTError, jwt
from datetime import datetime, timedelta

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
```

### Network Security

**1. Firewall Rules:**

```bash
# UFW configuration
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow from 10.0.0.0/8 to any port 9200  # OpenSearch (internal)
sudo ufw enable
```

**2. SSL/TLS Configuration:**

```nginx
# nginx.conf
server {
    listen 443 ssl http2;
    server_name research.example.com;

    ssl_certificate /etc/ssl/certs/fullchain.pem;
    ssl_certificate_key /etc/ssl/private/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_stapling on;
    ssl_stapling_verify on;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    location / {
        proxy_pass http://research-app:7860;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**3. VPC/Network Isolation:**

```yaml
# AWS VPC setup
VPC:
  CIDR: 10.0.0.0/16
  Subnets:
    Public:
      - 10.0.1.0/24  # Load balancer
      - 10.0.2.0/24  # Bastion host
    Private:
      - 10.0.10.0/24  # Application servers
      - 10.0.11.0/24  # Application servers
      - 10.0.20.0/24  # OpenSearch
      - 10.0.21.0/24  # OpenSearch
  SecurityGroups:
    LoadBalancer:
      Ingress: [80, 443] from 0.0.0.0/0
      Egress: [7860] to AppServers
    AppServers:
      Ingress: [7860] from LoadBalancer
      Egress: [9200] to OpenSearch
    OpenSearch:
      Ingress: [9200, 9300] from AppServers
```

### Secrets Management

**AWS Secrets Manager:**

```python
import boto3
import json

def get_secret(secret_name):
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager')

    try:
        response = client.get_secret_value(SecretId=secret_name)
        return json.loads(response['SecretString'])
    except Exception as e:
        print(f"Error retrieving secret: {e}")
        raise

# Usage
secrets = get_secret('research-app/production')
GEMINI_API_KEY = secrets['gemini_api_key']
OPENSEARCH_PASSWORD = secrets['opensearch_password']
```

**HashiCorp Vault:**

```python
import hvac

client = hvac.Client(url='https://vault.example.com:8200')
client.token = os.getenv('VAULT_TOKEN')

secret = client.secrets.kv.v2.read_secret_version(
    path='research-app/production'
)

GEMINI_API_KEY = secret['data']['data']['gemini_api_key']
```

## Monitoring and Logging

### Centralized Logging

**1. ELK Stack Setup:**

```yaml
# docker-compose.logging.yml
version: '3.8'

services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.10.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
    volumes:
      - elasticsearch-data:/usr/share/elasticsearch/data
    ports:
      - "9200:9200"

  logstash:
    image: docker.elastic.co/logstash/logstash:8.10.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf
    ports:
      - "5000:5000"
    depends_on:
      - elasticsearch

  kibana:
    image: docker.elastic.co/kibana/kibana:8.10.0
    ports:
      - "5601:5601"
    environment:
      ELASTICSEARCH_HOSTS: http://elasticsearch:9200
    depends_on:
      - elasticsearch
```

**2. Logstash Configuration:**

```conf
# logstash.conf
input {
  tcp {
    port => 5000
    codec => json
  }
  file {
    path => "/var/log/research-assistant/*.log"
    start_position => "beginning"
    sincedb_path => "/dev/null"
  }
}

filter {
  if [type] == "research-app" {
    grok {
      match => { "message" => "%{TIMESTAMP_ISO8601:timestamp} - %{LOGLEVEL:loglevel} - %{GREEDYDATA:message}" }
    }
    date {
      match => ["timestamp", "ISO8601"]
      target => "@timestamp"
    }
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "research-app-%{+YYYY.MM.dd}"
  }
  stdout { codec => rubydebug }
}
```

**3. Application Logging:**

```python
import logging
import logging.handlers
import json
from pythonjsonlogger import jsonlogger

# Configure structured logging
logHandler = logging.handlers.RotatingFileHandler(
    'logs/research_assistant.log',
    maxBytes=50*1024*1024,  # 50MB
    backupCount=10
)

formatter = jsonlogger.JsonFormatter(
    '%(timestamp)s %(name)s %(levelname)s %(message)s',
    timestamp=True
)

logHandler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

# Usage
logger.info('Search performed', extra={
    'query': query,
    'results_count': len(results),
    'duration_ms': duration,
    'user_id': user_id
})
```

### Metrics Collection

**1. Prometheus Setup:**

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'research-app'
    static_configs:
      - targets: ['research-app:8000']

  - job_name: 'opensearch'
    static_configs:
      - targets: ['opensearch-exporter:9114']

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']
```

**2. Application Metrics:**

```python
from prometheus_client import Counter, Histogram, Gauge, start_http_server

# Define metrics
search_requests = Counter('search_requests_total', 'Total search requests')
search_duration = Histogram('search_duration_seconds', 'Search duration')
active_users = Gauge('active_users', 'Number of active users')
api_errors = Counter('api_errors_total', 'Total API errors', ['endpoint'])

# Instrument code
@search_duration.time()
def perform_search(query):
    search_requests.inc()
    try:
        results = opensearch_manager.search(query)
        return results
    except Exception as e:
        api_errors.labels(endpoint='search').inc()
        raise

# Start metrics server
start_http_server(8000)
```

**3. Grafana Dashboards:**

```json
{
  "dashboard": {
    "title": "Research Assistant Monitoring",
    "panels": [
      {
        "title": "Request Rate",
        "targets": [
          {
            "expr": "rate(search_requests_total[5m])"
          }
        ]
      },
      {
        "title": "Search Latency (p95)",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, search_duration_seconds_bucket)"
          }
        ]
      },
      {
        "title": "Error Rate",
        "targets": [
          {
            "expr": "rate(api_errors_total[5m])"
          }
        ]
      }
    ]
  }
}
```

### Alerting

**1. Prometheus Alerts:**

```yaml
# alerts.yml
groups:
  - name: research-app-alerts
    interval: 30s
    rules:
      - alert: HighErrorRate
        expr: rate(api_errors_total[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }} errors/second"

      - alert: HighMemoryUsage
        expr: container_memory_usage_bytes / container_spec_memory_limit_bytes > 0.9
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage on {{ $labels.container_name }}"

      - alert: OpenSearchClusterRed
        expr: opensearch_cluster_health_status{color="red"} == 1
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "OpenSearch cluster is in RED state"
```

**2. PagerDuty Integration:**

```python
import pypd

pypd.api_key = os.getenv('PAGERDUTY_API_KEY')

def trigger_alert(title, description, severity='error'):
    pypd.EventV2.create(data={
        'routing_key': os.getenv('PAGERDUTY_ROUTING_KEY'),
        'event_action': 'trigger',
        'payload': {
            'summary': title,
            'severity': severity,
            'source': 'research-assistant',
            'custom_details': {
                'description': description
            }
        }
    })
```

## Backup Strategies

### Automated Backup System

**1. Backup Script:**

```bash
#!/bin/bash
# backup.sh

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/mnt/backups"
S3_BUCKET="s3://research-app-backups"

# OpenSearch snapshot
curl -X PUT "localhost:9200/_snapshot/backup_repo/snapshot_$TIMESTAMP?wait_for_completion=true"

# Application data
tar -czf "$BACKUP_DIR/app_data_$TIMESTAMP.tar.gz" /app/data/

# Logs
tar -czf "$BACKUP_DIR/logs_$TIMESTAMP.tar.gz" /app/logs/

# Upload to S3
aws s3 sync "$BACKUP_DIR/" "$S3_BUCKET/" --storage-class GLACIER

# Cleanup old backups (keep 30 days)
find "$BACKUP_DIR/" -name "*.tar.gz" -mtime +30 -delete

# Verify backups
aws s3 ls "$S3_BUCKET/" | tail -5
```

**2. Cron Schedule:**

```bash
# /etc/cron.d/research-app-backup
# Daily backup at 2 AM
0 2 * * * /opt/research-app/backup.sh >> /var/log/backup.log 2>&1

# Weekly full backup on Sunday
0 1 * * 0 /opt/research-app/full_backup.sh >> /var/log/backup.log 2>&1
```

**3. Backup Verification:**

```python
import subprocess
import hashlib

def verify_backup(backup_file):
    # Calculate checksum
    with open(backup_file, 'rb') as f:
        checksum = hashlib.sha256(f.read()).hexdigest()

    # Test extraction
    try:
        subprocess.run(
            ['tar', '-tzf', backup_file],
            check=True,
            capture_output=True
        )
        return True, checksum
    except subprocess.CalledProcessError:
        return False, None

def restore_backup(backup_file, destination):
    subprocess.run(
        ['tar', '-xzf', backup_file, '-C', destination],
        check=True
    )
```

### Disaster Recovery Plan

**RTO (Recovery Time Objective): 1 hour**
**RPO (Recovery Point Objective): 24 hours**

**Recovery Procedure:**

```bash
# 1. Provision new infrastructure
terraform apply -var-file=production.tfvars

# 2. Restore OpenSearch snapshots
curl -X POST "localhost:9200/_snapshot/backup_repo/latest/_restore"

# 3. Restore application data
aws s3 sync s3://research-app-backups/latest/ /app/data/

# 4. Verify services
curl http://localhost:9200/_cluster/health
curl http://localhost:7860/health

# 5. Switch DNS/Load balancer
# Manual or automated DNS update
```

## High Availability Setup

### Multi-Region Deployment

**Architecture:**

```
Region 1 (Primary)          Region 2 (Secondary)
┌─────────────────┐         ┌─────────────────┐
│ Load Balancer   │◄────────┤ Load Balancer   │
│ App Servers (3) │         │ App Servers (3) │
│ OpenSearch (3)  │◄────────┤ OpenSearch (3)  │
└─────────────────┘         └─────────────────┘
         │                           │
         └──────────┬────────────────┘
                    │
              Global DNS
           (Route 53/CloudFlare)
```

**Cross-Region Replication:**

```python
# OpenSearch cross-cluster replication
curl -X PUT "https://region1-opensearch:9200/_cluster/settings" -d'
{
  "persistent": {
    "cluster": {
      "remote": {
        "region2": {
          "seeds": ["region2-opensearch:9300"]
        }
      }
    }
  }
}'

# Start replication
curl -X PUT "https://region1-opensearch:9200/research_assistant/_ccr/follow" -d'
{
  "remote_cluster": "region2",
  "leader_index": "research_assistant"
}'
```

### Health Checks

```python
from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/health")
async def health_check():
    checks = {
        "opensearch": check_opensearch(),
        "redis": check_redis(),
        "disk_space": check_disk_space(),
        "memory": check_memory()
    }

    all_healthy = all(checks.values())
    status_code = 200 if all_healthy else 503

    return JSONResponse(
        content={"status": "healthy" if all_healthy else "unhealthy", "checks": checks},
        status_code=status_code
    )

def check_opensearch():
    try:
        health = opensearch_client.cluster.health()
        return health['status'] in ['green', 'yellow']
    except:
        return False

@app.get("/ready")
async def readiness_check():
    # Check if app is ready to serve traffic
    return {"status": "ready"}

@app.get("/live")
async def liveness_check():
    # Check if app is alive
    return {"status": "alive"}
```

## Load Balancing

### Nginx Configuration

```nginx
# /etc/nginx/nginx.conf

upstream research_app {
    least_conn;  # Load balancing method

    server app1.example.com:7860 max_fails=3 fail_timeout=30s;
    server app2.example.com:7860 max_fails=3 fail_timeout=30s;
    server app3.example.com:7860 max_fails=3 fail_timeout=30s;

    keepalive 32;
}

server {
    listen 80;
    server_name research.example.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name research.example.com;

    ssl_certificate /etc/ssl/certs/fullchain.pem;
    ssl_certificate_key /etc/ssl/private/privkey.pem;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req zone=api_limit burst=20 nodelay;

    # Connection limiting
    limit_conn_zone $binary_remote_addr zone=conn_limit:10m;
    limit_conn conn_limit 10;

    # Timeouts
    proxy_connect_timeout 60s;
    proxy_send_timeout 60s;
    proxy_read_timeout 60s;

    # Buffer settings
    proxy_buffering on;
    proxy_buffer_size 4k;
    proxy_buffers 8 4k;
    proxy_busy_buffers_size 8k;

    location / {
        proxy_pass http://research_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Health check
        proxy_next_upstream error timeout http_502 http_503 http_504;
        proxy_next_upstream_tries 3;
    }

    location /health {
        access_log off;
        proxy_pass http://research_app/health;
    }

    # Static files
    location /static {
        alias /var/www/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### HAProxy Configuration

```conf
# /etc/haproxy/haproxy.cfg

global
    log /dev/log local0
    log /dev/log local1 notice
    maxconn 4096
    user haproxy
    group haproxy
    daemon

defaults
    log     global
    mode    http
    option  httplog
    option  dontlognull
    timeout connect 5000
    timeout client  50000
    timeout server  50000

frontend http_front
    bind *:80
    redirect scheme https code 301 if !{ ssl_fc }

frontend https_front
    bind *:443 ssl crt /etc/ssl/certs/research.pem
    default_backend research_backend

backend research_backend
    balance roundrobin
    option httpchk GET /health
    http-check expect status 200

    server app1 app1.example.com:7860 check inter 5s fall 3 rise 2
    server app2 app2.example.com:7860 check inter 5s fall 3 rise 2
    server app3 app3.example.com:7860 check inter 5s fall 3 rise 2

listen stats
    bind *:8404
    stats enable
    stats uri /stats
    stats refresh 30s
```

## Cost Optimization

### Resource Right-Sizing

**1. Monitor Usage:**

```python
# Track resource utilization
import psutil

def log_resource_usage():
    metrics = {
        'cpu_percent': psutil.cpu_percent(interval=1),
        'memory_percent': psutil.virtual_memory().percent,
        'disk_usage': psutil.disk_usage('/').percent,
        'network_io': psutil.net_io_counters()._asdict()
    }
    logger.info('Resource usage', extra=metrics)
```

**2. Auto-Scaling Policies:**

```yaml
# Scale down during low traffic
scaleDown:
  - schedule: "0 22 * * *"  # 10 PM
    minReplicas: 1
    maxReplicas: 3

# Scale up during peak hours
scaleUp:
  - schedule: "0 8 * * *"  # 8 AM
    minReplicas: 3
    maxReplicas: 10
```

### Storage Optimization

**1. Data Lifecycle:**

```python
# Implement data retention policies
from datetime import datetime, timedelta

def cleanup_old_data():
    cutoff_date = datetime.now() - timedelta(days=90)

    # Delete old documents
    opensearch_client.delete_by_query(
        index='research_assistant',
        body={
            'query': {
                'range': {
                    'indexed_date': {'lt': cutoff_date.isoformat()}
                }
            }
        }
    )

    # Move to cold storage
    archive_to_s3(cutoff_date)
```

**2. Compression:**

```bash
# Compress stored files
find /app/data/papers -name "*.pdf" -exec gzip {} \;

# Use compressed index codec
curl -X PUT "localhost:9200/research_assistant/_settings" -d'
{
  "index": {
    "codec": "best_compression"
  }
}'
```

### Compute Optimization

**1. Spot Instances (AWS):**

```terraform
resource "aws_autoscaling_group" "research_app" {
  mixed_instances_policy {
    instances_distribution {
      on_demand_base_capacity                  = 2
      on_demand_percentage_above_base_capacity = 30
      spot_allocation_strategy                 = "capacity-optimized"
    }

    launch_template {
      launch_template_specification {
        launch_template_id = aws_launch_template.app.id
        version           = "$Latest"
      }

      override {
        instance_type = "c5.xlarge"
      }
      override {
        instance_type = "c5a.xlarge"
      }
    }
  }
}
```

**2. Reserved Instances:**

Purchase reserved instances for baseline capacity.

## Deployment Checklist

### Pre-Deployment

- [ ] Security audit completed
- [ ] Load testing performed
- [ ] Backup and recovery tested
- [ ] Monitoring and alerting configured
- [ ] SSL certificates installed and verified
- [ ] DNS configuration updated
- [ ] Firewall rules configured
- [ ] Secrets migrated to secrets manager
- [ ] Documentation updated
- [ ] Runbook created

### Deployment

- [ ] Create deployment snapshot/backup
- [ ] Deploy to staging environment first
- [ ] Run smoke tests
- [ ] Deploy to production with canary/blue-green
- [ ] Verify health checks
- [ ] Monitor error rates and latency
- [ ] Check logs for anomalies
- [ ] Verify all integrations working
- [ ] Test rollback procedure

### Post-Deployment

- [ ] Monitor performance metrics
- [ ] Review error logs
- [ ] Check backup completion
- [ ] Verify alerting system
- [ ] Update documentation
- [ ] Communicate to stakeholders
- [ ] Schedule post-mortem if needed

## Next Steps

- Review [Local Deployment](local.md) for development setup
- See [Docker Deployment](docker.md) for containerization
- Check [OpenSearch Setup](opensearch.md) for search configuration
