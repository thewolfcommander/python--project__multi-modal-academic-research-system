# Performance Optimization Guide

Comprehensive guide to optimizing performance of the Multi-Modal Academic Research System.

## Table of Contents

- [Performance Overview](#performance-overview)
- [Profiling and Measurement](#profiling-and-measurement)
- [Indexing Optimization](#indexing-optimization)
- [Search Optimization](#search-optimization)
- [LLM Optimization](#llm-optimization)
- [Database Optimization](#database-optimization)
- [Application-Level Optimization](#application-level-optimization)
- [Infrastructure Optimization](#infrastructure-optimization)

---

## Performance Overview

### Current Performance Characteristics

**Typical Latencies**:
- Initial query (cold start): 5-10 seconds
- Subsequent queries: 2-4 seconds
- Document indexing: 10-30 seconds per document
- PDF processing: 5-20 seconds per PDF
- Embedding generation: 0.5-2 seconds per document

**Bottlenecks**:
1. **Gemini API calls**: Rate-limited, network latency
2. **Embedding generation**: CPU-bound operation
3. **PDF processing**: I/O and computation intensive
4. **OpenSearch queries**: Network and index size dependent

### Performance Goals

| Operation | Current | Target | Priority |
|-----------|---------|--------|----------|
| Query response | 3-5s | <2s | High |
| Indexing throughput | 3-6 docs/min | 20+ docs/min | Medium |
| Search latency | 200-500ms | <100ms | High |
| Memory usage | 4-6GB | <4GB | Medium |
| Cold start | 5-10s | <3s | Low |

---

## Profiling and Measurement

### Basic Profiling

```python
import time
from functools import wraps

def timeit(func):
    """Decorator to measure function execution time."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        print(f"{func.__name__} took {elapsed:.2f}s")
        return result
    return wrapper

# Usage
@timeit
def process_document(doc):
    # ... processing logic
    return processed_doc
```

### Detailed Profiling

```python
import cProfile
import pstats
from io import StringIO

def profile_function(func, *args, **kwargs):
    """Profile a function call."""
    profiler = cProfile.Profile()
    profiler.enable()

    result = func(*args, **kwargs)

    profiler.disable()

    # Print stats
    stream = StringIO()
    stats = pstats.Stats(profiler, stream=stream)
    stats.sort_stats('cumulative')
    stats.print_stats(20)  # Top 20 functions

    print(stream.getvalue())

    return result

# Usage
result = profile_function(process_query, "machine learning")
```

### Memory Profiling

```python
from memory_profiler import profile

@profile
def memory_intensive_function():
    """Function to profile memory usage."""
    large_list = [i for i in range(10000000)]
    # ... more operations
    return result

# Run with: python -m memory_profiler script.py
```

### Performance Monitoring

```python
import psutil
import time

class PerformanceMonitor:
    """Monitor system performance metrics."""

    def __init__(self):
        self.metrics = []

    def record_metrics(self):
        """Record current system metrics."""
        process = psutil.Process()

        metrics = {
            'timestamp': time.time(),
            'cpu_percent': process.cpu_percent(),
            'memory_mb': process.memory_info().rss / 1024 / 1024,
            'threads': process.num_threads(),
            'open_files': len(process.open_files())
        }

        self.metrics.append(metrics)
        return metrics

    def get_summary(self):
        """Get performance summary."""
        if not self.metrics:
            return {}

        return {
            'avg_cpu': sum(m['cpu_percent'] for m in self.metrics) / len(self.metrics),
            'max_memory_mb': max(m['memory_mb'] for m in self.metrics),
            'avg_memory_mb': sum(m['memory_mb'] for m in self.metrics) / len(self.metrics)
        }

# Usage
monitor = PerformanceMonitor()

# During operation
for query in queries:
    monitor.record_metrics()
    process_query(query)

print(monitor.get_summary())
```

---

## Indexing Optimization

### 1. Batch Processing

**Problem**: Processing documents one-by-one is slow.

**Solution**: Batch processing.

```python
def index_documents_batch(documents, batch_size=100):
    """Index documents in batches."""

    for i in range(0, len(documents), batch_size):
        batch = documents[i:i+batch_size]

        # Generate embeddings for batch
        texts = [doc['content'] for doc in batch]
        embeddings = model.encode(
            texts,
            batch_size=32,
            show_progress_bar=True
        )

        # Add embeddings to documents
        for doc, embedding in zip(batch, embeddings):
            doc['embedding'] = embedding.tolist()

        # Bulk index
        from opensearchpy import helpers

        actions = [
            {
                '_index': 'research_assistant',
                '_id': doc['id'],
                '_source': doc
            }
            for doc in batch
        ]

        helpers.bulk(client, actions)

        print(f"Indexed batch {i//batch_size + 1}")

# Result: 5-10x faster than one-by-one
```

### 2. Parallel Processing

```python
from multiprocessing import Pool, cpu_count

def process_document_wrapper(doc_path):
    """Wrapper for multiprocessing."""
    try:
        return process_document(doc_path)
    except Exception as e:
        return {'error': str(e), 'path': doc_path}

def process_documents_parallel(doc_paths, num_workers=None):
    """Process documents in parallel."""

    if num_workers is None:
        num_workers = cpu_count() - 1

    with Pool(processes=num_workers) as pool:
        results = pool.map(process_document_wrapper, doc_paths)

    # Filter out errors
    successful = [r for r in results if 'error' not in r]
    errors = [r for r in results if 'error' in r]

    print(f"Processed: {len(successful)}, Errors: {len(errors)}")

    return successful, errors

# Result: Near-linear speedup with CPU cores
```

### 3. Async Processing

```python
import asyncio
import aiohttp

async def process_document_async(doc_path):
    """Process document asynchronously."""
    # I/O operations don't block
    async with aiofiles.open(doc_path, 'rb') as f:
        content = await f.read()

    # Process content
    processed = await process_content_async(content)

    return processed

async def process_batch_async(doc_paths):
    """Process multiple documents concurrently."""
    tasks = [process_document_async(path) for path in doc_paths]
    results = await asyncio.gather(*tasks)
    return results

# Usage
results = asyncio.run(process_batch_async(doc_paths))

# Result: Great for I/O-bound operations
```

### 4. Disable Refresh During Bulk Indexing

```python
def bulk_index_optimized(documents):
    """Optimize bulk indexing performance."""

    # Disable refresh during indexing
    client.indices.put_settings(
        index='research_assistant',
        body={'index': {'refresh_interval': '-1'}}
    )

    try:
        # Bulk index
        helpers.bulk(client, prepare_actions(documents))

    finally:
        # Re-enable refresh
        client.indices.put_settings(
            index='research_assistant',
            body={'index': {'refresh_interval': '1s'}}
        )

        # Force refresh
        client.indices.refresh(index='research_assistant')

# Result: 2-3x faster indexing
```

---

## Search Optimization

### 1. Result Caching

```python
from functools import lru_cache
import hashlib

class SearchCache:
    """Cache search results."""

    def __init__(self, max_size=1000, ttl=3600):
        self.cache = {}
        self.max_size = max_size
        self.ttl = ttl  # Time to live in seconds

    def get_key(self, query, params):
        """Generate cache key."""
        key_string = f"{query}:{str(sorted(params.items()))}"
        return hashlib.md5(key_string.encode()).hexdigest()

    def get(self, query, params):
        """Get cached results."""
        key = self.get_key(query, params)

        if key in self.cache:
            entry = self.cache[key]

            # Check if expired
            if time.time() - entry['timestamp'] < self.ttl:
                return entry['results']
            else:
                del self.cache[key]

        return None

    def set(self, query, params, results):
        """Cache results."""
        key = self.get_key(query, params)

        # Evict oldest if at capacity
        if len(self.cache) >= self.max_size:
            oldest = min(self.cache.items(), key=lambda x: x[1]['timestamp'])
            del self.cache[oldest[0]]

        self.cache[key] = {
            'results': results,
            'timestamp': time.time()
        }

# Usage
cache = SearchCache()

def search_with_cache(query, **params):
    """Search with caching."""
    cached = cache.get(query, params)
    if cached:
        return cached

    results = perform_search(query, **params)
    cache.set(query, params, results)

    return results

# Result: Sub-millisecond response for cached queries
```

### 2. Query Optimization

```python
def optimized_query(query_text, size=10):
    """Optimized query structure."""

    query = {
        'size': size,
        'query': {
            'bool': {
                # Use filter for exact matches (cached)
                'filter': [
                    {'term': {'content_type': 'paper'}}
                ],
                # Use must for scoring
                'must': [
                    {
                        'multi_match': {
                            'query': query_text,
                            'fields': ['title^3', 'abstract^2', 'content'],
                            'type': 'best_fields',
                            'operator': 'or'
                        }
                    }
                ],
                # Use should for boosting (optional)
                'should': [
                    {'match': {'key_concepts': query_text}}
                ],
                'minimum_should_match': 0
            }
        },
        # Only return needed fields
        '_source': ['title', 'abstract', 'authors', 'publication_date'],
        # Disable expensive features if not needed
        'track_scores': False
    }

    return query
```

### 3. Pagination Instead of Large Results

```python
def search_with_pagination(query, page=1, page_size=10):
    """Paginated search."""

    query_body = {
        'query': {...},
        'from': (page - 1) * page_size,
        'size': page_size
    }

    return client.search(index='research_assistant', body=query_body)

# Better than retrieving 1000 results at once
```

### 4. Search After (Efficient Deep Pagination)

```python
def deep_pagination(query, search_after=None, size=10):
    """Efficient deep pagination using search_after."""

    query_body = {
        'query': {...},
        'size': size,
        'sort': [
            {'_score': 'desc'},
            {'_id': 'asc'}  # Tiebreaker
        ]
    }

    if search_after:
        query_body['search_after'] = search_after

    response = client.search(index='research_assistant', body=query_body)

    # Get last hit's sort values for next page
    hits = response['hits']['hits']
    if hits:
        last_sort = hits[-1]['sort']
        return hits, last_sort
    else:
        return hits, None

# Usage
results, next_page = deep_pagination(query)
# Next page
results, next_page = deep_pagination(query, search_after=next_page)

# Much faster than using 'from' for deep pagination
```

---

## LLM Optimization

### 1. Prompt Optimization

**Problem**: Long prompts increase latency and cost.

**Solution**: Optimize prompt length.

```python
def optimize_context(documents, max_length=3000):
    """Select most relevant context."""

    # Sort by relevance score
    documents.sort(key=lambda x: x['score'], reverse=True)

    # Build context up to max length
    context_parts = []
    current_length = 0

    for doc in documents:
        # Use abstract instead of full content for length
        text = doc['abstract'] if len(doc['content']) > 500 else doc['content']

        if current_length + len(text) > max_length:
            break

        context_parts.append(text)
        current_length += len(text)

    return '\n\n'.join(context_parts)

# Result: 2-3x faster responses, lower costs
```

### 2. Response Streaming

```python
def stream_llm_response(prompt):
    """Stream LLM response for better UX."""

    response = model.generate_content(
        prompt,
        stream=True
    )

    full_response = ""
    for chunk in response:
        if chunk.text:
            full_response += chunk.text
            yield chunk.text  # Yield immediately

    return full_response

# In Gradio
def chat(message, history):
    """Chat with streaming."""
    prompt = format_prompt(message, history)

    partial = ""
    for chunk in stream_llm_response(prompt):
        partial += chunk
        yield partial

# Result: Perceived latency reduced by 50%+
```

### 3. Local LLM for Simple Tasks

```python
# Use Gemini for complex tasks
def complex_task(query, context):
    """Use Gemini for complex reasoning."""
    return gemini_model.generate_content(f"{query}\n\n{context}")

# Use local model for simple tasks
from transformers import pipeline

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def simple_summarization(text):
    """Use local model for simple summarization."""
    if len(text) > 1024:
        text = text[:1024]

    summary = summarizer(text, max_length=150, min_length=50)
    return summary[0]['summary_text']

# Result: No API latency or rate limits for simple tasks
```

---

## Database Optimization

### 1. Index Settings

```python
optimized_settings = {
    'settings': {
        'number_of_shards': 1,  # Single node = 1 shard
        'number_of_replicas': 0,  # No replicas for local dev
        'refresh_interval': '30s',  # Reduce refresh frequency
        'index': {
            'max_result_window': 10000,
            'knn': True,
            'knn.algo_param.ef_search': 100  # Balance speed vs quality
        }
    },
    'mappings': {
        'properties': {
            'embedding': {
                'type': 'knn_vector',
                'dimension': 384,
                'method': {
                    'name': 'hnsw',
                    'space_type': 'cosinesimil',
                    'engine': 'nmslib',
                    'parameters': {
                        'ef_construction': 128,
                        'm': 16
                    }
                }
            }
        }
    }
}
```

### 2. Connection Pooling

```python
from opensearchpy import OpenSearch

# Optimize connection settings
client = OpenSearch(
    hosts=[{'host': 'localhost', 'port': 9200}],
    http_compress=True,  # Compress requests/responses
    use_ssl=False,
    verify_certs=False,
    max_retries=3,
    retry_on_timeout=True,
    timeout=30,
    # Connection pooling
    maxsize=25,  # Connection pool size
    http_auth=None
)
```

### 3. Bulk Operations

```python
from opensearchpy import helpers

def efficient_bulk_index(documents):
    """Efficient bulk indexing."""

    # Prepare actions
    actions = [
        {
            '_index': 'research_assistant',
            '_id': doc['id'],
            '_source': doc
        }
        for doc in documents
    ]

    # Bulk with optimized settings
    success, failed = helpers.bulk(
        client,
        actions,
        chunk_size=500,  # Process in chunks
        request_timeout=60,
        max_retries=3,
        raise_on_error=False
    )

    return success, failed
```

---

## Application-Level Optimization

### 1. Lazy Loading

```python
class LazyModel:
    """Lazy-load models only when needed."""

    def __init__(self):
        self._model = None

    @property
    def model(self):
        if self._model is None:
            print("Loading model...")
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer('all-MiniLM-L6-v2')
        return self._model

# Usage
lazy_model = LazyModel()
# Model not loaded yet

embedding = lazy_model.model.encode("text")
# Now model is loaded
```

### 2. Pre-computation

```python
def precompute_embeddings():
    """Precompute embeddings for common queries."""

    common_queries = [
        "machine learning",
        "deep learning",
        "neural networks",
        # ... more queries
    ]

    embeddings = {}
    for query in common_queries:
        embeddings[query] = model.encode(query).tolist()

    # Save to file
    import pickle
    with open('query_embeddings.pkl', 'wb') as f:
        pickle.dump(embeddings, f)

# Load at startup
with open('query_embeddings.pkl', 'rb') as f:
    precomputed_embeddings = pickle.load(f)

# Use in search
def search_optimized(query):
    """Search with precomputed embeddings."""
    if query in precomputed_embeddings:
        query_embedding = precomputed_embeddings[query]
    else:
        query_embedding = model.encode(query).tolist()

    # ... rest of search
```

### 3. Background Processing

```python
import threading
import queue

class BackgroundProcessor:
    """Process tasks in background."""

    def __init__(self):
        self.queue = queue.Queue()
        self.thread = threading.Thread(target=self._process_queue, daemon=True)
        self.thread.start()

    def _process_queue(self):
        """Process tasks from queue."""
        while True:
            task = self.queue.get()
            if task is None:
                break

            func, args, kwargs = task
            try:
                func(*args, **kwargs)
            except Exception as e:
                print(f"Background task error: {e}")

            self.queue.task_done()

    def submit(self, func, *args, **kwargs):
        """Submit task for background processing."""
        self.queue.put((func, args, kwargs))

# Usage
processor = BackgroundProcessor()

# Index documents in background
processor.submit(index_documents, documents)

# Continue with other tasks immediately
```

---

## Infrastructure Optimization

### 1. OpenSearch Configuration

**Docker settings**:
```bash
docker run -d \
  --name opensearch \
  -p 9200:9200 -p 9600:9600 \
  -e "discovery.type=single-node" \
  -e "OPENSEARCH_JAVA_OPTS=-Xms4g -Xmx4g" \
  -e "bootstrap.memory_lock=true" \
  -e "cluster.routing.allocation.disk.threshold_enabled=false" \
  --ulimit memlock=-1:-1 \
  --memory=6g \
  opensearchproject/opensearch:latest
```

**JVM settings** (opensearch.yml):
```yaml
# Heap size (50% of available RAM)
-Xms4g
-Xmx4g

# GC settings
-XX:+UseG1GC
-XX:InitiatingHeapOccupancyPercent=45
```

### 2. GPU Acceleration

```python
import torch
from sentence_transformers import SentenceTransformer

# Check GPU
device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"Using device: {device}")

# Load model on GPU
model = SentenceTransformer('all-MiniLM-L6-v2', device=device)

# Encode with GPU
embeddings = model.encode(
    texts,
    batch_size=128,  # Larger batch for GPU
    convert_to_tensor=True,
    show_progress_bar=True
)

# Result: 10-100x faster on GPU
```

### 3. Caching Layer (Redis)

```python
import redis
import json

# Connect to Redis
redis_client = redis.Redis(host='localhost', port=6379, db=0)

def search_with_redis_cache(query, ttl=3600):
    """Search with Redis caching."""

    # Check cache
    cache_key = f"search:{query}"
    cached = redis_client.get(cache_key)

    if cached:
        return json.loads(cached)

    # Perform search
    results = perform_search(query)

    # Cache results
    redis_client.setex(
        cache_key,
        ttl,
        json.dumps(results)
    )

    return results
```

---

## Performance Checklist

### Before Optimization

- [ ] Profile to identify bottlenecks
- [ ] Measure baseline performance
- [ ] Set specific performance goals

### Indexing

- [ ] Use batch processing
- [ ] Enable parallel processing
- [ ] Disable refresh during bulk indexing
- [ ] Optimize batch sizes
- [ ] Use GPU for embeddings

### Search

- [ ] Implement result caching
- [ ] Optimize query structure
- [ ] Use pagination
- [ ] Limit result size
- [ ] Pre-compute common embeddings

### LLM

- [ ] Optimize prompt length
- [ ] Implement streaming
- [ ] Cache responses
- [ ] Use appropriate temperature
- [ ] Handle rate limits

### Database

- [ ] Optimize index settings
- [ ] Configure connection pooling
- [ ] Use bulk operations
- [ ] Monitor cluster health
- [ ] Regular maintenance

### Infrastructure

- [ ] Sufficient memory allocation
- [ ] GPU if available
- [ ] Caching layer (Redis)
- [ ] Monitor resource usage

---

## Benchmarking

### Create Benchmark Suite

```python
import time
import statistics

class Benchmark:
    """Benchmark suite for performance testing."""

    def __init__(self):
        self.results = {}

    def run_benchmark(self, name, func, iterations=10):
        """Run benchmark."""
        times = []

        # Warmup
        func()

        # Benchmark
        for _ in range(iterations):
            start = time.time()
            func()
            elapsed = time.time() - start
            times.append(elapsed)

        self.results[name] = {
            'mean': statistics.mean(times),
            'median': statistics.median(times),
            'stdev': statistics.stdev(times) if len(times) > 1 else 0,
            'min': min(times),
            'max': max(times)
        }

    def print_results(self):
        """Print benchmark results."""
        print("\nBenchmark Results:")
        print("-" * 60)

        for name, stats in self.results.items():
            print(f"\n{name}:")
            print(f"  Mean:   {stats['mean']:.3f}s")
            print(f"  Median: {stats['median']:.3f}s")
            print(f"  Stdev:  {stats['stdev']:.3f}s")
            print(f"  Min:    {stats['min']:.3f}s")
            print(f"  Max:    {stats['max']:.3f}s")

# Usage
bench = Benchmark()

bench.run_benchmark(
    "Keyword Search",
    lambda: keyword_search("machine learning"),
    iterations=20
)

bench.run_benchmark(
    "Semantic Search",
    lambda: semantic_search("machine learning"),
    iterations=20
)

bench.run_benchmark(
    "Hybrid Search",
    lambda: hybrid_search("machine learning"),
    iterations=20
)

bench.print_results()
```

---

## Additional Resources

- [OpenSearch Performance Tuning](https://opensearch.org/docs/latest/tuning-your-cluster/)
- [Sentence Transformers Performance](https://www.sbert.net/docs/training/performance.html)
- [Python Profiling](https://docs.python.org/3/library/profile.html)
- [Gemini API Best Practices](https://ai.google.dev/docs/best_practices)

## Summary

**Quick Wins** (implement first):
1. Enable result caching
2. Use batch processing
3. Optimize OpenSearch settings
4. Implement streaming responses
5. Add GPU support for embeddings

**Major Improvements** (larger effort):
1. Parallel processing pipeline
2. Redis caching layer
3. Query optimization
4. Pre-computation strategies
5. Infrastructure upgrades

**Remember**: Measure before and after optimizations to verify improvements!
