# Embedding Models Deep Dive

Comprehensive guide to understanding and working with embedding models in the Multi-Modal Academic Research System.

## Table of Contents

- [What Are Embeddings?](#what-are-embeddings)
- [Current Implementation](#current-implementation)
- [Choosing an Embedding Model](#choosing-an-embedding-model)
- [Model Comparison](#model-comparison)
- [Changing Embedding Models](#changing-embedding-models)
- [Fine-Tuning Embeddings](#fine-tuning-embeddings)
- [Optimization Techniques](#optimization-techniques)
- [Advanced Topics](#advanced-topics)

---

## What Are Embeddings?

### Definition

Embeddings are dense vector representations of text that capture semantic meaning. Similar concepts have similar vectors (measured by cosine similarity or other distance metrics).

**Example**:
```
"machine learning" → [0.23, -0.45, 0.67, ..., 0.12]  (384 dimensions)
"neural networks"  → [0.21, -0.42, 0.69, ..., 0.15]  (similar vector)
"pizza recipe"     → [-0.67, 0.34, -0.12, ..., 0.89] (different vector)
```

### Why Embeddings Matter

Traditional keyword search has limitations:
- **Exact matching only**: "ML" won't match "machine learning"
- **No semantic understanding**: Can't understand synonyms or context
- **Poor ranking**: Simple term frequency doesn't capture relevance

Embeddings enable:
- **Semantic search**: Find conceptually similar content
- **Context awareness**: Understand meaning, not just words
- **Better ranking**: Relevance based on meaning

---

## Current Implementation

### Model: all-MiniLM-L6-v2

The system uses `sentence-transformers/all-MiniLM-L6-v2` by default.

**Specifications**:
- **Parameters**: 22.7 million
- **Embedding dimension**: 384
- **Max sequence length**: 256 tokens
- **Speed**: ~1000 sentences/second (CPU)
- **Performance**: Good balance of speed and quality

**Location in code**: `multi_modal_rag/indexing/opensearch_manager.py`

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
```

### How It's Used

1. **During indexing**:
```python
def generate_embedding(self, text: str) -> List[float]:
    """Generate embedding vector for text."""
    embedding = self.model.encode(
        text,
        convert_to_numpy=True,
        normalize_embeddings=True
    )
    return embedding.tolist()
```

2. **During search**:
```python
def hybrid_search(self, query_text: str, size: int = 10):
    """Search using both keywords and embeddings."""
    # Generate query embedding
    query_embedding = self.generate_embedding(query_text)

    # Combine with keyword search
    query = {
        "query": {
            "bool": {
                "should": [
                    # Keyword search
                    {
                        "multi_match": {
                            "query": query_text,
                            "fields": ["title^2", "abstract", "content"]
                        }
                    },
                    # Semantic search
                    {
                        "knn": {
                            "embedding": {
                                "vector": query_embedding,
                                "k": size
                            }
                        }
                    }
                ]
            }
        }
    }
```

---

## Choosing an Embedding Model

### Factors to Consider

1. **Embedding dimension**
   - Larger = more information, but slower and more memory
   - Smaller = faster, less memory, but less nuanced

2. **Model size**
   - Larger models: Better quality, slower inference
   - Smaller models: Faster, use less memory

3. **Domain specialization**
   - General-purpose vs. domain-specific (e.g., scientific text)
   - Pre-trained on similar data = better performance

4. **Speed requirements**
   - Real-time search needs fast models
   - Batch processing can use slower, higher-quality models

5. **Hardware constraints**
   - GPU available? Can use larger models
   - CPU only? Need efficient models

### Decision Tree

```
Do you need real-time search?
├─ Yes → Use small, fast model (MiniLM, TinyBERT)
└─ No → Do you have GPU?
    ├─ Yes → Use larger model (MPNet, BERT-large)
    └─ No → Use medium model (MiniLM, BERT-base)

Is your content domain-specific?
├─ Scientific → Use SciBERT, BioBERT
├─ Legal → Use Legal-BERT
├─ Code → Use CodeBERT
└─ General → Use general models (SBERT, MPNet)
```

---

## Model Comparison

### Popular Sentence Transformer Models

| Model | Dimensions | Size (MB) | Speed* | Quality** |
|-------|-----------|-----------|--------|-----------|
| all-MiniLM-L6-v2 | 384 | 80 | Fast | Good |
| all-mpnet-base-v2 | 768 | 420 | Medium | Excellent |
| all-distilroberta-v1 | 768 | 290 | Medium | Very Good |
| paraphrase-MiniLM-L3-v2 | 384 | 60 | Very Fast | Fair |
| msmarco-distilbert-base-v4 | 768 | 250 | Medium | Very Good |
| multi-qa-mpnet-base-dot-v1 | 768 | 420 | Medium | Excellent |

*Speed: Sentences per second on CPU
**Quality: Performance on semantic search benchmarks

### Detailed Comparisons

#### all-MiniLM-L6-v2 (Current)
```python
# Pros:
# - Fast inference (~1000 sentences/sec)
# - Small memory footprint
# - Good general-purpose performance
# - Easy to run on CPU

# Cons:
# - Lower quality than larger models
# - 256 token limit (short sequences)
# - Not domain-specialized

# Best for:
# - General-purpose applications
# - CPU-only environments
# - Real-time search
```

#### all-mpnet-base-v2 (Recommended Upgrade)
```python
# Pros:
# - State-of-the-art quality
# - 514 token limit (longer sequences)
# - Excellent on benchmarks
# - Still reasonably fast

# Cons:
# - Larger size (420MB vs 80MB)
# - Slower inference (~500 sentences/sec)
# - Needs more memory

# Best for:
# - Quality-focused applications
# - When you have GPU
# - Longer documents
```

#### multi-qa-mpnet-base-dot-v1 (Q&A Specialized)
```python
# Pros:
# - Optimized for question-answering
# - Excellent for asymmetric search (query vs document)
# - High quality results
# - Uses dot product (faster than cosine)

# Cons:
# - Larger model size
# - Slower inference
# - Needs reindexing with dot product space

# Best for:
# - Question-answering systems (like this one!)
# - Asymmetric search scenarios
# - When GPU is available
```

### Domain-Specific Models

#### SciBERT (Scientific Papers)
```python
# Model: allenai/scibert_scivocab_uncased
# Dimensions: 768
# Trained on: Scientific papers (1.14M papers)

# Best for: Academic/scientific content
# Use when: Most content is from scientific papers

model = SentenceTransformer('sentence-transformers/allenai-specter')
```

#### BioBERT (Biomedical)
```python
# Model: dmis-lab/biobert-base-cased-v1.2
# Trained on: PubMed articles

# Best for: Medical/biological research
model = SentenceTransformer('pritamdeka/BioBERT-mnli-snli-scinli-scitail-mednli-stsb')
```

---

## Changing Embedding Models

### Step-by-Step Guide

#### 1. Choose Your Model

```python
# Option 1: Higher quality (recommended)
new_model_name = 'sentence-transformers/all-mpnet-base-v2'
new_dimension = 768

# Option 2: Faster inference
new_model_name = 'sentence-transformers/paraphrase-MiniLM-L3-v2'
new_dimension = 384

# Option 3: Scientific content
new_model_name = 'sentence-transformers/allenai-specter'
new_dimension = 768
```

#### 2. Update opensearch_manager.py

```python
# In __init__ method
class OpenSearchManager:
    def __init__(self, host='localhost', port=9200):
        # ... existing code ...

        # Load new model
        self.model = SentenceTransformer('all-mpnet-base-v2')  # Changed!

        # Update dimension
        self.embedding_dimension = 768  # Changed from 384!
```

#### 3. Update Index Mapping

```python
def create_index(self, index_name='research_assistant'):
    """Create index with updated dimension."""
    index_body = {
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
                    "dimension": 768  # Updated dimension!
                },
                # ... other fields ...
            }
        }
    }

    self.client.indices.create(index=index_name, body=index_body)
```

#### 4. Reindex All Documents

```python
# Delete old index
client.indices.delete(index='research_assistant')

# Create new index with updated dimension
manager.create_index('research_assistant')

# Reindex all documents
# Run your data collection and indexing pipeline
```

### Migration Script

```python
#!/usr/bin/env python3
"""
Script to migrate to a new embedding model.
"""

from multi_modal_rag.indexing.opensearch_manager import OpenSearchManager
from sentence_transformers import SentenceTransformer
import json

def migrate_embeddings(
    old_index='research_assistant',
    new_index='research_assistant_v2',
    new_model_name='all-mpnet-base-v2',
    new_dimension=768
):
    """Migrate to new embedding model."""

    # Initialize
    manager = OpenSearchManager()
    new_model = SentenceTransformer(new_model_name)

    # Create new index
    print(f"Creating new index: {new_index}")
    # Update index creation with new dimension
    manager.create_index(new_index)

    # Get all documents from old index
    print(f"Fetching documents from {old_index}")
    from opensearchpy import helpers

    docs = helpers.scan(
        manager.client,
        index=old_index,
        query={"query": {"match_all": {}}}
    )

    # Reindex with new embeddings
    print("Reindexing with new embeddings...")
    batch = []
    for i, doc in enumerate(docs):
        # Extract text
        text = doc['_source'].get('content', '')

        # Generate new embedding
        new_embedding = new_model.encode(text).tolist()

        # Update document
        doc['_source']['embedding'] = new_embedding

        batch.append({
            '_index': new_index,
            '_id': doc['_id'],
            '_source': doc['_source']
        })

        # Batch insert
        if len(batch) >= 100:
            helpers.bulk(manager.client, batch)
            print(f"Processed {i+1} documents...")
            batch = []

    # Insert remaining
    if batch:
        helpers.bulk(manager.client, batch)

    print(f"Migration complete! {i+1} documents reindexed.")

    # Verify
    count = manager.client.count(index=new_index)
    print(f"New index has {count['count']} documents")

    # Switch alias (optional)
    print("Switching alias...")
    manager.client.indices.update_aliases(body={
        "actions": [
            {"remove": {"index": old_index, "alias": "research"}},
            {"add": {"index": new_index, "alias": "research"}}
        ]
    })

    print("Done! You can now delete the old index:")
    print(f"  curl -X DELETE http://localhost:9200/{old_index}")

if __name__ == '__main__':
    migrate_embeddings()
```

---

## Fine-Tuning Embeddings

### When to Fine-Tune

Fine-tune when:
- Your domain is very specialized
- You have labeled training data
- Pre-trained models perform poorly
- You need maximum quality

### Training Data Format

```python
# Triplet format: (anchor, positive, negative)
training_data = [
    {
        'anchor': 'What is machine learning?',
        'positive': 'Machine learning is a subset of AI...',
        'negative': 'The weather today is sunny...'
    },
    # ... more examples
]

# Or pairs format: (sentence1, sentence2, similarity_score)
training_pairs = [
    ('deep learning', 'neural networks', 0.9),
    ('deep learning', 'pizza recipe', 0.1),
    # ... more pairs
]
```

### Fine-Tuning Script

```python
from sentence_transformers import SentenceTransformer, InputExample, losses
from torch.utils.data import DataLoader

# Load base model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Prepare training data
train_examples = [
    InputExample(texts=[item['anchor'], item['positive'], item['negative']])
    for item in training_data
]

# Create dataloader
train_dataloader = DataLoader(
    train_examples,
    shuffle=True,
    batch_size=16
)

# Define loss
train_loss = losses.TripletLoss(model=model)

# Train
model.fit(
    train_objectives=[(train_dataloader, train_loss)],
    epochs=3,
    warmup_steps=100,
    output_path='./fine_tuned_model'
)

# Use fine-tuned model
custom_model = SentenceTransformer('./fine_tuned_model')
```

---

## Optimization Techniques

### 1. GPU Acceleration

```python
from sentence_transformers import SentenceTransformer
import torch

# Check GPU availability
device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"Using device: {device}")

# Load model on GPU
model = SentenceTransformer('all-MiniLM-L6-v2', device=device)

# Batch encoding (much faster)
texts = ["text 1", "text 2", ..., "text N"]
embeddings = model.encode(
    texts,
    batch_size=64,  # Adjust based on GPU memory
    show_progress_bar=True,
    convert_to_tensor=True  # Keep on GPU
)
```

### 2. Caching Embeddings

```python
import pickle
from functools import lru_cache

class EmbeddingCache:
    """Cache embeddings to avoid recomputation."""

    def __init__(self, cache_file='embeddings_cache.pkl'):
        self.cache_file = cache_file
        self.cache = self._load_cache()

    def _load_cache(self):
        try:
            with open(self.cache_file, 'rb') as f:
                return pickle.load(f)
        except:
            return {}

    def get_embedding(self, text, model):
        """Get embedding from cache or compute."""
        # Use hash as key
        text_hash = hash(text)

        if text_hash not in self.cache:
            self.cache[text_hash] = model.encode(text).tolist()
            self._save_cache()

        return self.cache[text_hash]

    def _save_cache(self):
        with open(self.cache_file, 'wb') as f:
            pickle.dump(self.cache, f)

# Usage
cache = EmbeddingCache()
embedding = cache.get_embedding("machine learning", model)
```

### 3. Dimensionality Reduction

Reduce embedding dimension for faster search:

```python
from sklearn.decomposition import PCA
import numpy as np

# Get original embeddings
embeddings = model.encode(texts)  # Shape: (N, 384)

# Reduce dimensions
pca = PCA(n_components=128)  # Reduce 384 → 128
reduced_embeddings = pca.fit_transform(embeddings)

# Quality vs speed tradeoff:
# 384 → 256: ~99% quality, ~1.5x faster
# 384 → 128: ~95% quality, ~3x faster
# 384 → 64:  ~85% quality, ~6x faster
```

### 4. Quantization

Reduce memory and increase speed:

```python
import numpy as np

def quantize_embeddings(embeddings, bits=8):
    """Quantize embeddings to reduce memory."""
    # Normalize to [0, 1]
    min_val = embeddings.min()
    max_val = embeddings.max()
    normalized = (embeddings - min_val) / (max_val - min_val)

    # Quantize
    scale = (2 ** bits) - 1
    quantized = (normalized * scale).astype(np.uint8)

    return quantized, min_val, max_val

def dequantize_embeddings(quantized, min_val, max_val, bits=8):
    """Reconstruct embeddings."""
    scale = (2 ** bits) - 1
    normalized = quantized.astype(np.float32) / scale
    return normalized * (max_val - min_val) + min_val

# Usage: 8-bit quantization reduces memory by 4x
quantized, min_v, max_v = quantize_embeddings(embeddings, bits=8)
```

---

## Advanced Topics

### Multi-Vector Embeddings

For long documents, use multiple embeddings:

```python
def chunk_and_embed(text, model, chunk_size=256):
    """Split text into chunks and embed each."""
    # Split text
    words = text.split()
    chunks = [
        ' '.join(words[i:i+chunk_size])
        for i in range(0, len(words), chunk_size)
    ]

    # Embed each chunk
    embeddings = model.encode(chunks)

    return embeddings

# Store in OpenSearch
doc = {
    'content': long_text,
    'embeddings': chunk_and_embed(long_text, model),  # List of vectors
    'num_chunks': len(embeddings)
}

# Search: Compare query to all chunks, take max similarity
```

### Cross-Encoder Reranking

Use cross-encoder for better ranking:

```python
from sentence_transformers import CrossEncoder

# Step 1: Fast bi-encoder retrieval (current method)
bi_encoder = SentenceTransformer('all-MiniLM-L6-v2')
candidates = retrieve_top_100(query, bi_encoder)

# Step 2: Slow cross-encoder reranking
cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-12-v2')

# Create query-document pairs
pairs = [[query, doc['content']] for doc in candidates]

# Score pairs
scores = cross_encoder.predict(pairs)

# Rerank
reranked = sorted(
    zip(candidates, scores),
    key=lambda x: x[1],
    reverse=True
)[:10]  # Top 10 after reranking
```

### Multilingual Embeddings

For multilingual support:

```python
# Use multilingual model
model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-mpnet-base-v2')

# Supports 50+ languages
# Same embedding space across languages!

# Example: Search in any language
query_en = "machine learning"
query_fr = "apprentissage automatique"
query_de = "maschinelles Lernen"

# All produce similar embeddings
emb_en = model.encode(query_en)
emb_fr = model.encode(query_fr)
emb_de = model.encode(query_de)

# Cosine similarity ~0.9+
```

---

## Evaluation and Benchmarking

### Measuring Embedding Quality

```python
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def evaluate_embeddings(model, test_queries, relevant_docs):
    """Evaluate embedding quality."""

    # Embed queries and documents
    query_embeddings = model.encode(test_queries)
    doc_embeddings = model.encode(relevant_docs)

    # Calculate similarities
    similarities = cosine_similarity(query_embeddings, doc_embeddings)

    # Calculate metrics
    # Mean Reciprocal Rank (MRR)
    reciprocal_ranks = []
    for i, sim_row in enumerate(similarities):
        # Get rank of correct document
        rank = np.where(np.argsort(sim_row)[::-1] == i)[0][0] + 1
        reciprocal_ranks.append(1.0 / rank)

    mrr = np.mean(reciprocal_ranks)

    # Mean Average Precision (MAP)
    # ... implement MAP calculation

    return {
        'mrr': mrr,
        'map': map_score
    }
```

### Speed Benchmarking

```python
import time

def benchmark_model(model, texts, num_runs=5):
    """Benchmark embedding generation speed."""

    # Warmup
    model.encode(texts[:10])

    # Benchmark
    times = []
    for _ in range(num_runs):
        start = time.time()
        embeddings = model.encode(texts, batch_size=32)
        times.append(time.time() - start)

    avg_time = np.mean(times)
    throughput = len(texts) / avg_time

    print(f"Average time: {avg_time:.2f}s")
    print(f"Throughput: {throughput:.0f} sentences/sec")

    return throughput
```

---

## Additional Resources

- [Sentence Transformers Documentation](https://www.sbert.net/)
- [Hugging Face Model Hub](https://huggingface.co/models?library=sentence-transformers)
- [MTEB Leaderboard](https://huggingface.co/spaces/mteb/leaderboard) (Benchmark rankings)
- [Hybrid Search Guide](./hybrid-search.md)
- [Performance Optimization](./performance.md)

## Best Practices

1. **Start with general models**: all-MiniLM-L6-v2 or all-mpnet-base-v2
2. **Use GPU when possible**: 10-100x speedup for large batches
3. **Cache embeddings**: Don't recompute for same text
4. **Batch processing**: Much faster than one-by-one
5. **Monitor quality**: Use evaluation metrics
6. **Consider domain**: Use specialized models when available
7. **Test before switching**: Compare quality on your data
8. **Document your choice**: Note why you chose a particular model
