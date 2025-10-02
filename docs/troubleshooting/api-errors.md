# API Error Troubleshooting Guide

Comprehensive guide for diagnosing and resolving API-related errors in the Multi-Modal Academic Research System.

## Table of Contents

- [HTTP Status Codes](#http-status-codes)
- [Request Validation Errors](#request-validation-errors)
- [Authentication Issues](#authentication-issues)
- [Rate Limiting](#rate-limiting)
- [Timeout Errors](#timeout-errors)
- [API-Specific Issues](#api-specific-issues)
- [Error Handling Best Practices](#error-handling-best-practices)

---

## HTTP Status Codes

### 400 Bad Request

**Meaning**: The server cannot process the request due to invalid syntax or parameters.

**Common Causes**:
- Malformed JSON in request body
- Missing required parameters
- Invalid parameter values
- Incorrect content type

**Example Error**:
```
400 Bad Request: {"error": "Invalid query parameter"}
```

**Solutions**:

1. **Validate request format**:
```python
import requests
import json

# Correct format
data = {
    "query": "machine learning",
    "max_results": 10
}

response = requests.post(
    api_url,
    headers={"Content-Type": "application/json"},
    data=json.dumps(data)  # Ensure proper JSON encoding
)

# Check response
if response.status_code == 400:
    print(f"Bad request: {response.json()}")
```

2. **Validate parameters**:
```python
def validate_query_params(params):
    """Validate API query parameters."""
    required = ['query']
    for field in required:
        if field not in params:
            raise ValueError(f"Missing required field: {field}")

    if 'max_results' in params:
        if not isinstance(params['max_results'], int):
            raise ValueError("max_results must be an integer")
        if params['max_results'] < 1 or params['max_results'] > 100:
            raise ValueError("max_results must be between 1 and 100")

    return True

# Use before making request
try:
    validate_query_params(params)
    response = requests.get(api_url, params=params)
except ValueError as e:
    print(f"Validation error: {e}")
```

---

### 401 Unauthorized

**Meaning**: Authentication is required or has failed.

**Common Causes**:
- Missing API key
- Invalid API key
- Expired credentials
- Wrong authentication method

**Example Error**:
```
401 Unauthorized: {"error": "Invalid API key"}
```

**Solutions**:

1. **Verify API key**:
```python
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('GEMINI_API_KEY')

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment")

# Test API key
response = requests.get(
    f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
)

if response.status_code == 401:
    print("Invalid API key. Get a new one from https://makersuite.google.com/app/apikey")
```

2. **Use correct authentication method**:
```python
# For Gemini API - use query parameter
import google.generativeai as genai

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-pro')

# For other APIs - use headers
headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}

response = requests.get(api_url, headers=headers)
```

3. **Handle expired credentials**:
```python
def call_api_with_retry(url, api_key):
    """Call API with automatic key refresh."""
    response = requests.get(
        url,
        headers={'Authorization': f'Bearer {api_key}'}
    )

    if response.status_code == 401:
        # Refresh credentials
        new_api_key = refresh_credentials()
        response = requests.get(
            url,
            headers={'Authorization': f'Bearer {new_api_key}'}
        )

    return response
```

---

### 403 Forbidden

**Meaning**: Server understands the request but refuses to authorize it.

**Common Causes**:
- Insufficient permissions
- API access not enabled
- Blocked by firewall or security policy
- Accessing restricted resources

**Example Error**:
```
403 Forbidden: {"error": "API not enabled for this project"}
```

**Solutions**:

1. **Enable required APIs**:
```bash
# For Google Cloud APIs
gcloud services enable generativelanguage.googleapis.com

# Or enable in console:
# https://console.cloud.google.com/apis/library
```

2. **Check API quotas and limits**:
```python
import google.generativeai as genai

try:
    response = model.generate_content(prompt)
except Exception as e:
    if "403" in str(e):
        print("API access denied. Check:")
        print("1. API is enabled in Google Cloud Console")
        print("2. Billing is enabled (if required)")
        print("3. You have necessary permissions")
```

3. **Verify resource access**:
```python
# Check if resource is accessible
response = requests.head(resource_url)

if response.status_code == 403:
    print(f"Access denied to {resource_url}")
    print("Possible reasons:")
    print("- Private resource")
    print("- Geographic restrictions")
    print("- Account limitations")
```

---

### 404 Not Found

**Meaning**: The requested resource doesn't exist.

**Common Causes**:
- Incorrect URL or endpoint
- Resource has been deleted
- Typo in resource ID
- API version mismatch

**Example Error**:
```
404 Not Found: {"error": "Resource not found"}
```

**Solutions**:

1. **Verify endpoint URL**:
```python
# Correct ArXiv API endpoint
ARXIV_API = "http://export.arxiv.org/api/query"

# Common mistakes:
# Wrong: "http://arxiv.org/api/query"
# Wrong: "http://export.arxiv.org/query"

response = requests.get(ARXIV_API, params=params)
if response.status_code == 404:
    print(f"Invalid endpoint: {ARXIV_API}")
```

2. **Validate resource IDs**:
```python
def validate_arxiv_id(arxiv_id):
    """Validate ArXiv ID format."""
    import re

    # Format: YYMM.NNNNN or YYMM.NNNNNN
    pattern = r'^\d{4}\.\d{4,5}(v\d+)?$'

    if not re.match(pattern, arxiv_id):
        raise ValueError(f"Invalid ArXiv ID format: {arxiv_id}")

    return True

# Use before fetching
try:
    validate_arxiv_id("2301.12345")
    response = fetch_paper(arxiv_id)
except ValueError as e:
    print(f"Validation error: {e}")
```

3. **Handle missing resources gracefully**:
```python
def fetch_resource_safe(resource_id):
    """Fetch resource with fallback."""
    response = requests.get(f"{api_url}/{resource_id}")

    if response.status_code == 404:
        print(f"Resource {resource_id} not found")
        # Try alternative source
        return fetch_from_alternative(resource_id)

    return response.json()
```

---

### 429 Too Many Requests

**Meaning**: Rate limit has been exceeded.

**Common Causes**:
- Too many requests in short time
- Exceeded quota limits
- No rate limiting implemented
- Multiple concurrent requests

**Example Error**:
```
429 Too Many Requests: {"error": "Rate limit exceeded. Retry after 60 seconds."}
```

**Solutions**:

1. **Implement rate limiting**:
```python
import time
from functools import wraps

def rate_limit(calls_per_second=1):
    """Decorator to rate limit function calls."""
    min_interval = 1.0 / calls_per_second
    last_called = [0.0]

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            wait_time = min_interval - elapsed

            if wait_time > 0:
                time.sleep(wait_time)

            result = func(*args, **kwargs)
            last_called[0] = time.time()
            return result

        return wrapper
    return decorator

@rate_limit(calls_per_second=2)  # Max 2 calls per second
def call_api(url):
    return requests.get(url)
```

2. **Implement exponential backoff**:
```python
import time
import random

def exponential_backoff(func, max_retries=5):
    """Retry with exponential backoff."""
    for attempt in range(max_retries):
        try:
            response = func()

            if response.status_code == 429:
                # Check Retry-After header
                retry_after = response.headers.get('Retry-After')

                if retry_after:
                    wait_time = int(retry_after)
                else:
                    # Exponential backoff: 2^attempt + random jitter
                    wait_time = (2 ** attempt) + random.uniform(0, 1)

                print(f"Rate limited. Waiting {wait_time}s...")
                time.sleep(wait_time)
                continue

            return response

        except Exception as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)

    raise Exception(f"Max retries ({max_retries}) exceeded")

# Usage
response = exponential_backoff(
    lambda: requests.get(api_url, params=params)
)
```

3. **Use token bucket algorithm**:
```python
import threading
import time

class TokenBucket:
    """Token bucket rate limiter."""

    def __init__(self, rate, capacity):
        """
        Args:
            rate: Tokens added per second
            capacity: Maximum tokens
        """
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last_update = time.time()
        self.lock = threading.Lock()

    def consume(self, tokens=1):
        """Consume tokens, waiting if necessary."""
        with self.lock:
            # Refill tokens
            now = time.time()
            elapsed = now - self.last_update
            self.tokens = min(
                self.capacity,
                self.tokens + elapsed * self.rate
            )
            self.last_update = now

            # Wait if not enough tokens
            if self.tokens < tokens:
                wait_time = (tokens - self.tokens) / self.rate
                time.sleep(wait_time)
                self.tokens = 0
            else:
                self.tokens -= tokens

            return True

# Usage
limiter = TokenBucket(rate=10, capacity=20)  # 10 requests/sec

def make_api_call():
    limiter.consume()
    return requests.get(api_url)
```

---

### 500 Internal Server Error

**Meaning**: Server encountered an unexpected condition.

**Common Causes**:
- Server-side bug
- Database issues
- Timeout on server
- Invalid data causing crash

**Example Error**:
```
500 Internal Server Error: {"error": "Internal server error"}
```

**Solutions**:

1. **Retry with backoff**:
```python
def retry_on_server_error(func, max_retries=3):
    """Retry on 5xx errors."""
    for attempt in range(max_retries):
        try:
            response = func()

            if 500 <= response.status_code < 600:
                print(f"Server error (attempt {attempt + 1}/{max_retries})")
                time.sleep(2 ** attempt)
                continue

            return response

        except Exception as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)

    return None
```

2. **Validate input data**:
```python
def sanitize_input(text):
    """Clean input to prevent server errors."""
    # Remove null bytes
    text = text.replace('\x00', '')

    # Limit length
    max_length = 10000
    if len(text) > max_length:
        text = text[:max_length]

    # Remove invalid unicode
    text = text.encode('utf-8', 'ignore').decode('utf-8')

    return text

# Use before API calls
cleaned_text = sanitize_input(user_input)
response = api_call(cleaned_text)
```

3. **Log errors for debugging**:
```python
import logging

logging.basicConfig(level=logging.ERROR)

def call_api_with_logging(url, data):
    """Call API with comprehensive logging."""
    try:
        response = requests.post(url, json=data)

        if response.status_code == 500:
            logging.error(f"Server error for URL: {url}")
            logging.error(f"Request data: {data}")
            logging.error(f"Response: {response.text}")

        return response

    except Exception as e:
        logging.error(f"Exception calling {url}: {e}")
        raise
```

---

### 503 Service Unavailable

**Meaning**: Server is temporarily unable to handle the request.

**Common Causes**:
- Server maintenance
- Overloaded server
- Temporary outage
- Dependency failure

**Solutions**:

1. **Implement circuit breaker**:
```python
import time

class CircuitBreaker:
    """Circuit breaker pattern for API calls."""

    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failures = 0
        self.last_failure_time = None
        self.state = 'closed'  # closed, open, half_open

    def call(self, func):
        """Execute function with circuit breaker."""
        if self.state == 'open':
            if time.time() - self.last_failure_time > self.timeout:
                self.state = 'half_open'
            else:
                raise Exception("Circuit breaker is open")

        try:
            result = func()

            if self.state == 'half_open':
                self.state = 'closed'
                self.failures = 0

            return result

        except Exception as e:
            self.failures += 1
            self.last_failure_time = time.time()

            if self.failures >= self.failure_threshold:
                self.state = 'open'

            raise

# Usage
breaker = CircuitBreaker(failure_threshold=3, timeout=60)

def make_api_call():
    try:
        return breaker.call(lambda: requests.get(api_url))
    except Exception as e:
        print(f"Circuit breaker error: {e}")
        return None
```

2. **Check service status**:
```python
def check_service_health(base_url):
    """Check if service is available."""
    health_endpoint = f"{base_url}/health"

    try:
        response = requests.get(health_endpoint, timeout=5)
        return response.status_code == 200
    except:
        return False

# Use before making requests
if not check_service_health(api_base_url):
    print("Service is unavailable. Waiting...")
    time.sleep(30)
```

---

## Request Validation Errors

### Invalid JSON Format

**Problem**: Request body is not valid JSON.

**Solutions**:

```python
import json

def safe_json_request(url, data):
    """Make JSON request with validation."""
    try:
        # Validate JSON before sending
        json_data = json.dumps(data)
        json.loads(json_data)  # Verify it's valid

        response = requests.post(
            url,
            headers={'Content-Type': 'application/json'},
            data=json_data
        )

        return response

    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}")
        return None
```

---

### Missing Required Fields

**Problem**: Required parameters not provided.

**Solutions**:

```python
from typing import Dict, List

def validate_required_fields(data: Dict, required: List[str]):
    """Validate required fields in request."""
    missing = [field for field in required if field not in data]

    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")

    return True

# Usage
request_data = {
    'query': 'machine learning',
    'max_results': 10
}

required_fields = ['query', 'max_results']

try:
    validate_required_fields(request_data, required_fields)
    response = requests.post(api_url, json=request_data)
except ValueError as e:
    print(f"Validation error: {e}")
```

---

### Invalid Parameter Types

**Problem**: Parameters have wrong data types.

**Solutions**:

```python
from typing import Any, Dict, Type

def validate_types(data: Dict[str, Any], schema: Dict[str, Type]):
    """Validate parameter types."""
    for field, expected_type in schema.items():
        if field in data:
            if not isinstance(data[field], expected_type):
                raise TypeError(
                    f"Field '{field}' must be {expected_type.__name__}, "
                    f"got {type(data[field]).__name__}"
                )

    return True

# Usage
schema = {
    'query': str,
    'max_results': int,
    'include_abstract': bool
}

try:
    validate_types(request_data, schema)
    response = requests.post(api_url, json=request_data)
except TypeError as e:
    print(f"Type error: {e}")
```

---

## API-Specific Issues

### Gemini API

**Common Errors**:

1. **Safety settings blocking**:
```python
import google.generativeai as genai

# Configure safety settings
safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    }
]

model = genai.GenerativeModel(
    'gemini-pro',
    safety_settings=safety_settings
)

try:
    response = model.generate_content(prompt)
except Exception as e:
    if "safety" in str(e).lower():
        print("Content blocked by safety filters")
        print("Try rephrasing or adjusting safety settings")
```

2. **Token limit exceeded**:
```python
def truncate_prompt(prompt, max_tokens=30000):
    """Truncate prompt to fit token limit."""
    # Rough estimate: 1 token ≈ 4 characters
    max_chars = max_tokens * 4

    if len(prompt) > max_chars:
        prompt = prompt[:max_chars]
        print(f"Prompt truncated to {max_tokens} tokens")

    return prompt

# Usage
safe_prompt = truncate_prompt(long_prompt)
response = model.generate_content(safe_prompt)
```

---

### ArXiv API

**Common Errors**:

1. **Malformed query**:
```python
def build_arxiv_query(search_terms, category=None):
    """Build valid ArXiv query."""
    # Escape special characters
    search_terms = search_terms.replace('"', '\\"')

    # Build query
    query_parts = [f'all:{search_terms}']

    if category:
        query_parts.append(f'cat:{category}')

    return ' AND '.join(query_parts)

# Usage
query = build_arxiv_query("machine learning", category="cs.LG")
```

2. **Empty results**:
```python
import arxiv

def search_arxiv_with_fallback(query, max_results=10):
    """Search ArXiv with fallback to broader query."""
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance
    )

    results = list(search.results())

    if not results:
        # Try broader query
        broader_query = query.split()[0]  # Use first word only
        search = arxiv.Search(
            query=broader_query,
            max_results=max_results
        )
        results = list(search.results())

    return results
```

---

### YouTube API

**Common Errors**:

1. **Transcript not available**:
```python
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    NoTranscriptFound,
    TranscriptsDisabled
)

def get_transcript_safe(video_id):
    """Get transcript with error handling."""
    try:
        # Try to get transcript
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return transcript

    except NoTranscriptFound:
        # Try auto-generated captions
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            transcript = transcript_list.find_generated_transcript(['en'])
            return transcript.fetch()
        except:
            print(f"No transcript available for {video_id}")
            return None

    except TranscriptsDisabled:
        print(f"Transcripts disabled for {video_id}")
        return None
```

---

## Error Handling Best Practices

### Comprehensive Error Handler

```python
import requests
from requests.exceptions import (
    Timeout,
    ConnectionError,
    HTTPError,
    RequestException
)
import logging

logging.basicConfig(level=logging.INFO)

def robust_api_call(url, method='GET', **kwargs):
    """Make API call with comprehensive error handling."""
    max_retries = 3
    timeout = kwargs.get('timeout', 30)

    for attempt in range(max_retries):
        try:
            # Make request
            if method == 'GET':
                response = requests.get(url, timeout=timeout, **kwargs)
            elif method == 'POST':
                response = requests.post(url, timeout=timeout, **kwargs)
            else:
                raise ValueError(f"Unsupported method: {method}")

            # Check status code
            if response.status_code == 200:
                return response

            elif response.status_code == 400:
                logging.error(f"Bad request: {response.text}")
                return None

            elif response.status_code == 401:
                logging.error("Authentication failed")
                return None

            elif response.status_code == 403:
                logging.error("Access forbidden")
                return None

            elif response.status_code == 404:
                logging.error(f"Resource not found: {url}")
                return None

            elif response.status_code == 429:
                wait_time = int(response.headers.get('Retry-After', 60))
                logging.warning(f"Rate limited. Waiting {wait_time}s...")
                time.sleep(wait_time)
                continue

            elif 500 <= response.status_code < 600:
                logging.error(f"Server error: {response.status_code}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return None

            else:
                logging.error(f"Unexpected status: {response.status_code}")
                return None

        except Timeout:
            logging.error(f"Request timeout (attempt {attempt + 1}/{max_retries})")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            return None

        except ConnectionError:
            logging.error(f"Connection error (attempt {attempt + 1}/{max_retries})")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            return None

        except RequestException as e:
            logging.error(f"Request exception: {e}")
            return None

    return None

# Usage
response = robust_api_call(
    'https://api.example.com/data',
    method='GET',
    params={'query': 'test'},
    timeout=30
)

if response:
    data = response.json()
else:
    print("API call failed after retries")
```

---

## Additional Resources

- [Common Issues](./common-issues.md)
- [OpenSearch Troubleshooting](./opensearch.md)
- [FAQ](./faq.md)
- [Performance Optimization](../advanced/performance.md)
