# REST API Reference

## Overview

The Multi-Modal Research Data API is a FastAPI-based REST service that provides programmatic access to the collected research data stored in the SQLite database. The API allows querying collections, retrieving detailed information, searching, and viewing statistics.

**Base URL**: `http://localhost:8000` (default)
**API Version**: 1.0.0
**Framework**: FastAPI 0.x
**Documentation**: Auto-generated Swagger UI available at `/docs`

## Starting the API Server

```bash
# Method 1: Direct execution
python -m multi_modal_rag.api.api_server

# Method 2: Using uvicorn
uvicorn multi_modal_rag.api.api_server:app --host 0.0.0.0 --port 8000

# Method 3: With auto-reload for development
uvicorn multi_modal_rag.api.api_server:app --reload
```

## Interactive Documentation

FastAPI provides automatic interactive API documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`

## CORS Configuration

The API is configured with permissive CORS settings to allow frontend access:

```python
allow_origins=["*"]
allow_credentials=True
allow_methods=["*"]
allow_headers=["*"]
```

**Note**: In production, restrict `allow_origins` to specific domains.

---

## Endpoints

### 1. Root Endpoint

Get API information and available endpoints.

#### Request

```http
GET /
```

#### Parameters

None

#### Response

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

#### Example

```bash
curl http://localhost:8000/
```

---

### 2. Get Collections

Retrieve all collections with optional filtering and pagination.

#### Request

```http
GET /api/collections
```

#### Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `content_type` | string | No | None | Filter by content type: `paper`, `video`, or `podcast` |
| `limit` | integer | No | 100 | Maximum number of results (1-1000) |
| `offset` | integer | No | 0 | Offset for pagination (≥0) |

#### Response

**Status**: 200 OK

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
      "collection_date": "2025-10-01 10:30:00",
      "metadata": {
        "keywords": ["transformers", "attention"]
      },
      "status": "collected",
      "indexed": 1
    },
    ...
  ]
}
```

#### Error Responses

**Status**: 500 Internal Server Error

```json
{
  "detail": "Error message"
}
```

#### Examples

**Get all collections (default pagination)**

```bash
curl http://localhost:8000/api/collections
```

**Get only papers**

```bash
curl "http://localhost:8000/api/collections?content_type=paper"
```

**Get videos with custom pagination**

```bash
curl "http://localhost:8000/api/collections?content_type=video&limit=50&offset=100"
```

**Get podcasts (first 20)**

```bash
curl "http://localhost:8000/api/collections?content_type=podcast&limit=20"
```

#### Python Example

```python
import requests

response = requests.get(
    'http://localhost:8000/api/collections',
    params={
        'content_type': 'paper',
        'limit': 50,
        'offset': 0
    }
)

data = response.json()
print(f"Found {data['count']} collections")
for collection in data['collections']:
    print(f"  - {collection['title']}")
```

---

### 3. Get Collection Details

Retrieve detailed information about a specific collection, including type-specific data.

#### Request

```http
GET /api/collections/{collection_id}
```

#### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `collection_id` | integer | Yes | Unique collection ID |

#### Response

**Status**: 200 OK

**For a paper:**

```json
{
  "id": 1,
  "content_type": "paper",
  "title": "Attention Is All You Need",
  "source": "arxiv",
  "url": "https://arxiv.org/abs/1706.03762",
  "collection_date": "2025-10-01 10:30:00",
  "metadata": {
    "keywords": ["transformers"]
  },
  "status": "collected",
  "indexed": 1,
  "details": {
    "id": 1,
    "collection_id": 1,
    "arxiv_id": "1706.03762",
    "pmc_id": null,
    "abstract": "The dominant sequence transduction models...",
    "authors": ["Ashish Vaswani", "Noam Shazeer", "Niki Parmar"],
    "published_date": "2017-06-12",
    "categories": ["cs.CL", "cs.AI", "cs.LG"],
    "pdf_path": "data/papers/arxiv_1706.03762.pdf"
  }
}
```

**For a video:**

