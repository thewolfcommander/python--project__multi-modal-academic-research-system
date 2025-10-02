# Indexing Module

## Overview

The Indexing module manages OpenSearch integration for hybrid search capabilities. It combines traditional keyword search (BM25) with semantic vector search using embeddings, providing powerful retrieval for multi-modal academic content.

## Module Architecture

```
multi_modal_rag/indexing/
└── opensearch_manager.py    # OpenSearch client and search logic
```

---

## OpenSearchManager

**File**: `multi_modal_rag/indexing/opensearch_manager.py`

### Class Overview

Manages all OpenSearch operations including index creation, document indexing, and hybrid search. Uses `sentence-transformers` for embedding generation and OpenSearch's kNN capabilities for semantic search.

### Initialization

```python
from multi_modal_rag.indexing import OpenSearchManager

manager = OpenSearchManager(
    host='localhost',
    port=9200,
    use_ssl=True,
    username='admin',
    password='MyStrongPassword@2024!'
)
```

**Parameters**:
- `host` (str, optional): OpenSearch host address. Default: `'localhost'`
- `port` (int, optional): OpenSearch port. Default: `9200`
- `use_ssl` (bool, optional): Use SSL/TLS connection. Default: `True`
- `username` (str, optional): Authentication username. Default: `'admin'`
- `password` (str, optional): Authentication password. Default: `'MyStrongPassword@2024!'`

**Connection Testing**:
- Automatically tests connection on initialization
- Sets `self.connected = True` if successful
- Logs error and continues with limited functionality if connection fails

**Embedding Model**:
- Uses `SentenceTransformer('all-MiniLM-L6-v2')`
- Generates 384-dimensional embeddings
- Lightweight and fast (suitable for free-tier deployment)

**Example**:

```python
manager = OpenSearchManager(
    host='localhost',
    port=9200
)

if manager.connected:
    print("✅ Connected to OpenSearch")
else:
    print("⚠️  OpenSearch not available - limited functionality")
```

---

### Methods

#### `create_index(index_name: str) -> bool`

Creates an OpenSearch index with mappings optimized for multi-modal academic content.

**Parameters**:
- `index_name` (str): Name of the index to create

**Returns**: `True` if successful, `False` otherwise

**Index Configuration**:

```python
{
    'settings': {
        'index': {
            'number_of_shards': 2,
            'number_of_replicas': 1,
            'knn': True  # Enable k-NN for vector search
        }
    },
    'mappings': {
        'properties': {
            'content_type': {'type': 'keyword'},
            'title': {
                'type': 'text',
                'fields': {'keyword': {'type': 'keyword'}}
            },
            'abstract': {'type': 'text'},
            'content': {'type': 'text'},
            'authors': {'type': 'keyword'},
            'publication_date': {'type': 'date'},
            'url': {'type': 'keyword'},
            'transcript': {'type': 'text'},
            'diagram_descriptions': {'type': 'text'},
            'key_concepts': {'type': 'keyword'},
            'citations': {
                'type': 'nested',
                'properties': {
                    'text': {'type': 'text'},
                    'source': {'type': 'keyword'}
                }
            },
            'embedding': {
                'type': 'knn_vector',
                'dimension': 384
            },
            'metadata': {
                'type': 'object',
                'enabled': True
            }
        }
    }
}
```

**Example**:

```python
manager = OpenSearchManager()
success = manager.create_index("research_assistant")

if success:
    print("Index created successfully")
else:
    print("Failed to create index")
```

