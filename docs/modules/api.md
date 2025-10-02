# API Module

## Overview

The API module provides a FastAPI-based REST API for visualizing and accessing collected research data. It includes endpoints for retrieving collections, viewing statistics, searching content, and serving a visualization dashboard.

## Module Architecture

```
multi_modal_rag/api/
├── api_server.py         # FastAPI application
└── static/
    └── visualization.html # Frontend dashboard (optional)
```

---

## FastAPI Application

**File**: `multi_modal_rag/api/api_server.py`

### Application Setup

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Multi-Modal Research Data API",
    description="API for visualizing collected research data",
    version="1.0.0"
)
```

**Features**:
- CORS enabled for frontend access
- Automatic OpenAPI/Swagger documentation
- Integrated database manager
- RESTful endpoints

### Starting the Server

**Method 1: Direct Execution**

```bash
python -m multi_modal_rag.api.api_server
```

**Method 2: Using uvicorn**

```bash
uvicorn multi_modal_rag.api.api_server:app --host 0.0.0.0 --port 8000
```

**Method 3: Using start script**

```bash
python start_api_server.py
```

**Access Points**:
- API: http://localhost:8000
- Swagger Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## API Endpoints

### Root Endpoint

#### `GET /`

Returns API information and available endpoints.

**Response**:

```json
{
    "message": "Multi-Modal Research Data API",
    "endpoints": {
        "collections": "/api/collections",
        "statistics": "/api/statistics",
        "search": "/api/search",
        "visualization": "/viz"
    }
}
```

**Example**:

```bash
curl http://localhost:8000/
```

---

### Collections Endpoints

#### `GET /api/collections`

Retrieves all collections with optional filtering and pagination.

**Query Parameters**:
- `content_type` (str, optional): Filter by type ('paper', 'video', 'podcast')
- `limit` (int, optional): Max results (1-1000). Default: 100
- `offset` (int, optional): Offset for pagination. Default: 0

**Response**:

```json
{
    "count": 25,
    "collections": [
        {
            "id": 1,
            "content_type": "paper",
            "title": "Attention Is All You Need",
            "source": "arxiv",
            "url": "https://arxiv.org/abs/1706.03762",
            "collection_date": "2024-10-02T14:30:00",
            "metadata": {
                "query": "transformer models",
                "categories": ["cs.CL", "cs.LG"]
            },
            "status": "collected",
            "indexed": true
        },
        // ... more collections
    ]
}
```

**Examples**:

```bash
# Get all collections
curl http://localhost:8000/api/collections

# Get only papers
curl http://localhost:8000/api/collections?content_type=paper

# Get videos with pagination
curl http://localhost:8000/api/collections?content_type=video&limit=20&offset=0

# Get second page
curl http://localhost:8000/api/collections?limit=50&offset=50
```

**Python Client**:

```python
import requests

# Get all collections
response = requests.get("http://localhost:8000/api/collections")
data = response.json()

print(f"Total collections: {data['count']}")
for item in data['collections']:
    print(f"  - {item['title']} ({item['content_type']})")

# Filter by type
response = requests.get(
    "http://localhost:8000/api/collections",
    params={"content_type": "paper", "limit": 50}
)
papers = response.json()['collections']
```

---

#### `GET /api/collections/{collection_id}`

Retrieves detailed information for a specific collection.

**Path Parameters**:
- `collection_id` (int): Collection ID

**Response**:

```json
{
    "id": 1,
    "content_type": "paper",
    "title": "Attention Is All You Need",
    "source": "arxiv",
    "url": "https://arxiv.org/abs/1706.03762",
    "collection_date": "2024-10-02T14:30:00",
    "metadata": {
        "query": "transformer models",
        "categories": ["cs.CL", "cs.LG"]
    },
    "status": "collected",
    "indexed": true,
    "details": {
        "id": 1,
        "collection_id": 1,
        "arxiv_id": "1706.03762",
        "pmc_id": null,
        "abstract": "The dominant sequence transduction models...",
        "authors": ["Ashish Vaswani", "Noam Shazeer", "Niki Parmar"],
        "published_date": "2017-06-12",
        "categories": ["cs.CL", "cs.LG"],
        "pdf_path": "data/papers/1706.03762.pdf"
    }
}
```

**Error Responses**:

```json
// 404 Not Found
{
    "detail": "Collection not found"
}