```json
{
  "id": 2,
  "content_type": "video",
  "title": "Neural Networks Explained",
  "source": "youtube",
  "url": "https://youtube.com/watch?v=abc123",
  "collection_date": "2025-10-01 11:00:00",
  "metadata": {},
  "status": "collected",
  "indexed": 1,
  "details": {
    "id": 1,
    "collection_id": 2,
    "video_id": "abc123",
    "channel": "3Blue1Brown",
    "duration": 1194,
    "views": 5234891,
    "thumbnail_url": "https://i.ytimg.com/vi/abc123/maxresdefault.jpg",
    "transcript_available": 1
  }
}
```

**For a podcast:**

```json
{
  "id": 3,
  "content_type": "podcast",
  "title": "AI Safety Discussion",
  "source": "podcast_rss",
  "url": "https://podcast.ai/ep42",
  "collection_date": "2025-10-02 09:15:00",
  "metadata": {},
  "status": "collected",
  "indexed": 0,
  "details": {
    "id": 1,
    "collection_id": 3,
    "episode_id": "ep-42",
    "podcast_name": "AI Alignment Podcast",
    "audio_url": "https://podcast.ai/audio/ep42.mp3",
    "duration": 3600
  }
}
```

#### Error Responses

**Status**: 404 Not Found

```json
{
  "detail": "Collection not found"
}
```

**Status**: 500 Internal Server Error

```json
{
  "detail": "Error message"
}
```

#### Examples

```bash
# Get collection with ID 1
curl http://localhost:8000/api/collections/1

# Get collection with ID 42
curl http://localhost:8000/api/collections/42
```

#### Python Example

```python
import requests

collection_id = 1
response = requests.get(f'http://localhost:8000/api/collections/{collection_id}')

if response.status_code == 200:
    collection = response.json()
    print(f"Title: {collection['title']}")
    print(f"Type: {collection['content_type']}")

    if 'details' in collection:
        if collection['content_type'] == 'paper':
            print(f"Authors: {', '.join(collection['details']['authors'])}")
        elif collection['content_type'] == 'video':
            print(f"Channel: {collection['details']['channel']}")
elif response.status_code == 404:
    print("Collection not found")
```

---

### 4. Get Statistics

Retrieve database statistics including counts by type, indexing status, and collection history.

#### Request

```http
GET /api/statistics
```

#### Parameters

None

#### Response

**Status**: 200 OK

```json
{
  "by_type": {
    "paper": 1523,
    "video": 342,
    "podcast": 87
  },
  "indexed": 1845,
  "not_indexed": 107,
  "recent_7_days": 23,
  "collection_history": [
    {
      "type": "paper",
      "source": "arxiv",
      "total": 1200
    },
    {
      "type": "paper",
      "source": "pubmed",
      "total": 323
    },
    {
      "type": "video",
      "source": "youtube",
      "total": 342
    }
  ]
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `by_type` | object | Count of collections by content type |
| `indexed` | integer | Number of indexed collections |
| `not_indexed` | integer | Number of not-yet-indexed collections |
| `recent_7_days` | integer | Collections added in last 7 days |
| `collection_history` | array | Breakdown by type and source API |

#### Error Responses

**Status**: 500 Internal Server Error

```json
{
  "detail": "Error message"
}
```

#### Examples

```bash
curl http://localhost:8000/api/statistics
```

#### Python Example

```python
import requests

response = requests.get('http://localhost:8000/api/statistics')
stats = response.json()