**Behavior**:
- Checks if index already exists before creating
- Skips creation if index exists (doesn't overwrite)
- Returns `False` if not connected to OpenSearch

---

#### `index_document(index_name: str, document: Dict) -> Dict`

Indexes a single document with automatic embedding generation.

**Parameters**:
- `index_name` (str): Target index name
- `document` (Dict): Document to index

**Returns**: OpenSearch response dict, or `None` on error

**Document Structure**:

```python
document = {
    'content_type': str,        # 'paper', 'video', or 'podcast'
    'title': str,
    'abstract': str,            # For papers
    'content': str,             # Main text content
    'authors': List[str],
    'publication_date': str,    # ISO format date
    'url': str,
    'transcript': str,          # For videos/podcasts
    'diagram_descriptions': str,# For papers with diagrams
    'key_concepts': List[str],
    'metadata': Dict            # Additional metadata
}
```

**Automatic Processing**:
1. Combines title + abstract + content (first 1000 chars) into searchable text
2. Generates 384-dim embedding using `SentenceTransformer`
3. Adds embedding to document
4. Indexes document in OpenSearch

**Example**:

```python
manager = OpenSearchManager()

paper_doc = {
    'content_type': 'paper',
    'title': 'Attention Is All You Need',
    'abstract': 'The dominant sequence transduction models...',
    'content': 'We propose a new simple network architecture...',
    'authors': ['Ashish Vaswani', 'Noam Shazeer'],
    'publication_date': '2017-06-12',
    'url': 'https://arxiv.org/abs/1706.03762',
    'key_concepts': ['transformer', 'attention', 'neural networks']
}

response = manager.index_document("research_assistant", paper_doc)

if response:
    print(f"Indexed document with ID: {response['_id']}")
```

**Embedding Generation**:

```python
# Internally performed by index_document()
searchable_text = f"{document.get('title', '')} {document.get('abstract', '')} {document.get('content', '')[:1000]}"
embedding = self.embedding_model.encode(searchable_text).tolist()
document['embedding'] = embedding  # 384-dimensional vector
```

---

#### `bulk_index(index_name: str, documents: List[Dict]) -> int`

Bulk indexes multiple documents efficiently.

**Parameters**:
- `index_name` (str): Target index name
- `documents` (List[Dict]): List of documents to index

**Returns**: Number of successfully indexed documents, or `None` on error

**Example**:

```python
manager = OpenSearchManager()

papers = [
    {
        'content_type': 'paper',
        'title': 'Paper 1',
        'content': 'Content 1...',
        # ... other fields
    },
    {
        'content_type': 'paper',
        'title': 'Paper 2',
        'content': 'Content 2...',
        # ... other fields
    },
    # ... more papers
]

success_count = manager.bulk_index("research_assistant", papers)
print(f"Successfully indexed {success_count} documents")
```

**Performance**:
- Uses OpenSearch bulk API for efficiency
- Processes embeddings for all documents before indexing
- Much faster than individual `index_document()` calls
- Recommended for batches > 10 documents

**Progress Logging**:

```
INFO - Starting bulk indexing of 50 documents to 'research_assistant'
DEBUG - Processing document 1/50 for bulk index: Attention Is All You Need
DEBUG - Processing document 2/50 for bulk index: BERT: Pre-training...
...
DEBUG - Executing bulk index operation...
INFO - ✅ Bulk indexed 50 documents successfully to 'research_assistant'
```

---

#### `hybrid_search(index_name: str, query: str, k: int = 10) -> List[Dict]`

Performs hybrid search combining keyword matching with semantic similarity.

**Parameters**:
- `index_name` (str): Index to search
- `query` (str): Search query
- `k` (int, optional): Number of results to return. Default: 10

**Returns**: List of result dictionaries:

```python
[
    {
        'score': float,      # Relevance score
        'source': Dict       # Source document
    },
    # ... more results
]
```

**Search Algorithm**:

The current implementation uses **text-based multi-match search** with field boosting:

```python
{
    'size': k,
    'query': {
        'multi_match': {
            'query': query,
            'fields': [
                'title^3',           # 3x weight
                'abstract^2',        # 2x weight
                'content',           # 1x weight
                'transcript',        # 1x weight
                'key_concepts^2'     # 2x weight
            ],
            'type': 'best_fields',
            'fuzziness': 'AUTO'
        }
    }
}
```

**Field Boosting Explained**:
- `title^3`: Title matches weighted 3x (most important)
- `abstract^2`: Abstract matches weighted 2x
- `key_concepts^2`: Concept matches weighted 2x
- `content`, `transcript`: Standard 1x weight

**Fuzziness**: `AUTO` handles typos (1-2 character edits allowed)

**Example**:

```python
manager = OpenSearchManager()
results = manager.hybrid_search(
    index_name="research_assistant",
    query="transformer architecture",
    k=5
)

for result in results:
    print(f"Score: {result['score']:.2f}")
    print(f"Title: {result['source']['title']}")
    print(f"Type: {result['source']['content_type']}")
    print("---")
```

**Output**:

```
Score: 15.42
Title: Attention Is All You Need
Type: paper
---
Score: 12.18
Title: BERT: Pre-training of Deep Bidirectional Transformers
Type: paper
---
Score: 8.94
Title: Illustrated Transformer
Type: video
---
```

**Vector Search (Disabled)**:

Previous versions used kNN vector search, but it's currently disabled for OpenSearch 3.x compatibility:

```python
# Original hybrid search (commented out)
{
    'query': {
        'bool': {
            'should': [
                # Keyword search
                {'multi_match': {...}},
                # Semantic search
                {
                    'knn': {
                        'embedding': {
                            'vector': query_embedding,
                            'k': k
                        }
                    }
                }
            ]
        }
    }
}
```

To re-enable vector search, modify the query structure and generate query embeddings.

---

## Index Schema Deep Dive

### Field Types and Purposes

#### Content Type (`content_type`)

```python
'content_type': {'type': 'keyword'}
```

- **Purpose**: Identify document type (paper, video, podcast)
- **Type**: `keyword` (exact match, not analyzed)
- **Usage**: Filtering by content type in queries

**Example Query**:

```python
{
    'query': {
        'bool': {
            'must': [{'match': {'content': 'neural networks'}}],
            'filter': [{'term': {'content_type': 'paper'}}]
        }
    }
}
```

#### Title (`title`)

```python
'title': {
    'type': 'text',
    'fields': {
        'keyword': {'type': 'keyword'}
    }
}
```

- **`text` field**: Full-text search, analyzed (tokenized, lowercased)
- **`keyword` subfield**: Exact match, sorting, aggregations
- **Usage**: Primary search field with 3x boost

**Example**:

```python
# Text search (matches "attention mechanism")
{'match': {'title': 'attention'}}

# Exact match (must match entire title)
{'term': {'title.keyword': 'Attention Is All You Need'}}

# Sorting
{'sort': [{'title.keyword': 'asc'}]}
```

#### Authors (`authors`)

```python
'authors': {'type': 'keyword'}
```

- **Type**: `keyword` array (exact match)
- **Purpose**: Filter by specific authors, aggregations
- **Usage**: Author filtering, co-author analysis

**Example**:

```python
# Find all papers by author
{'term': {'authors': 'Geoffrey Hinton'}}

# Aggregation: top authors
{
    'aggs': {
        'top_authors': {
            'terms': {'field': 'authors', 'size': 10}
        }
    }
}
```

#### Embeddings (`embedding`)

```python
'embedding': {
    'type': 'knn_vector',
    'dimension': 384
}
```

- **Type**: k-NN vector for semantic search
- **Dimension**: 384 (from `all-MiniLM-L6-v2`)
- **Purpose**: Semantic similarity matching
- **Usage**: Vector search for conceptual matching

**Example** (when enabled):

```python
query_embedding = embedding_model.encode("neural networks").tolist()

{
    'query': {
        'knn': {
            'embedding': {
                'vector': query_embedding,
                'k': 10
            }
        }
    }
}
```

#### Citations (`citations`)

```python
'citations': {
    'type': 'nested',
    'properties': {
        'text': {'type': 'text'},
        'source': {'type': 'keyword'}
    }
}
```

- **Type**: `nested` (allows querying within citation objects)
- **Purpose**: Store and search extracted citations
- **Usage**: Citation analysis, reference tracking

**Example**:

```python
# Find documents citing specific source
{
    'query': {
        'nested': {
            'path': 'citations',
            'query': {
                'term': {'citations.source': 'Vaswani et al., 2017'}
            }
        }
    }
}
```

---

## Embedding Generation

### Sentence Transformer Model

**Model**: `all-MiniLM-L6-v2`

**Characteristics**:
- **Size**: 80MB (lightweight)
- **Dimension**: 384
- **Speed**: ~1000 sentences/second (CPU)
- **Quality**: Good for general semantic similarity

**Why This Model?**:
1. **Free**: No API costs
2. **Fast**: Suitable for real-time indexing
3. **Accurate**: 0.68 Spearman correlation on STS benchmark
4. **Lightweight**: Runs on CPU without GPU

### Embedding Process

```python
# 1. Prepare searchable text
searchable_text = f"{title} {abstract} {content[:1000]}"

# 2. Generate embedding
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
embedding = model.encode(searchable_text)  # numpy array (384,)

# 3. Convert to list for JSON serialization
embedding_list = embedding.tolist()  # List[float] (384 elements)

# 4. Store in document
document['embedding'] = embedding_list
```

### Semantic Search Benefits

**Query**: "deep learning models for language understanding"

**Traditional Keyword Search** would miss:
- "neural architectures for NLP"
- "transformer networks for text comprehension"

**Semantic Search** (using embeddings) finds:
- Documents about BERT, GPT (even without exact keywords)
- Papers on attention mechanisms (related concept)
- Content about language models (semantic similarity)

---

## Hybrid Search Strategy

### Why Hybrid?

Combines strengths of both approaches:

| Search Type | Strengths | Weaknesses |
|-------------|-----------|------------|
| **Keyword** (BM25) | - Exact matches<br>- Fast<br>- Handles rare terms well | - Misses synonyms<br>- No semantic understanding |
| **Vector** (kNN) | - Semantic similarity<br>- Finds related concepts<br>- Handles paraphrasing | - May miss exact terms<br>- Slower<br>- Requires embeddings |
| **Hybrid** | - Best of both worlds<br>- Balanced precision/recall | - More complex<br>- Requires tuning |

### Current Implementation (Text-Only)

The system currently uses **multi-match** with field boosting:

**Advantages**:
- Simple and fast
- No vector computation at query time
- Works well for exact and fuzzy matches

**Limitations**:
- No semantic similarity
- Relies on keyword overlap
- May miss conceptually similar content

### Ideal Hybrid Implementation

To re-enable full hybrid search:

```python
def hybrid_search(self, index_name: str, query: str, k: int = 10):
    # 1. Generate query embedding
    query_embedding = self.embedding_model.encode(query).tolist()

    # 2. Construct hybrid query
    search_query = {
        'size': k,
        'query': {
            'bool': {
                'should': [
                    # Keyword search (BM25)
                    {
                        'multi_match': {
                            'query': query,
                            'fields': ['title^3', 'abstract^2', 'content'],
                            'type': 'best_fields'
                        }
                    },
                    # Vector search (kNN)
                    {
                        'script_score': {
                            'query': {'match_all': {}},
                            'script': {
                                'source': "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                                'params': {'query_vector': query_embedding}
                            }
                        }
                    }
                ]
            }
        }
    }

    return self.client.search(index=index_name, body=search_query)
```

**Score Combination**:
- BM25 score: 0-10 (keyword relevance)
- Cosine similarity: 0-2 (semantic similarity, +1 offset)
- Combined: Sum of both (higher = more relevant)

---

## Search Query Examples

### Basic Text Search

```python
manager = OpenSearchManager()
results = manager.hybrid_search("research_assistant", "machine learning")
```

### Filter by Content Type

```python
# Direct OpenSearch query (bypass hybrid_search)
query = {
    'query': {
        'bool': {
            'must': [
                {'match': {'content': 'neural networks'}}
            ],
            'filter': [
                {'term': {'content_type': 'video'}}
            ]
        }
    }
}

response = manager.client.search(index="research_assistant", body=query)
```

### Date Range Search

```python
query = {
    'query': {
        'bool': {
            'must': [
                {'match': {'title': 'transformers'}}
            ],
            'filter': [
                {
                    'range': {
                        'publication_date': {
                            'gte': '2020-01-01',
                            'lte': '2024-12-31'
                        }
                    }
                }
            ]
        }
    }
}
```

### Author Filter

```python
query = {
    'query': {
        'bool': {
            'must': [
                {'match': {'content': 'attention mechanism'}}
            ],
            'filter': [
                {'term': {'authors': 'Yoshua Bengio'}}
            ]
        }
    }
}
```

### Aggregations (Analytics)

```python
query = {
    'size': 0,  # Don't return documents
    'aggs': {
        'papers_per_year': {
            'date_histogram': {
                'field': 'publication_date',
                'calendar_interval': 'year'
            }
        },
        'top_concepts': {
            'terms': {
                'field': 'key_concepts',
                'size': 20
            }
        }
    }
}

response = manager.client.search(index="research_assistant", body=query)
print(response['aggregations'])
```

---

## Performance Tuning

### Indexing Performance

**Single Document**:
- Embedding generation: ~10-50ms
- Index operation: ~50-100ms
- **Total**: ~60-150ms per document

**Bulk Indexing** (100 documents):
- Embedding generation: ~1-5 seconds
- Bulk index operation: ~500ms-1s
- **Total**: ~1.5-6 seconds (10-60ms per doc)

**Optimization Tips**:

1. **Use Bulk Indexing**:
   ```python
   # Bad: 100 individual calls
   for doc in documents:
       manager.index_document(index, doc)

   # Good: 1 bulk call
   manager.bulk_index(index, documents)
   ```

2. **Batch Embedding Generation**:
   ```python
   # Encode all texts at once (faster)
   texts = [f"{d['title']} {d['content']}" for d in documents]
   embeddings = model.encode(texts)  # Batch processing

   for doc, emb in zip(documents, embeddings):
       doc['embedding'] = emb.tolist()
   ```

3. **Increase Shard Count** (for large indices):
   ```python
   'settings': {
       'number_of_shards': 5,  # More shards = more parallelism
       'number_of_replicas': 1
   }
   ```

### Search Performance

**Text Search**:
- Query time: ~10-50ms (10K documents)
- Query time: ~50-200ms (1M documents)

**Vector Search** (when enabled):
- Query time: ~50-100ms (10K documents)
- Query time: ~200-500ms (1M documents)

**Optimization Tips**:

1. **Limit Result Size**:
   ```python
   results = manager.hybrid_search(index, query, k=10)  # Not k=1000
   ```

2. **Use Filters** (before scoring):
   ```python
   # Filters don't contribute to score (faster)
   {'filter': [{'term': {'content_type': 'paper'}}]}
   ```

3. **Field Selection** (return only needed fields):
   ```python
   {
       'query': {...},
       '_source': ['title', 'authors', 'url']  # Don't return large 'content' field
   }
   ```

4. **Enable Caching**:
   ```python
   {
       'query': {
           'bool': {
               'filter': [
                   {'term': {'content_type': 'paper'}}  # Cached
               ]
           }
       }
   }
   ```

---

## Error Handling

### Connection Errors

```python
manager = OpenSearchManager(host='localhost', port=9200)

if not manager.connected:
    print("OpenSearch unavailable - using fallback search")
    # Implement fallback logic (e.g., SQLite FTS)
```

### Index Creation Errors

```python
success = manager.create_index("research_assistant")

if not success:
    # Check if index exists
    if manager.client.indices.exists(index="research_assistant"):
        print("Index already exists - using existing index")
    else:
        print("Failed to create index - check permissions")
```

### Indexing Errors

```python
response = manager.index_document(index, document)

if response is None:
    # Log error and continue
    logger.error(f"Failed to index: {document.get('title')}")
else:
    logger.info(f"Indexed: {response['_id']}")
```

### Search Errors

```python
try:
    results = manager.hybrid_search(index, query)
except Exception as e:
    logger.error(f"Search failed: {e}")
    results = []  # Return empty results
```

---

## Dependencies

```python
from opensearchpy import OpenSearch, helpers
from sentence_transformers import SentenceTransformer
```

**Installation**:
```bash
pip install opensearch-py sentence-transformers
```

**OpenSearch Server**:
```bash
# Docker (recommended for development)
docker run -p 9200:9200 -e "discovery.type=single-node" opensearchproject/opensearch:latest

# Verify connection
curl -X GET "https://localhost:9200" -u admin:admin -k
```

---

## Troubleshooting

### Issue: Connection refused

**Error**: `ConnectionError: Connection refused`

**Solution**:
1. Check OpenSearch is running: `docker ps`
2. Verify port: `curl http://localhost:9200`
3. Check firewall settings

### Issue: SSL certificate verification failed

**Error**: `SSLError: certificate verify failed`

**Solution**: Set `verify_certs=False` in initialization:
```python
manager = OpenSearchManager(
    use_ssl=True,
    verify_certs=False  # For self-signed certs
)
```

### Issue: Embedding model download fails

**Error**: `OSError: Can't load model`

**Solution**: Pre-download model:
```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
# Downloads to ~/.cache/torch/sentence_transformers/
```

### Issue: Index creation fails with "resource_already_exists_exception"

**Cause**: Index already exists

**Solution**: Delete and recreate, or use existing index:
```python
# Delete existing index
manager.client.indices.delete(index="research_assistant")

# Recreate
manager.create_index("research_assistant")
```

### Issue: Search returns no results for valid query

**Possible Causes**:
1. **Index is empty**: Check document count
   ```python
   count = manager.client.count(index="research_assistant")
   print(f"Documents: {count['count']}")
   ```

2. **Field mismatch**: Verify field names in index
   ```python
   mapping = manager.client.indices.get_mapping(index="research_assistant")
   print(mapping)
   ```

3. **Query syntax error**: Test with simple match query
   ```python
   {'query': {'match_all': {}}}  # Should return all docs
   ```

---

## Advanced Usage

### Custom Analyzers

Add custom text analysis during index creation:

```python
index_body = {
    'settings': {
        'analysis': {
            'analyzer': {
                'scientific_analyzer': {
                    'type': 'custom',
                    'tokenizer': 'standard',
                    'filter': ['lowercase', 'asciifolding', 'porter_stem']
                }
            }
        }
    },
    'mappings': {
        'properties': {
            'content': {
                'type': 'text',
                'analyzer': 'scientific_analyzer'
            }
        }
    }
}
```

### Multi-Index Search

Search across multiple indices:

```python
results = manager.client.search(
    index=['research_assistant', 'archived_papers'],
    body={'query': {'match': {'title': 'transformers'}}}
)
```

### Percolate Queries (Reverse Search)

Store queries and match documents to them:

```python
# Index a query
manager.client.index(
    index='research_queries',
    body={
        'query': {'match': {'content': 'neural networks'}}
    }
)

# Percolate document against stored queries
response = manager.client.search(
    index='research_queries',
    body={
        'query': {
            'percolate': {
                'field': 'query',
                'document': {
                    'content': 'This paper discusses neural network architectures...'
                }
            }
        }
    }
)
```

---

## Future Enhancements

### Planned Features

1. **Re-enable Vector Search**: Full kNN + BM25 hybrid
2. **Query Expansion**: Use LLM to expand queries before search
3. **Re-ranking**: Use Gemini to re-rank top results
4. **Federated Search**: Search external APIs alongside OpenSearch
5. **Caching Layer**: Redis cache for frequent queries

### Extension Points

```python
# Add query expansion
def expand_query(self, query: str) -> str:
    """Use LLM to add synonyms and related terms"""
    pass

# Add re-ranking
def rerank_results(self, query: str, results: List[Dict]) -> List[Dict]:
    """Use Gemini to re-rank results by relevance"""
    pass

# Add caching
def cached_search(self, query: str, k: int = 10) -> List[Dict]:
    """Cache frequent query results"""
    pass
```