// 500 Internal Server Error
{
    "detail": "Error message here"
}
```

**Examples**:

```bash
# Get collection details
curl http://localhost:8000/api/collections/1

# Handle errors
curl http://localhost:8000/api/collections/99999
# Returns 404 with "Collection not found"
```

**Python Client**:

```python
import requests

def get_collection_details(collection_id: int):
    response = requests.get(
        f"http://localhost:8000/api/collections/{collection_id}"
    )

    if response.status_code == 200:
        data = response.json()
        print(f"Title: {data['title']}")
        print(f"Type: {data['content_type']}")

        if 'details' in data:
            if data['content_type'] == 'paper':
                details = data['details']
                print(f"Authors: {', '.join(details['authors'])}")
                print(f"Abstract: {details['abstract'][:200]}...")
    else:
        print(f"Error: {response.status_code}")

get_collection_details(1)
```

---

### Statistics Endpoint

#### `GET /api/statistics`

Retrieves database statistics.

**Response**:

```json
{
    "by_type": {
        "paper": 150,
        "video": 75,
        "podcast": 30
    },
    "indexed": 200,
    "not_indexed": 55,
    "recent_7_days": 25,
    "collection_history": [
        {
            "type": "paper",
            "source": "arxiv",
            "total": 150
        },
        {
            "type": "video",
            "source": "youtube",
            "total": 75
        },
        {
            "type": "podcast",
            "source": "rss",
            "total": 30
        }
    ]
}
```

**Example**:

```bash
curl http://localhost:8000/api/statistics
```

**Python Client**:

```python
import requests

response = requests.get("http://localhost:8000/api/statistics")
stats = response.json()

print("=== Database Statistics ===")
print(f"\nContent by Type:")
for content_type, count in stats['by_type'].items():
    print(f"  {content_type}: {count}")

print(f"\nIndexing Status:")
print(f"  Indexed: {stats['indexed']}")
print(f"  Not Indexed: {stats['not_indexed']}")

total = stats['indexed'] + stats['not_indexed']
percentage = (stats['indexed'] / total * 100) if total > 0 else 0
print(f"  Completion: {percentage:.1f}%")

print(f"\nRecent Activity:")
print(f"  Last 7 days: {stats['recent_7_days']} new items")
```

**Visualization Example**:

```python
import matplotlib.pyplot as plt

# Pie chart of content types
response = requests.get("http://localhost:8000/api/statistics")
stats = response.json()

labels = list(stats['by_type'].keys())
sizes = list(stats['by_type'].values())

plt.pie(sizes, labels=labels, autopct='%1.1f%%')
plt.title('Collection Distribution by Type')
plt.show()
```

---

### Search Endpoint

#### `GET /api/search`

Searches collections by title or source.

**Query Parameters**:
- `q` (str, required): Search query (min 1 character)
- `limit` (int, optional): Max results (1-500). Default: 50

**Response**:

```json
{
    "query": "transformer",
    "count": 12,
    "results": [
        {
            "id": 1,
            "content_type": "paper",
            "title": "Attention Is All You Need",
            "source": "arxiv",
            "url": "https://arxiv.org/abs/1706.03762",
            "collection_date": "2024-10-02T14:30:00",
            "metadata": {...},
            "status": "collected",
            "indexed": true
        },
        // ... more results
    ]
}
```

**Examples**:

```bash
# Search by title keyword
curl "http://localhost:8000/api/search?q=transformer"

# Search by source
curl "http://localhost:8000/api/search?q=arxiv&limit=100"

# Search with special characters (URL encoded)
curl "http://localhost:8000/api/search?q=neural%20networks"
```

**Python Client**:

```python
import requests

