# Common Issues and Solutions

This guide covers the most frequently encountered issues when using the Multi-Modal Academic Research System.

## Table of Contents

- [Installation Issues](#installation-issues)
- [Runtime Errors](#runtime-errors)
- [Data Collection Failures](#data-collection-failures)
- [Search Problems](#search-problems)
- [UI Issues](#ui-issues)
- [Configuration Issues](#configuration-issues)
- [Performance Issues](#performance-issues)

---

## Installation Issues

### 1. pip install fails with dependency conflicts

**Problem**: Installation fails with messages about incompatible package versions.

**Cause**: Conflicting dependencies between packages or outdated pip.

**Solution**:
```bash
# Update pip first
pip install --upgrade pip

# Install with --upgrade flag
pip install --upgrade -r requirements.txt

# If still failing, use a clean virtual environment
deactivate
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Prevention**: Always use a virtual environment and keep pip updated.

---

### 2. ModuleNotFoundError after installation

**Problem**: `ModuleNotFoundError: No module named 'opensearchpy'` or similar.

**Cause**: Virtual environment not activated or installation incomplete.

**Solution**:
```bash
# Ensure venv is activated (you should see (venv) in prompt)
source venv/bin/activate  # Mac/Linux
# or
venv\Scripts\activate  # Windows

# Verify installation
pip list | grep opensearch

# Reinstall if needed
pip install opensearch-py
```

**Prevention**: Always activate virtual environment before running the application.

---

### 3. Python version compatibility issues

**Problem**: Syntax errors or import failures related to Python version.

**Cause**: Using Python < 3.8 (minimum required version).

**Solution**:
```bash
# Check Python version
python --version

# Use Python 3.8+ to create virtual environment
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Prevention**: Ensure Python 3.8 or higher is installed before starting.

---

### 4. SSL certificate verification failed

**Problem**: `SSLError: [SSL: CERTIFICATE_VERIFY_FAILED]` during package installation.

**Cause**: Corporate proxy or network security blocking SSL connections.

**Solution**:
```bash
# Option 1: Update certificates (recommended)
pip install --upgrade certifi

# Option 2: Use trusted host (less secure)
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
```

**Prevention**: Ensure your network allows HTTPS connections to PyPI.

---

## Runtime Errors

### 5. Gemini API key not found or invalid

**Problem**: `Error: GEMINI_API_KEY not found in environment` or 401 Unauthorized.

**Cause**: Missing or incorrect API key in `.env` file.

**Solution**:
```bash
# Create .env file from example
cp .env.example .env

# Edit .env and add your key
# GEMINI_API_KEY=your_actual_api_key_here

# Get API key from: https://makersuite.google.com/app/apikey
```

**Prevention**: Verify API key validity by testing in Google AI Studio first.

---

### 6. OpenSearch connection refused

**Problem**: `ConnectionError: Connection to OpenSearch failed` or similar.

**Cause**: OpenSearch service not running or wrong host/port.

**Solution**:
```bash
# Check if OpenSearch is running
curl http://localhost:9200

# If not running, start Docker container
docker run -p 9200:9200 -p 9600:9600 \
  -e "discovery.type=single-node" \
  -e "DISABLE_SECURITY_PLUGIN=true" \
  opensearchproject/opensearch:latest

# Verify connection
curl http://localhost:9200/_cluster/health
```

**Prevention**: Start OpenSearch before running the application.

---

### 7. Out of memory errors

**Problem**: `MemoryError` or process killed during processing.

**Cause**: Processing large PDFs or too many documents simultaneously.

**Solution**:
```python
# Reduce batch size in opensearch_manager.py
# Change from:
bulk_data = []  # Process all at once

# To:
BATCH_SIZE = 100
for i in range(0, len(documents), BATCH_SIZE):
    batch = documents[i:i+BATCH_SIZE]
    # Process batch
```

**Prevention**: Process documents in smaller batches, increase system memory.

---

### 8. Rate limiting from external APIs

**Problem**: `HTTP 429: Too Many Requests` from ArXiv, YouTube, etc.

**Cause**: Sending too many requests too quickly.

**Solution**:
```python
# Add delays between requests in collectors
import time

for query in queries:
    results = fetch_data(query)
    time.sleep(3)  # Wait 3 seconds between requests
```

**Prevention**: Implement exponential backoff and respect API rate limits.

---

### 9. Encoding errors when processing PDFs

**Problem**: `UnicodeDecodeError` or garbled text from PDFs.

**Cause**: PDFs with non-standard encoding or scanned images.

**Solution**:
```python
# In pdf_processor.py, handle encoding errors gracefully
try:
    text = page.get_text(encoding='utf-8')
except UnicodeDecodeError:
    text = page.get_text(encoding='utf-8', errors='ignore')

# For scanned PDFs, consider OCR
from pdf2image import convert_from_path
import pytesseract

images = convert_from_path(pdf_path)
text = pytesseract.image_to_string(images[0])
```

**Prevention**: Validate PDF quality before processing.

---

### 10. Gradio interface won't start

**Problem**: `OSError: [Errno 48] Address already in use` or similar.

**Cause**: Port 7860 already occupied by another process.

**Solution**:
```bash
# Find process using port 7860
lsof -i :7860

# Kill the process
kill -9 <PID>

# Or use different port in main.py
interface.launch(server_port=7861, share=True)
```

**Prevention**: Check port availability before launching.

---

## Data Collection Failures

### 11. ArXiv queries return no results

**Problem**: Searches return empty results or errors.

**Cause**: Invalid query syntax or overly restrictive search terms.

**Solution**:
```python
# Use broader search terms
query = "machine learning"  # Instead of very specific terms

# Check ArXiv query syntax
# Valid: ti:"neural networks"
# Invalid: title:neural networks (wrong field name)

# Test query directly at https://arxiv.org/search/
```

**Prevention**: Start with broad queries and refine based on results.

---

### 12. YouTube transcript not available

**Problem**: `NoTranscriptFound` or `TranscriptsDisabled` error.

**Cause**: Video doesn't have captions or they're disabled.

**Solution**:
```python
# Add error handling in youtube_collector.py
from youtube_transcript_api._errors import NoTranscriptFound

try:
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
except NoTranscriptFound:
    print(f"No transcript for {video_id}, skipping...")
    continue
```

**Prevention**: Filter for videos with available transcripts.

---

### 13. PDF download fails

**Problem**: PDFs fail to download from ArXiv or other sources.

**Cause**: Network issues, invalid URLs, or access restrictions.

**Solution**:
```python
# Add retry logic with exponential backoff
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

session = requests.Session()
retry = Retry(total=3, backoff_factor=1)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)

response = session.get(pdf_url, timeout=30)
```

**Prevention**: Implement robust error handling and retry mechanisms.

---

### 14. Podcast RSS feed parsing errors

**Problem**: `XMLSyntaxError` or malformed feed errors.

**Cause**: Invalid or non-standard RSS feed format.

**Solution**:
```python
# Use feedparser which is more forgiving
import feedparser

feed = feedparser.parse(rss_url)
if feed.bozo:  # Indicates malformed feed
    print(f"Warning: Malformed feed {rss_url}")
    # Still try to extract data
    entries = feed.entries
```

**Prevention**: Validate RSS URLs before processing.

---

### 15. Semantic Scholar API timeouts

**Problem**: Requests to Semantic Scholar timeout or fail.

**Cause**: API server issues or network latency.

**Solution**:
```python
# Increase timeout and add retry logic
import requests

try:
    response = requests.get(
        api_url,
        timeout=60,  # Increase from default
        headers={'User-Agent': 'YourApp/1.0'}
    )
    response.raise_for_status()
except requests.Timeout:
    print("Request timed out, retrying...")
    time.sleep(5)
    response = requests.get(api_url, timeout=90)
```

**Prevention**: Monitor API status at https://api.semanticscholar.org/

---

## Search Problems

### 16. Search returns no results

**Problem**: Queries return empty results even though documents are indexed.

**Cause**: Mismatch between query terms and indexed content, or index not created.

**Solution**:
```bash
# Check if index exists and has documents
curl http://localhost:9200/research_assistant/_count

# Check index mapping
curl http://localhost:9200/research_assistant/_mapping

# Try broader query
# Instead of: "specific technical term"
# Try: "general concept"
```

**Prevention**: Verify indexing completed successfully before querying.

---

### 17. Search results are irrelevant

**Problem**: Results don't match query intent or are poorly ranked.

**Cause**: Incorrect field weights or hybrid search configuration.

**Solution**:
```python
# Adjust field weights in opensearch_manager.py
query = {
    "query": {
        "multi_match": {
            "query": query_text,
            "fields": [
                "title^3",      # Increase title weight
                "abstract^2",   # Increase abstract weight
                "content^1",
                "key_concepts^2"
            ]
        }
    }
}
```

**Prevention**: Test with various queries and tune weights accordingly.

---

### 18. Embeddings generation is slow

**Problem**: Generating embeddings takes too long during indexing.

**Cause**: Processing on CPU instead of GPU or large batch size.

**Solution**:
```python
# Use GPU if available
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
if torch.cuda.is_available():
    model = model.to('cuda')

# Process in smaller batches
embeddings = model.encode(
    texts,
    batch_size=32,  # Reduce if memory issues
    show_progress_bar=True
)
```

**Prevention**: Use GPU-enabled environment for large-scale indexing.

---

### 19. kNN search fails or returns errors

**Problem**: Vector search errors like `invalid knn query` or no results.

**Cause**: Index not configured for kNN or embedding dimension mismatch.

**Solution**:
```python
# Verify index has kNN settings
curl http://localhost:9200/research_assistant/_settings

# Recreate index with correct kNN configuration
index_settings = {
    "settings": {
        "index": {
            "knn": True,
            "knn.space_type": "cosinesimil"
        }
    },
    "mappings": {
        "properties": {
            "embedding": {
                "type": "knn_vector",
                "dimension": 384  # Must match model output
            }
        }
    }
}
```

**Prevention**: Ensure index created with correct kNN settings before indexing.

---

### 20. Search performance degrades over time

**Problem**: Queries become slower as more documents are added.

**Cause**: Index fragmentation or insufficient resources.

**Solution**:
```bash
# Force merge index to reduce segments
curl -X POST "localhost:9200/research_assistant/_forcemerge?max_num_segments=1"

# Increase OpenSearch memory
docker run -p 9200:9200 \
  -e "discovery.type=single-node" \
  -e "OPENSEARCH_JAVA_OPTS=-Xms2g -Xmx2g" \
  opensearchproject/opensearch:latest
```

**Prevention**: Regular index maintenance and monitoring.

---

## UI Issues

### 21. Gradio interface is unresponsive

**Problem**: UI freezes or buttons don't respond.

**Cause**: Long-running operations blocking the UI thread.

**Solution**:
```python
# Use async functions for long operations
async def query_system(query_text):
    results = await asyncio.to_thread(
        orchestrator.process_query, query_text
    )
    return results

# Or use Gradio's queue
interface.queue().launch()
```

**Prevention**: Keep UI operations non-blocking.

---

### 22. Share link not working

**Problem**: Public share URL doesn't open or shows errors.

**Cause**: Network restrictions or Gradio service issues.

**Solution**:
```python
# Try without share link first
interface.launch(share=False, server_port=7860)

# Access locally at http://localhost:7860

# If share needed, check firewall settings
# or use alternative like ngrok
```

**Prevention**: Test local access first before using share links.

---

### 23. Citation manager not updating

**Problem**: Citations don't appear in the manager tab.

**Cause**: Citation extraction regex not matching response format.

**Solution**:
```python
# Update citation patterns in citation_tracker.py
citation_patterns = [
    r'\[(\d+)\]',           # [1], [2], etc.
    r'\((\d+)\)',           # (1), (2), etc.
    r'\[([A-Za-z]+\d+)\]',  # [Smith2023], etc.
]

# Test extraction
import re
text = "According to [1], machine learning..."
matches = re.findall(r'\[(\d+)\]', text)
print(matches)  # Should print ['1']
```

**Prevention**: Standardize citation format in prompts.

---

### 24. File upload fails in UI

**Problem**: Cannot upload PDFs or other files through Gradio interface.

**Cause**: File size limits or incorrect file type handling.

**Solution**:
```python
# Increase file size limit
gr.File(
    file_count="single",
    file_types=[".pdf"],
    max_size=50_000_000  # 50MB limit
)

# Handle upload errors gracefully
def handle_upload(file):
    if file is None:
        return "No file uploaded"
    try:
        process_file(file.name)
        return "Success"
    except Exception as e:
        return f"Error: {str(e)}"
```

**Prevention**: Validate file before processing.

---

## Configuration Issues

### 25. Environment variables not loading

**Problem**: Application can't read values from `.env` file.

**Cause**: `.env` file not in correct location or wrong format.

**Solution**:
```bash
# Ensure .env is in project root
ls -la .env

# Check file format (no spaces around =)
# Correct: GEMINI_API_KEY=abc123
# Wrong:   GEMINI_API_KEY = abc123

# Load manually if needed
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('GEMINI_API_KEY'))"
```

**Prevention**: Use `.env.example` as template.

---

### 26. OpenSearch host/port configuration ignored

**Problem**: Application connects to wrong OpenSearch instance.

**Cause**: Hardcoded values overriding configuration.

**Solution**:
```python
# In opensearch_manager.py, ensure env vars are used
import os
from dotenv import load_dotenv

load_dotenv()

host = os.getenv('OPENSEARCH_HOST', 'localhost')
port = int(os.getenv('OPENSEARCH_PORT', 9200))

client = OpenSearch(
    hosts=[{'host': host, 'port': port}],
    http_compress=True,
    use_ssl=False
)
```

**Prevention**: Always use environment variables for configuration.

---

## Performance Issues

### 27. Slow query responses

**Problem**: Queries take 30+ seconds to complete.

**Cause**: Large result sets, complex queries, or unoptimized retrieval.

**Solution**:
```python
# Limit result size
results = opensearch.search(
    index='research_assistant',
    body=query,
    size=10  # Reduce from default 100
)

# Use pagination for large result sets
# Add timeout to prevent hanging
results = opensearch.search(
    body=query,
    request_timeout=30
)
```

**Prevention**: Optimize queries and use appropriate result limits.

---

### 28. High memory usage during indexing

**Problem**: Application consumes excessive memory when indexing.

**Cause**: Loading all documents into memory at once.

**Solution**:
```python
# Process documents in batches
def index_documents_batch(documents, batch_size=50):
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i+batch_size]
        index_batch(batch)
        # Force garbage collection
        import gc
        gc.collect()
```

**Prevention**: Stream processing instead of batch loading.

---

### 29. Gemini API quota exceeded

**Problem**: `QuotaExceeded` or `ResourceExhausted` errors from Gemini.

**Cause**: Exceeding free tier limits (60 requests per minute).

**Solution**:
```python
# Add rate limiting
import time
from functools import wraps

def rate_limit(calls_per_minute=60):
    min_interval = 60.0 / calls_per_minute
    last_called = [0.0]

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            wait = min_interval - elapsed
            if wait > 0:
                time.sleep(wait)
            result = func(*args, **kwargs)
            last_called[0] = time.time()
            return result
        return wrapper
    return decorator

@rate_limit(calls_per_minute=50)
def call_gemini(prompt):
    return model.generate_content(prompt)
```

**Prevention**: Monitor API usage in Google Cloud Console.

---

### 30. Docker container crashes

**Problem**: OpenSearch Docker container stops unexpectedly.

**Cause**: Insufficient memory allocation or disk space.

**Solution**:
```bash
# Increase memory limits
docker run -p 9200:9200 \
  -e "discovery.type=single-node" \
  -e "OPENSEARCH_JAVA_OPTS=-Xms1g -Xmx1g" \
  --memory=2g \
  opensearchproject/opensearch:latest

# Check container logs
docker logs <container_id>

# Clean up disk space
docker system prune -a
```

**Prevention**: Monitor container resource usage with `docker stats`.

---

## Additional Resources

- [OpenSearch Troubleshooting](./opensearch.md)
- [API Error Guide](./api-errors.md)
- [FAQ](./faq.md)
- [Performance Optimization](../advanced/performance.md)

## Getting Help

If you encounter an issue not covered here:

1. Check the [FAQ](./faq.md)
2. Review application logs in `logs/` directory
3. Enable debug logging: `logging.basicConfig(level=logging.DEBUG)`
4. Search existing GitHub issues
5. Create a new issue with:
   - Error message and full stack trace
   - Steps to reproduce
   - System information (OS, Python version, etc.)
   - Relevant configuration (sanitized)
