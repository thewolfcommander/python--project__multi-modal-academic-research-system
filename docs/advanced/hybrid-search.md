# Hybrid Search: Algorithm and Implementation

Deep dive into the hybrid search algorithm that combines keyword and semantic search in the Multi-Modal Academic Research System.

## Table of Contents

- [Overview](#overview)
- [Why Hybrid Search?](#why-hybrid-search)
- [Algorithm Details](#algorithm-details)
- [Implementation](#implementation)
- [Score Combination Strategies](#score-combination-strategies)
- [Tuning Parameters](#tuning-parameters)
- [Advanced Techniques](#advanced-techniques)
- [Performance Optimization](#performance-optimization)

---

## Overview

### What is Hybrid Search?

Hybrid search combines two complementary search methods:

1. **Keyword Search (Lexical)**: Traditional text matching using BM25 algorithm
2. **Semantic Search (Vector)**: Neural embeddings with cosine similarity

By combining both, we get the best of both worlds:
- **Precision** from keyword matching (exact terms)
- **Recall** from semantic matching (related concepts)

### Simple Example

**Query**: "ML algorithms"

**Keyword search finds**:
- ✓ Documents containing "ML"
- ✓ Documents containing "algorithms"
- ✗ Documents containing "machine learning" (different term)
- ✗ Documents containing "neural networks" (related concept)

**Semantic search finds**:
- ✓ Documents about "machine learning" (synonym)
- ✓ Documents about "neural networks" (related concept)
- ✗ Documents about "ML" in different context (e.g., "Maximum Likelihood")
- ✗ May miss exact "ML" if discussed differently

**Hybrid search finds**:
- ✓ All of the above, properly weighted and ranked

---

## Why Hybrid Search?

### Limitations of Keyword-Only Search

```python
# Query: "deep learning frameworks"
# Keyword search results:
# 1. Paper with "deep learning frameworks" → Perfect match ✓
# 2. Paper with "DL frameworks" → Missed (abbreviation) ✗
# 3. Paper with "neural network libraries" → Missed (synonyms) ✗
# 4. Paper with "TensorFlow and PyTorch" → Missed (examples) ✗
```

**Problems**:
- Vocabulary mismatch
- No understanding of synonyms
- Can't handle paraphrases
- Misses related concepts

### Limitations of Semantic-Only Search

```python
# Query: "BERT architecture details"
# Semantic search results:
# 1. Paper about transformers → Related ✓
# 2. Paper about attention mechanism → Related ✓
# 3. Paper mentioning "BERT" once → High ranking ✗
# 4. General NLP paper → Too broad ✗
```

**Problems**:
- May miss exact terminology
- Less precise for specific terms
- Can be too broad
- Slower than keyword search

### Benefits of Hybrid Search

| Aspect | Keyword | Semantic | Hybrid |
|--------|---------|----------|--------|
| Exact matches | Excellent | Poor | Excellent |
| Synonyms | Poor | Excellent | Excellent |
| Related concepts | Poor | Excellent | Excellent |
| Precision | High | Medium | High |
| Recall | Low | High | High |
| Speed | Fast | Slower | Medium |

---

## Algorithm Details

### High-Level Flow

```
User Query: "deep learning for NLP"
           |
           v
    ┌──────────────┐
    │ Query Parser │
    └──────────────┘
           |
    ┌──────┴──────┐
    |             |
    v             v
┌─────────┐  ┌─────────┐
│ Keyword │  │ Semantic│
│ Search  │  │ Search  │
│ (BM25)  │  │ (kNN)   │
└─────────┘  └─────────┘
    |             |
    |   Results   |
    |   +Scores   |
    └──────┬──────┘
           v
    ┌──────────────┐
    │ Score Fusion │
    │ (Normalization,│
    │  Combination) │
    └──────────────┘
           |
           v
    ┌──────────────┐
    │ Final Ranking│
    └──────────────┘
           |
           v
      Top N Results
```

### Step-by-Step Breakdown

#### Step 1: Query Processing

```python
def process_query(query_text):
    """Process query for both search methods."""

    # For keyword search: Use as-is
    keyword_query = query_text

    # For semantic search: Generate embedding
    query_embedding = embedding_model.encode(query_text)

    return keyword_query, query_embedding
```

#### Step 2: Keyword Search (BM25)

**BM25 Algorithm**:
```
BM25(D, Q) = Σ IDF(qi) × (f(qi, D) × (k1 + 1)) / (f(qi, D) + k1 × (1 - b + b × |D| / avgdl))

Where:
- D = document
- Q = query
- qi = query term i
- f(qi, D) = frequency of qi in D
- |D| = length of D
- avgdl = average document length
- k1, b = tuning parameters (typically k1=1.5, b=0.75)
- IDF(qi) = inverse document frequency of qi
```

**Implementation**:
```python
def keyword_search(query_text, index, size=100):
    """Perform BM25 keyword search."""

    query = {
        "query": {
            "multi_match": {
                "query": query_text,
                "fields": [
                    "title^3",      # 3x weight
                    "abstract^2",   # 2x weight
                    "content^1",    # 1x weight
                    "key_concepts^2"
                ],
                "type": "best_fields",
                "operator": "or"
            }
        },
        "size": size
    }

    response = client.search(index=index, body=query)

    return [
        {
            'id': hit['_id'],
            'score': hit['_score'],
            'source': hit['_source']
        }
        for hit in response['hits']['hits']
    ]
```

#### Step 3: Semantic Search (kNN)

**Cosine Similarity**:
```
similarity(A, B) = (A · B) / (||A|| × ||B||)

Where:
- A, B = embedding vectors
- A · B = dot product
- ||A|| = magnitude of A
```

**Implementation**:
```python
def semantic_search(query_embedding, index, size=100):
    """Perform kNN semantic search."""

    query = {
        "query": {
            "knn": {
                "embedding": {
                    "vector": query_embedding,
                    "k": size
                }
            }
        },
        "size": size
    }

    response = client.search(index=index, body=query)

    return [
        {
            'id': hit['_id'],
            'score': hit['_score'],
            'source': hit['_source']
        }
        for hit in response['hits']['hits']
    ]
```

#### Step 4: Score Normalization

**Problem**: BM25 scores and cosine similarities have different scales.

**Solution**: Normalize to [0, 1] range.

```python
def min_max_normalize(scores):
    """Normalize scores to [0, 1] range."""
    if not scores:
        return []

    min_score = min(scores)
    max_score = max(scores)

    if max_score == min_score:
        return [1.0] * len(scores)

    return [
        (score - min_score) / (max_score - min_score)
        for score in scores
    ]

def z_score_normalize(scores):
    """Normalize using z-score (mean=0, std=1)."""
    if not scores:
        return []

    mean = np.mean(scores)
    std = np.std(scores)

    if std == 0:
        return [0.0] * len(scores)

    return [
        (score - mean) / std
        for score in scores
    ]
```

#### Step 5: Score Combination

**Linear Combination**:
```python
def combine_scores(keyword_score, semantic_score, alpha=0.5):
    """
    Combine scores using weighted average.

    Args:
        keyword_score: Normalized BM25 score
        semantic_score: Normalized cosine similarity
        alpha: Weight for keyword score (1-alpha for semantic)

    Returns:
        Combined score
    """
    return alpha * keyword_score + (1 - alpha) * semantic_score
```

#### Step 6: Result Merging and Ranking

```python
def merge_results(keyword_results, semantic_results, alpha=0.5):
    """Merge and rank results from both searches."""

    # Extract scores
    keyword_scores = [r['score'] for r in keyword_results]
    semantic_scores = [r['score'] for r in semantic_results]

    # Normalize
    keyword_scores_norm = min_max_normalize(keyword_scores)
    semantic_scores_norm = min_max_normalize(semantic_scores)

    # Create score dictionary
    combined_scores = {}

    # Add keyword results
    for result, norm_score in zip(keyword_results, keyword_scores_norm):
        doc_id = result['id']
        combined_scores[doc_id] = {
            'keyword_score': norm_score,
            'semantic_score': 0.0,
            'source': result['source']
        }

    # Add semantic results
    for result, norm_score in zip(semantic_results, semantic_scores_norm):
        doc_id = result['id']
        if doc_id in combined_scores:
            combined_scores[doc_id]['semantic_score'] = norm_score
        else:
            combined_scores[doc_id] = {
                'keyword_score': 0.0,
                'semantic_score': norm_score,
                'source': result['source']
            }

    # Combine scores
    final_results = []
    for doc_id, scores in combined_scores.items():
        combined_score = combine_scores(
            scores['keyword_score'],
            scores['semantic_score'],
            alpha=alpha
        )

        final_results.append({
            'id': doc_id,
            'combined_score': combined_score,
            'keyword_score': scores['keyword_score'],
            'semantic_score': scores['semantic_score'],
            'source': scores['source']
        })

    # Sort by combined score
    final_results.sort(key=lambda x: x['combined_score'], reverse=True)

    return final_results
```

---

## Implementation

### Complete Hybrid Search Function

```python
from typing import List, Dict
import numpy as np
from opensearchpy import OpenSearch
from sentence_transformers import SentenceTransformer

class HybridSearch:
    """Hybrid search combining keyword and semantic search."""

    def __init__(self, client: OpenSearch, model: SentenceTransformer):
        self.client = client
        self.model = model

    def search(
        self,
        query: str,
        index: str = 'research_assistant',
        size: int = 10,
        alpha: float = 0.5,
        keyword_size: int = 100,
        semantic_size: int = 100
    ) -> List[Dict]:
        """
        Perform hybrid search.

        Args:
            query: Search query
            index: Index name
            size: Number of results to return
            alpha: Weight for keyword score (0-1)
            keyword_size: Number of keyword results to retrieve
            semantic_size: Number of semantic results to retrieve

        Returns:
            List of search results with combined scores
        """

        # 1. Generate query embedding
        query_embedding = self.model.encode(query).tolist()

        # 2. Keyword search
        keyword_results = self._keyword_search(
            query, index, keyword_size
        )

        # 3. Semantic search
        semantic_results = self._semantic_search(
            query_embedding, index, semantic_size
        )

        # 4. Merge and rank
        combined_results = self._merge_results(
            keyword_results,
            semantic_results,
            alpha=alpha
        )

        # 5. Return top N
        return combined_results[:size]

    def _keyword_search(
        self,
        query: str,
        index: str,
        size: int
    ) -> List[Dict]:
        """Perform keyword search."""

        query_body = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": [
                        "title^3",
                        "abstract^2",
                        "content^1",
                        "key_concepts^2",
                        "diagram_descriptions^1.5"
                    ],
                    "type": "best_fields",
                    "operator": "or",
                    "fuzziness": "AUTO"
                }
            },
            "size": size
        }

        response = self.client.search(index=index, body=query_body)

        return [
            {
                'id': hit['_id'],
                'score': hit['_score'],
                'source': hit['_source']
            }
            for hit in response['hits']['hits']
        ]

    def _semantic_search(
        self,
        query_embedding: List[float],
        index: str,
        size: int
    ) -> List[Dict]:
        """Perform semantic search."""

        query_body = {
            "query": {
                "knn": {
                    "embedding": {
                        "vector": query_embedding,
                        "k": size
                    }
                }
            },
            "size": size
        }

        response = self.client.search(index=index, body=query_body)

        return [
            {
                'id': hit['_id'],
                'score': hit['_score'],
                'source': hit['_source']
            }
            for hit in response['hits']['hits']
        ]

    def _merge_results(
        self,
        keyword_results: List[Dict],
        semantic_results: List[Dict],
        alpha: float
    ) -> List[Dict]:
        """Merge and rank results."""

        # Normalize scores
        keyword_scores = [r['score'] for r in keyword_results]
        semantic_scores = [r['score'] for r in semantic_results]

        keyword_norm = self._min_max_normalize(keyword_scores)
        semantic_norm = self._min_max_normalize(semantic_scores)

        # Combine scores
        combined = {}

        for result, norm_score in zip(keyword_results, keyword_norm):
            doc_id = result['id']
            combined[doc_id] = {
                'keyword': norm_score,
                'semantic': 0.0,
                'source': result['source']
            }

        for result, norm_score in zip(semantic_results, semantic_norm):
            doc_id = result['id']
            if doc_id in combined:
                combined[doc_id]['semantic'] = norm_score
            else:
                combined[doc_id] = {
                    'keyword': 0.0,
                    'semantic': norm_score,
                    'source': result['source']
                }

        # Calculate final scores
        final_results = []
        for doc_id, scores in combined.items():
            final_score = (
                alpha * scores['keyword'] +
                (1 - alpha) * scores['semantic']
            )

            final_results.append({
                'id': doc_id,
                'score': final_score,
                'keyword_score': scores['keyword'],
                'semantic_score': scores['semantic'],
                'source': scores['source']
            })

        # Sort by score
        final_results.sort(key=lambda x: x['score'], reverse=True)

        return final_results

    @staticmethod
    def _min_max_normalize(scores: List[float]) -> List[float]:
        """Normalize scores to [0, 1] range."""
        if not scores:
            return []

        min_score = min(scores)
        max_score = max(scores)

        if max_score == min_score:
            return [1.0] * len(scores)

        return [
            (score - min_score) / (max_score - min_score)
            for score in scores
        ]

# Usage
search = HybridSearch(client, model)
results = search.search(
    query="deep learning for natural language processing",
    size=10,
    alpha=0.5  # Equal weight
)

for i, result in enumerate(results, 1):
    print(f"{i}. {result['source']['title']}")
    print(f"   Combined: {result['score']:.3f}")
    print(f"   Keyword: {result['keyword_score']:.3f}")
    print(f"   Semantic: {result['semantic_score']:.3f}")
```

---

## Score Combination Strategies

### 1. Linear Combination (Current)

```python
score = α × keyword_score + (1 - α) × semantic_score
```

**Pros**:
- Simple and interpretable
- Easy to tune with single parameter α
- Fast computation

**Cons**:
- Assumes linear relationship
- May not capture complex interactions

**When to use**: Default choice, works well in most cases.

### 2. Reciprocal Rank Fusion (RRF)

```python
def reciprocal_rank_fusion(keyword_ranks, semantic_ranks, k=60):
    """
    Combine using RRF algorithm.

    Args:
        keyword_ranks: Dict mapping doc_id to rank in keyword results
        semantic_ranks: Dict mapping doc_id to rank in semantic results
        k: Constant (typically 60)

    Returns:
        Combined scores
    """
    all_docs = set(keyword_ranks.keys()) | set(semantic_ranks.keys())

    scores = {}
    for doc_id in all_docs:
        keyword_score = 1 / (k + keyword_ranks.get(doc_id, 1000))
        semantic_score = 1 / (k + semantic_ranks.get(doc_id, 1000))
        scores[doc_id] = keyword_score + semantic_score

    return scores
```

**Pros**:
- No normalization needed
- Robust to score scale differences
- Parameter-free (except k)

**Cons**:
- Only uses rank information (ignores score magnitude)
- May miss nuance in scores

**When to use**: When score scales are very different or unreliable.

### 3. Bayesian Combination

```python
def bayesian_combination(keyword_score, semantic_score, prior=0.5):
    """
    Combine scores using Bayesian approach.

    Assumes scores are probabilities of relevance.
    """
    # Convert scores to probabilities
    p_relevant_keyword = keyword_score
    p_relevant_semantic = semantic_score

    # Bayes' theorem
    posterior = (
        (p_relevant_keyword * p_relevant_semantic * prior) /
        (p_relevant_keyword * p_relevant_semantic * prior +
         (1 - p_relevant_keyword) * (1 - p_relevant_semantic) * (1 - prior))
    )

    return posterior
```

**Pros**:
- Theoretically grounded
- Accounts for uncertainty
- Can incorporate prior knowledge

**Cons**:
- Assumes independence (often violated)
- Requires probability interpretation
- More complex

**When to use**: When you have probabilistic scores and independence assumptions hold.

### 4. Harmonic Mean

```python
def harmonic_mean(keyword_score, semantic_score, alpha=0.5):
    """
    Combine using weighted harmonic mean.

    Penalizes imbalanced scores more than arithmetic mean.
    """
    if keyword_score == 0 or semantic_score == 0:
        return 0

    return 1 / (alpha / keyword_score + (1 - alpha) / semantic_score)
```

**Pros**:
- Penalizes very low scores in one component
- Good when both components should be strong

**Cons**:
- Sensitive to zero scores
- More conservative than arithmetic mean

**When to use**: When you want both keyword and semantic to contribute meaningfully.

---

## Tuning Parameters

### Alpha (α) - Keyword vs Semantic Weight

The α parameter controls the balance between keyword and semantic search.

**Values**:
- `α = 0.0`: Pure semantic search
- `α = 0.5`: Equal weight (default)
- `α = 1.0`: Pure keyword search

**Guidelines**:

| Query Type | Recommended α | Reasoning |
|-----------|--------------|-----------|
| Exact terminology | 0.7 - 0.9 | Prioritize keyword matching |
| Concept exploration | 0.1 - 0.3 | Prioritize semantic similarity |
| Technical terms | 0.6 - 0.8 | Exact terms matter |
| Natural questions | 0.3 - 0.5 | Semantic understanding helps |
| Short queries | 0.4 - 0.6 | Balance both |
| Long queries | 0.3 - 0.5 | More context for semantic |

**Tuning Process**:

```python
def find_optimal_alpha(queries, ground_truth):
    """Find optimal alpha using validation set."""

    alphas = np.arange(0, 1.1, 0.1)
    best_alpha = 0.5
    best_score = 0

    for alpha in alphas:
        scores = []
        for query, relevant_docs in zip(queries, ground_truth):
            results = hybrid_search(query, alpha=alpha)
            score = evaluate_ranking(results, relevant_docs)
            scores.append(score)

        avg_score = np.mean(scores)
        if avg_score > best_score:
            best_score = avg_score
            best_alpha = alpha

    print(f"Optimal alpha: {best_alpha} (score: {best_score:.3f})")
    return best_alpha
```

### Field Weights

Control importance of different document fields:

```python
fields = [
    "title^3",           # Title most important
    "abstract^2",        # Abstract very important
    "key_concepts^2",    # Key concepts important
    "content^1",         # Content baseline
    "diagram_descriptions^1.5"  # Diagrams somewhat important
]
```

**Tuning tips**:
- Start with `title^3`, `abstract^2`, `content^1`
- Increase if field should be more important
- Test with queries targeting each field
- Monitor impact on overall quality

---

## Advanced Techniques

### Query Expansion

Expand query before searching:

```python
def expand_query(query, model, top_k=5):
    """Expand query with similar terms."""

    # Get query embedding
    query_emb = model.encode(query)

    # Find similar terms (using pre-built term index)
    similar_terms = find_similar_terms(query_emb, top_k)

    # Combine
    expanded = f"{query} {' '.join(similar_terms)}"

    return expanded

# Usage
expanded = expand_query("ML algorithms")
# Result: "ML algorithms machine learning classification regression neural networks"
```

### Personalization

Adapt search based on user history:

```python
def personalized_search(query, user_history, alpha=0.5, beta=0.2):
    """
    Personalized hybrid search.

    Args:
        query: Search query
        user_history: List of previously viewed documents
        alpha: Keyword vs semantic weight
        beta: Personalization weight
    """

    # Standard hybrid search
    results = hybrid_search(query, alpha=alpha)

    # Calculate personalization scores
    for result in results:
        doc_vector = result['source']['embedding']

        # Similarity to user history
        history_similarities = [
            cosine_similarity(doc_vector, hist_doc['embedding'])
            for hist_doc in user_history
        ]

        personalization_score = np.mean(history_similarities)

        # Combine with hybrid score
        result['score'] = (
            (1 - beta) * result['score'] +
            beta * personalization_score
        )

    # Re-sort
    results.sort(key=lambda x: x['score'], reverse=True)

    return results
```

### Multi-Stage Retrieval

Retrieve in stages for efficiency:

```python
def multi_stage_search(query, size=10):
    """
    Multi-stage retrieval:
    1. Fast keyword retrieval (top 1000)
    2. Semantic reranking (top 100)
    3. Cross-encoder reranking (top 10)
    """

    # Stage 1: Fast keyword retrieval
    candidates = keyword_search(query, size=1000)

    # Stage 2: Semantic reranking
    query_emb = model.encode(query)
    for candidate in candidates:
        doc_emb = candidate['source']['embedding']
        semantic_score = cosine_similarity(query_emb, doc_emb)
        candidate['score'] = (
            0.5 * candidate['score'] +
            0.5 * semantic_score
        )

    candidates.sort(key=lambda x: x['score'], reverse=True)
    top_100 = candidates[:100]

    # Stage 3: Cross-encoder reranking (expensive but accurate)
    cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-12-v2')
    pairs = [[query, c['source']['content'][:512]] for c in top_100]
    cross_scores = cross_encoder.predict(pairs)

    for candidate, cross_score in zip(top_100, cross_scores):
        candidate['score'] = cross_score

    top_100.sort(key=lambda x: x['score'], reverse=True)

    return top_100[:size]
```

---

## Performance Optimization

### Caching

```python
from functools import lru_cache
import hashlib

class CachedHybridSearch:
    """Hybrid search with result caching."""

    def __init__(self, client, model):
        self.client = client
        self.model = model
        self.cache = {}

    def search(self, query, **kwargs):
        """Search with caching."""

        # Create cache key
        cache_key = self._create_cache_key(query, kwargs)

        # Check cache
        if cache_key in self.cache:
            return self.cache[cache_key]

        # Perform search
        results = self._hybrid_search(query, **kwargs)

        # Cache results
        self.cache[cache_key] = results

        return results

    def _create_cache_key(self, query, kwargs):
        """Create cache key from query and parameters."""
        key_string = f"{query}_{str(sorted(kwargs.items()))}"
        return hashlib.md5(key_string.encode()).hexdigest()
```

### Parallel Execution

```python
import concurrent.futures

def parallel_hybrid_search(query, client, model):
    """Execute keyword and semantic search in parallel."""

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        # Submit both searches
        keyword_future = executor.submit(keyword_search, query, client)
        semantic_future = executor.submit(
            semantic_search,
            model.encode(query),
            client
        )

        # Wait for both to complete
        keyword_results = keyword_future.result()
        semantic_results = semantic_future.result()

    # Merge results
    return merge_results(keyword_results, semantic_results)
```

---

## Additional Resources

- [Embedding Models Guide](./embedding-models.md)
- [Performance Optimization](./performance.md)
- [OpenSearch kNN Documentation](https://opensearch.org/docs/latest/search-plugins/knn/index/)
- [BM25 Algorithm](https://en.wikipedia.org/wiki/Okapi_BM25)

## Best Practices

1. **Start with α = 0.5**: Equal weight as baseline
2. **Use field boosting**: Weight title and abstract higher
3. **Normalize scores**: Always normalize before combining
4. **Test on real queries**: Use actual user queries for tuning
5. **Monitor performance**: Track both speed and quality metrics
6. **Consider query type**: Adapt α based on query characteristics
7. **Iterate**: Continuously evaluate and refine parameters