def search_collections(query: str, limit: int = 50):
    response = requests.get(
        "http://localhost:8000/api/search",
        params={"q": query, "limit": limit}
    )

    data = response.json()
    print(f"Query: '{data['query']}'")
    print(f"Found {data['count']} results\n")

    for item in data['results']:
        print(f"  {item['id']}: {item['title']}")
        print(f"     Type: {item['content_type']}, Source: {item['source']}")
        print()

# Search for papers about attention
search_collections("attention", limit=10)

# Search for specific source
search_collections("youtube")
```

---

### Visualization Dashboard

#### `GET /viz`

Serves the HTML visualization dashboard.

**Response**: HTML page with interactive visualizations

**Features**:
- Charts showing collection distribution
- Filter by content type
- Search functionality
- Recent activity timeline
- Statistics cards

**Access**:

```bash
# Open in browser
open http://localhost:8000/viz
```

**Fallback Response** (if visualization.html not found):

```html
<html>
    <body>
        <h1>Visualization page not found</h1>
        <p>Please ensure visualization.html exists in the static directory</p>
    </body>
</html>
```

**Dashboard Implementation**:

The visualization page should be located at:
```
multi_modal_rag/api/static/visualization.html
```

**Example Dashboard HTML**:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Research Collection Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .stats-card {
            display: inline-block;
            padding: 20px;
            margin: 10px;
            background: #f0f0f0;
            border-radius: 8px;
        }
        .chart-container {
            width: 400px;
            height: 400px;
            display: inline-block;
        }
    </style>
</head>
<body>
    <h1>Research Collection Dashboard</h1>

    <div id="stats"></div>
    <div id="charts"></div>

    <script>
        // Fetch statistics
        fetch('/api/statistics')
            .then(response => response.json())
            .then(stats => {
                // Display stats cards
                document.getElementById('stats').innerHTML = `
                    <div class="stats-card">
                        <h3>Total Papers</h3>
                        <p>${stats.by_type.paper || 0}</p>
                    </div>
                    <div class="stats-card">
                        <h3>Total Videos</h3>
                        <p>${stats.by_type.video || 0}</p>
                    </div>
                    <div class="stats-card">
                        <h3>Indexed</h3>
                        <p>${stats.indexed}</p>
                    </div>
                `;

                // Create pie chart
                const ctx = document.createElement('canvas');
                document.getElementById('charts').appendChild(ctx);

                new Chart(ctx, {
                    type: 'pie',
                    data: {
                        labels: Object.keys(stats.by_type),
                        datasets: [{
                            data: Object.values(stats.by_type),
                            backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56']
                        }]
                    }
                });
            });
    </script>
</body>
</html>
```

---

### Health Check Endpoint

#### `GET /health`

Health check endpoint for monitoring.

**Response**:

```json
{
    "status": "healthy"
}
```

**Example**:

```bash
curl http://localhost:8000/health
```

**Use Cases**:
- Load balancer health checks
- Container orchestration (Kubernetes)
- Monitoring systems
- CI/CD pipelines

---

## CORS Configuration

The API is configured to allow cross-origin requests:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],          # Allow all HTTP methods
    allow_headers=["*"],          # Allow all headers
)
```

**Security Note**: For production, restrict `allow_origins` to specific domains:

```python
allow_origins=[
    "https://yourdomain.com",
    "http://localhost:3000"
]
```

---

## Error Handling

### HTTP Status Codes

| Code | Description | When Used |
|------|-------------|-----------|
| 200 | OK | Successful request |
| 404 | Not Found | Collection ID doesn't exist |
| 422 | Unprocessable Entity | Invalid parameters |
| 500 | Internal Server Error | Database or server error |

### Error Response Format

```json
{
    "detail": "Error message describing what went wrong"
}
```

**Examples**:

```python
from fastapi import HTTPException

# Collection not found
raise HTTPException(status_code=404, detail="Collection not found")