print("Collection Statistics:")
print(f"  Total Papers: {stats['by_type'].get('paper', 0)}")
print(f"  Total Videos: {stats['by_type'].get('video', 0)}")
print(f"  Total Podcasts: {stats['by_type'].get('podcast', 0)}")
print(f"  Indexed: {stats['indexed']}")
print(f"  Not Indexed: {stats['not_indexed']}")
print(f"  Added in Last 7 Days: {stats['recent_7_days']}")
```

---

### 5. Search Collections

Search collections by title or source using substring matching.

#### Request

```http
GET /api/search
```

#### Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `q` | string | Yes | - | Search query (minimum 1 character) |
| `limit` | integer | No | 50 | Maximum number of results (1-500) |

#### Response

**Status**: 200 OK

```json
{
  "query": "machine learning",
  "count": 12,
  "results": [
    {
      "id": 5,
      "content_type": "paper",
      "title": "Deep Learning for Machine Translation",
      "source": "arxiv",
      "url": "https://arxiv.org/abs/...",
      "collection_date": "2025-10-01 14:20:00",
      "metadata": {},
      "status": "collected",
      "indexed": 1
    },
    ...
  ]
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `query` | string | The search query that was executed |
| `count` | integer | Number of results found |
| `results` | array | Array of matching collection objects |

#### Error Responses

**Status**: 422 Unprocessable Entity

```json
{
  "detail": [
    {
      "loc": ["query", "q"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**Status**: 500 Internal Server Error

```json
{
  "detail": "Error message"
}
```

#### Examples

**Search for "transformer"**

```bash
curl "http://localhost:8000/api/search?q=transformer"
```

**Search for "neural network" with limit**

```bash
curl "http://localhost:8000/api/search?q=neural%20network&limit=20"
```

**Search by source**

```bash
curl "http://localhost:8000/api/search?q=arxiv"
```

#### Python Example

```python
import requests

response = requests.get(
    'http://localhost:8000/api/search',
    params={
        'q': 'machine learning',
        'limit': 30
    }
)

data = response.json()
print(f"Search: '{data['query']}' - Found {data['count']} results")

for result in data['results']:
    print(f"  [{result['content_type']}] {result['title']}")
```

#### Search Behavior

- Case-insensitive substring matching
- Searches both `title` and `source` fields
- Uses SQL `LIKE` operator with wildcards: `%query%`
- Results ordered by `collection_date` DESC (newest first)

---

### 6. Visualization Page

Serve the HTML visualization page for browsing collected data.

#### Request

```http
GET /viz
```

#### Parameters

None

#### Response

**Status**: 200 OK

**Content-Type**: `text/html`

Returns the HTML content of the visualization page if available, or a fallback message if the file is not found.

#### Examples

```bash
# Open in browser
open http://localhost:8000/viz

# Or with curl
curl http://localhost:8000/viz
```

#### File Location

Expected file: `multi_modal_rag/api/static/visualization.html`

---

### 7. Health Check

Simple health check endpoint to verify API is running.

#### Request

```http
GET /health
```

#### Parameters

None

#### Response

**Status**: 200 OK

```json
{
  "status": "healthy"
}
```

#### Examples

```bash
curl http://localhost:8000/health
```

#### Use Cases

- Container orchestration health checks
- Load balancer status monitoring
- Automated testing
- CI/CD pipeline verification

---

## Complete cURL Examples

### Basic Workflow

```bash
# 1. Check API is running
curl http://localhost:8000/health

# 2. Get API information
curl http://localhost:8000/

# 3. Get statistics
curl http://localhost:8000/api/statistics

# 4. Get all collections
curl http://localhost:8000/api/collections

# 5. Get only papers
curl "http://localhost:8000/api/collections?content_type=paper&limit=10"

# 6. Search for specific topic
curl "http://localhost:8000/api/search?q=attention%20mechanism"

# 7. Get details of specific collection
curl http://localhost:8000/api/collections/1
```

### Advanced Examples

**Pagination through all papers**

```bash
# Page 1
curl "http://localhost:8000/api/collections?content_type=paper&limit=100&offset=0"

# Page 2
curl "http://localhost:8000/api/collections?content_type=paper&limit=100&offset=100"

# Page 3
curl "http://localhost:8000/api/collections?content_type=paper&limit=100&offset=200"
```

**With authentication (if implemented)**

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8000/api/collections
```

**Save response to file**

```bash
curl http://localhost:8000/api/statistics -o statistics.json
```

**Pretty print JSON output (with jq)**

```bash
curl http://localhost:8000/api/collections | jq .
```

---

## Python Client Example

Complete Python client for interacting with the API:

```python
import requests
from typing import Optional, List, Dict

class ResearchDataAPIClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')

    def health_check(self) -> bool:
        """Check if API is healthy"""
        try:
            response = requests.get(f"{self.base_url}/health")
            return response.status_code == 200
        except:
            return False

    def get_collections(
        self,
        content_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Dict:
        """Get collections with optional filtering"""
        params = {'limit': limit, 'offset': offset}
        if content_type:
            params['content_type'] = content_type

        response = requests.get(
            f"{self.base_url}/api/collections",
            params=params
        )
        response.raise_for_status()
        return response.json()

    def get_collection_details(self, collection_id: int) -> Dict:
        """Get detailed information about a collection"""
        response = requests.get(
            f"{self.base_url}/api/collections/{collection_id}"
        )
        response.raise_for_status()
        return response.json()

    def get_statistics(self) -> Dict:
        """Get database statistics"""
        response = requests.get(f"{self.base_url}/api/statistics")
        response.raise_for_status()
        return response.json()

    def search(self, query: str, limit: int = 50) -> Dict:
        """Search collections by title or source"""
        response = requests.get(
            f"{self.base_url}/api/search",
            params={'q': query, 'limit': limit}
        )
        response.raise_for_status()
        return response.json()

# Usage
client = ResearchDataAPIClient()

# Check health
if client.health_check():
    print("API is healthy")

    # Get statistics
    stats = client.get_statistics()
    print(f"Total papers: {stats['by_type'].get('paper', 0)}")

    # Search
    results = client.search("transformers", limit=10)
    print(f"Found {results['count']} results")

    # Get details
    if results['count'] > 0:
        first_id = results['results'][0]['id']
        details = client.get_collection_details(first_id)
        print(f"Title: {details['title']}")
```

---

## Error Handling

### HTTP Status Codes

| Code | Meaning | When It Occurs |
|------|---------|----------------|
| 200 | OK | Successful request |
| 404 | Not Found | Collection ID doesn't exist |
| 422 | Unprocessable Entity | Invalid query parameters |
| 500 | Internal Server Error | Database or server error |

### Error Response Format

All errors return JSON with a `detail` field:

```json
{
  "detail": "Human-readable error message"
}
```

For validation errors (422), the detail is an array:

```json
{
  "detail": [
    {
      "loc": ["query", "limit"],
      "msg": "ensure this value is less than or equal to 1000",
      "type": "value_error.number.not_le"
    }
  ]
}
```

---

## Rate Limiting

Currently, the API has **no rate limiting** implemented. For production use, consider:

- Adding rate limiting middleware (e.g., `slowapi`)
- Implementing per-IP request limits
- Adding authentication and per-user quotas

---

## Security Considerations

### Current State

- No authentication required
- CORS allows all origins
- No rate limiting
- Suitable for local/development use only

### Production Recommendations

1. **Add Authentication**
   ```python
   from fastapi.security import HTTPBearer
   security = HTTPBearer()
   ```

2. **Restrict CORS**
   ```python
   allow_origins=["https://yourdomain.com"]
   ```

3. **Add Rate Limiting**
   ```python
   from slowapi import Limiter
   limiter = Limiter(key_func=get_remote_address)
   ```

4. **Use HTTPS**
   - Deploy behind reverse proxy (nginx, Caddy)
   - Use SSL certificates

5. **Input Validation**
   - Already implemented via FastAPI/Pydantic
   - Additional sanitization for search queries

---

## Deployment

### Development

```bash
uvicorn multi_modal_rag.api.api_server:app --reload --host 127.0.0.1 --port 8000
```

### Production (with Gunicorn)

```bash
gunicorn multi_modal_rag.api.api_server:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

### Docker

```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "multi_modal_rag.api.api_server:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables

```bash
# Database path
export DB_PATH=/path/to/collections.db

# API host and port
export API_HOST=0.0.0.0
export API_PORT=8000
```

---

## Monitoring and Logging

The API uses the application's logging configuration from `multi_modal_rag.logging_config`.

**Log Locations**: Check `logs/` directory or console output

**Log Levels**:
- INFO: Normal operations
- ERROR: Database errors, exceptions

**Example Log Output**:
```
2025-10-02 10:30:00 - INFO - CollectionDatabaseManager initialized
2025-10-02 10:30:05 - INFO - Starting FastAPI server...
2025-10-02 10:30:15 - ERROR - Error fetching collections: database is locked
```

---

## Testing

### Manual Testing

Use the interactive Swagger UI: `http://localhost:8000/docs`

### Automated Testing

```python
import pytest
from fastapi.testclient import TestClient
from multi_modal_rag.api.api_server import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_get_collections():
    response = client.get("/api/collections")
    assert response.status_code == 200
    assert "count" in response.json()
    assert "collections" in response.json()

def test_search():
    response = client.get("/api/search?q=test")
    assert response.status_code == 200
    assert "query" in response.json()
    assert response.json()["query"] == "test"
```

Run tests:
```bash
pytest tests/test_api.py
```