# Invalid parameters (handled by FastAPI automatically)
# Query parameter validation fails → 422

# Database error
raise HTTPException(status_code=500, detail=str(e))
```

---

## Integration Examples

### Frontend Integration (React)

```javascript
import React, { useState, useEffect } from 'react';

function CollectionsList() {
    const [collections, setCollections] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetch('http://localhost:8000/api/collections?limit=50')
            .then(response => response.json())
            .then(data => {
                setCollections(data.collections);
                setLoading(false);
            });
    }, []);

    if (loading) return <div>Loading...</div>;

    return (
        <div>
            <h1>Collections ({collections.length})</h1>
            {collections.map(item => (
                <div key={item.id}>
                    <h3>{item.title}</h3>
                    <p>Type: {item.content_type}</p>
                    <p>Source: {item.source}</p>
                </div>
            ))}
        </div>
    );
}
```

### Python Data Analysis

```python
import requests
import pandas as pd
import matplotlib.pyplot as plt

# Fetch all collections
response = requests.get("http://localhost:8000/api/collections?limit=1000")
collections = response.json()['collections']

# Convert to DataFrame
df = pd.DataFrame(collections)

# Analysis
print("Collections by Type:")
print(df['content_type'].value_counts())

print("\nCollections by Source:")
print(df['source'].value_counts())

# Visualization
df['content_type'].value_counts().plot(kind='bar')
plt.title('Collections by Type')
plt.xlabel('Content Type')
plt.ylabel('Count')
plt.show()

# Time series analysis
df['collection_date'] = pd.to_datetime(df['collection_date'])
df.set_index('collection_date', inplace=True)
df.resample('D').size().plot()
plt.title('Collections Over Time')
plt.show()
```

### CLI Tool

```python
import click
import requests

@click.group()
def cli():
    """Research Collection CLI"""
    pass

@cli.command()
@click.option('--type', help='Filter by content type')
@click.option('--limit', default=10, help='Number of results')
def list_collections(type, limit):
    """List collections"""
    params = {'limit': limit}
    if type:
        params['content_type'] = type

    response = requests.get('http://localhost:8000/api/collections', params=params)
    data = response.json()

    click.echo(f"Found {data['count']} collections\n")
    for item in data['collections']:
        click.echo(f"[{item['id']}] {item['title']}")
        click.echo(f"    Type: {item['content_type']}, Source: {item['source']}")
        click.echo()

@cli.command()
@click.argument('query')
def search(query):
    """Search collections"""
    response = requests.get('http://localhost:8000/api/search', params={'q': query})
    data = response.json()

    click.echo(f"Query: '{data['query']}' - {data['count']} results\n")
    for item in data['results']:
        click.echo(f"• {item['title']} ({item['content_type']})")

@cli.command()
def stats():
    """Show statistics"""
    response = requests.get('http://localhost:8000/api/statistics')
    data = response.json()

    click.echo("=== Statistics ===\n")
    click.echo("By Type:")
    for t, count in data['by_type'].items():
        click.echo(f"  {t}: {count}")

    click.echo(f"\nIndexed: {data['indexed']}")
    click.echo(f"Not Indexed: {data['not_indexed']}")

if __name__ == '__main__':
    cli()
```

**Usage**:

```bash
python cli_tool.py list-collections --type paper --limit 5
python cli_tool.py search "neural networks"
python cli_tool.py stats
```

---

## Performance Considerations

### Response Times

**Typical Response Times**:
- `GET /`: <5ms
- `GET /api/collections`: 10-50ms (100 items)
- `GET /api/collections/{id}`: 5-20ms
- `GET /api/statistics`: 20-100ms (aggregations)
- `GET /api/search`: 50-200ms (LIKE query)

### Optimization Tips

1. **Pagination**: Always use `limit` parameter
   ```python
   # Good
   response = requests.get('/api/collections?limit=50')

   # Bad (loads all)
   response = requests.get('/api/collections?limit=10000')
   ```

2. **Caching**: Implement Redis caching for statistics
   ```python
   from fastapi_cache import FastAPICache
   from fastapi_cache.decorator import cache

   @app.get("/api/statistics")
   @cache(expire=300)  # Cache for 5 minutes
   async def get_statistics():
       ...
   ```

3. **Database Indexing**: Add indexes to frequently queried fields
   ```sql
   CREATE INDEX idx_content_type ON collections(content_type);
   CREATE INDEX idx_indexed ON collections(indexed);
   ```

4. **Async Database Operations**: Use async SQLite library
   ```python
   import aiosqlite

   @app.get("/api/collections")
   async def get_collections(...):
       async with aiosqlite.connect(db_path) as db:
           async with db.execute("SELECT ...") as cursor:
               rows = await cursor.fetchall()
   ```

---

## Security Considerations

### Production Deployment

1. **CORS**: Restrict origins
   ```python
   allow_origins=["https://yourdomain.com"]
   ```

2. **Authentication**: Add API key or OAuth
   ```python
   from fastapi.security import APIKeyHeader

   api_key_header = APIKeyHeader(name="X-API-Key")

   @app.get("/api/collections")
   async def get_collections(api_key: str = Depends(api_key_header)):
       if api_key != os.getenv("API_KEY"):
           raise HTTPException(401, "Invalid API key")
       ...
   ```

3. **Rate Limiting**: Prevent abuse
   ```python
   from slowapi import Limiter
   from slowapi.util import get_remote_address

   limiter = Limiter(key_func=get_remote_address)

   @app.get("/api/search")
   @limiter.limit("10/minute")
   async def search(...):
       ...
   ```

4. **HTTPS**: Use SSL/TLS in production
   ```bash
   uvicorn app:app --host 0.0.0.0 --port 443 --ssl-keyfile key.pem --ssl-certfile cert.pem
   ```

---

## Deployment

### Docker Deployment

**Dockerfile**:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "multi_modal_rag.api.api_server:app", "--host", "0.0.0.0", "--port", "8000"]
```

**docker-compose.yml**:

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
    environment:
      - DATABASE_PATH=/app/data/collections.db
```

**Run**:

```bash
docker-compose up -d
```

### Kubernetes Deployment

**deployment.yaml**:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: research-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: research-api
  template:
    metadata:
      labels:
        app: research-api
    spec:
      containers:
      - name: api
        image: research-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_PATH
          value: "/data/collections.db"
        volumeMounts:
        - name: data
          mountPath: /data
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: research-data-pvc
```

---

## Dependencies

```python
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import uvicorn
```

**Installation**:

```bash
pip install fastapi uvicorn[standard]
```

---

## Troubleshooting

### Issue: Port already in use

**Error**: `OSError: [Errno 48] Address already in use`

**Solution**: Use different port or kill existing process
```bash
# Find process
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
uvicorn app:app --port 8001
```

### Issue: CORS errors in browser

**Error**: `Access to fetch at 'http://localhost:8000' from origin 'http://localhost:3000' has been blocked by CORS policy`

**Solution**: Ensure CORS middleware is configured correctly
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue: 422 Unprocessable Entity

**Cause**: Invalid query parameters

**Example**:
```bash
# Missing required parameter 'q'
curl http://localhost:8000/api/search
# Returns: {"detail":[{"loc":["query","q"],"msg":"field required",...}]}
```

**Solution**: Provide required parameters
```bash
curl "http://localhost:8000/api/search?q=test"
```

---

## API Documentation

### Auto-Generated Docs

FastAPI automatically generates interactive API documentation:

**Swagger UI**: http://localhost:8000/docs
- Interactive testing
- Try endpoints directly in browser
- View request/response schemas

**ReDoc**: http://localhost:8000/redoc
- Clean, readable documentation
- Three-panel layout
- Better for sharing with team

**OpenAPI Schema**: http://localhost:8000/openapi.json
- Machine-readable API specification
- Use for client generation
- Import into Postman/Insomnia
