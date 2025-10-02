# Tutorial: Custom Searches and Advanced Queries

This tutorial teaches you how to perform advanced searches using the Multi-Modal Academic Research System. You'll learn about query syntax, field boosting, filters, OpenSearch DSL, and optimizing search relevance.

## Table of Contents

1. [Basic Search Concepts](#basic-search-concepts)
2. [Advanced Query Syntax](#advanced-query-syntax)
3. [Field Boosting](#field-boosting)
4. [Combining Filters](#combining-filters)
5. [OpenSearch Query DSL](#opensearch-query-dsl)
6. [Optimizing Search Relevance](#optimizing-search-relevance)
7. [Practical Examples](#practical-examples)

## Basic Search Concepts

### How Search Works

The system uses **hybrid search** combining:

1. **Keyword Matching (BM25):** Traditional text search
2. **Semantic Similarity:** Embedding-based similarity using SentenceTransformer
3. **Field Weighting:** Different fields have different importance

### Searchable Fields

When you search, the system looks through these fields:

- `title` (3x weight): Paper/video/podcast title
- `abstract` (2x weight): Paper abstract or description
- `content`: Full text content
- `transcript`: Video/podcast transcripts
- `key_concepts` (2x weight): Extracted concepts
- `authors`: Author names
- `metadata`: Additional metadata fields

### Simple Search Examples

Using the Gradio UI Research tab:

```
Query: "machine learning transformers"
Result: Searches across all fields, prioritizing title matches
```

```
Query: "attention mechanisms in neural networks"
Result: Semantic search finds related papers even with different wording
```

## Advanced Query Syntax

### Boolean Operators

Combine terms using Boolean logic:

**AND operator:**
```
machine learning AND transformers
```
Both terms must appear in the document.

**OR operator:**
```
transformers OR attention mechanisms
```
Either term can appear in the document.

**NOT operator:**
```
neural networks NOT convolutional
```
Excludes documents containing "convolutional".

**Grouping with parentheses:**
```
(deep learning OR neural networks) AND (computer vision OR image recognition)
```

### Phrase Matching

Search for exact phrases using quotes:

```
"attention is all you need"
```
Matches only documents containing this exact phrase.

```
"generative adversarial network"
```
More precise than individual words.

### Wildcards

Use wildcards for pattern matching:

**Asterisk (*):** Matches any characters
```
transform*
```
Matches: transformer, transformers, transformation, transformed

**Question mark (?):** Matches single character
```
neural networ?
```
Matches: neural network (typo tolerance)

### Fuzzy Search

Handle typos and variations:

```
transformer~
```
Finds similar words like: transformers, transformer, transformed

**Specify edit distance:**
```
transformer~2
```
Allows up to 2 character differences.

### Range Queries

Search within date or numeric ranges:

**Date ranges:**
```
publication_date:[2023-01-01 TO 2023-12-31]
```

**Numeric ranges:**
```
views:[1000 TO *]
```
Videos with 1000+ views.

## Field Boosting

Boost importance of specific fields in your searches.

### Default Field Weights

The system uses these default weights:
- `title`: 3x
- `abstract`: 2x
- `key_concepts`: 2x
- `content`: 1x
- `transcript`: 1x

### Custom Field Boosting

Search specific fields with custom weights using Python API:

```python
from multi_modal_rag.indexing.opensearch_manager import OpenSearchManager

manager = OpenSearchManager()

# Custom search query
search_query = {
    'query': {
        'multi_match': {
            'query': 'deep learning',
            'fields': [
                'title^5',        # 5x weight on title
                'abstract^3',     # 3x weight on abstract
                'content^1',      # 1x weight on content
                'key_concepts^4'  # 4x weight on concepts
            ],
            'type': 'best_fields'
        }
    },
    'size': 20
}

results = manager.client.search(
    index='research_assistant',
    body=search_query
)
```

### Field-Specific Searches

Search only in specific fields:

```python
# Search only in titles
search_query = {
    'query': {
        'match': {
            'title': {
                'query': 'transformers',
                'boost': 1.0
            }
        }
    }
}

# Search only in abstracts
search_query = {
    'query': {
        'match': {
            'abstract': 'attention mechanisms'
        }
    }
}

# Search only in transcripts (for videos)
search_query = {
    'query': {
        'match': {
            'transcript': 'neural network architectures'
        }
    }
}
```

### Combining Multiple Fields

```python
# Title must match, abstract should match
search_query = {
    'query': {
        'bool': {
            'must': [
                {'match': {'title': 'transformer'}}
            ],
            'should': [
                {'match': {'abstract': 'attention mechanisms'}}
            ]
        }
    }
}
```

## Combining Filters

Filters narrow down results without affecting relevance scores.

### Content Type Filters

Filter by content type (paper, video, podcast):

```python
# Only papers
search_query = {
    'query': {
        'bool': {
            'must': [
                {'multi_match': {'query': 'machine learning', 'fields': ['title', 'abstract']}}
            ],
            'filter': [
                {'term': {'content_type': 'paper'}}
            ]
        }
    }
}

# Only videos
search_query = {
    'query': {
        'bool': {
            'must': [
                {'multi_match': {'query': 'deep learning tutorial', 'fields': ['title', 'transcript']}}
            ],
            'filter': [
                {'term': {'content_type': 'video'}}
            ]
        }
    }
}

# Papers or videos (exclude podcasts)
search_query = {
    'query': {
        'bool': {
            'must': [
                {'match': {'title': 'neural networks'}}
            ],
            'filter': [
                {'terms': {'content_type': ['paper', 'video']}}
            ]
        }
    }
}
```

### Date Filters

Filter by publication date:

```python
# Papers from last year
search_query = {
    'query': {
        'bool': {
            'must': [
                {'match': {'title': 'transformers'}}
            ],
            'filter': [
                {
                    'range': {
                        'publication_date': {
                            'gte': '2023-01-01',
                            'lte': '2023-12-31'
                        }
                    }
                }
            ]
        }
    }
}

# Recent papers (last 6 months)
from datetime import datetime, timedelta

six_months_ago = (datetime.now() - timedelta(days=180)).isoformat()

search_query = {
    'query': {
        'bool': {
            'must': [
                {'match': {'content': 'deep learning'}}
            ],
            'filter': [
                {
                    'range': {
                        'publication_date': {
                            'gte': six_months_ago
                        }
                    }
                }
            ]
        }
    }
}
```

### Author Filters

Filter by specific authors:

```python
# Papers by specific author
search_query = {
    'query': {
        'bool': {
            'must': [
                {'match': {'content': 'attention mechanisms'}}
            ],
            'filter': [
                {'term': {'authors': 'Vaswani'}}
            ]
        }
    }
}

# Multiple authors
search_query = {
    'query': {
        'bool': {
            'must': [
                {'match': {'title': 'transformers'}}
            ],
            'filter': [
                {'terms': {'authors': ['Vaswani', 'Hinton', 'Bengio']}}
            ]
        }
    }
}
```

### Category Filters

Filter by ArXiv categories or tags:

```python
# Machine learning papers
search_query = {
    'query': {
        'bool': {
            'must': [
                {'match': {'title': 'neural networks'}}
            ],
            'filter': [
                {'term': {'metadata.categories': 'cs.LG'}}
            ]
        }
    }
}

# Multiple categories
search_query = {
    'query': {
        'bool': {
            'must': [
                {'match_all': {}}
            ],
            'filter': [
                {
                    'terms': {
                        'metadata.categories': ['cs.LG', 'cs.AI', 'cs.CV']
                    }
                }
            ]
        }
    }
}
```

### Combining Multiple Filters

```python
# Papers from 2023, in computer vision, with high relevance
search_query = {
    'query': {
        'bool': {
            'must': [
                {
                    'multi_match': {
                        'query': 'object detection',
                        'fields': ['title^3', 'abstract^2', 'content']
                    }
                }
            ],
            'filter': [
                {'term': {'content_type': 'paper'}},
                {
                    'range': {
                        'publication_date': {
                            'gte': '2023-01-01',
                            'lte': '2023-12-31'
                        }
                    }
                },
                {'term': {'metadata.categories': 'cs.CV'}}
            ]
        }
    },
    'size': 50
}
```

## OpenSearch Query DSL

For maximum control, use OpenSearch Query DSL directly.

### Basic Structure

```python
from multi_modal_rag.indexing.opensearch_manager import OpenSearchManager

manager = OpenSearchManager()

query_dsl = {
    'query': {
        # Query goes here
    },
    'size': 10,           # Number of results
    'from': 0,            # Offset for pagination
    'sort': [],           # Sorting criteria
    '_source': []         # Fields to return
}

results = manager.client.search(
    index='research_assistant',
    body=query_dsl
)
```

### Match Query

Simple text matching:

```python
query_dsl = {
    'query': {
        'match': {
            'title': {
                'query': 'machine learning',
                'operator': 'and',  # Both words must appear
                'fuzziness': 'AUTO'  # Allow typos
            }
        }
    }
}
```

### Multi-Match Query

Search across multiple fields:

```python
query_dsl = {
    'query': {
        'multi_match': {
            'query': 'deep learning neural networks',
            'fields': ['title^3', 'abstract^2', 'content'],
            'type': 'best_fields',  # Use best matching field
            'tie_breaker': 0.3,      # Consider other fields
            'minimum_should_match': '75%'
        }
    }
}
```

**Match types:**
- `best_fields`: Use highest scoring field (default)
- `most_fields`: Combine scores from all fields
- `cross_fields`: Treat fields as one big field
- `phrase`: Match as phrase across fields

### Bool Query

Combine multiple query clauses:

```python
query_dsl = {
    'query': {
        'bool': {
            'must': [
                # Must match all of these
                {'match': {'title': 'transformers'}}
            ],
            'should': [
                # Should match some of these (boosts score)
                {'match': {'abstract': 'attention'}},
                {'match': {'content': 'self-attention'}}
            ],
            'must_not': [
                # Must not match any of these
                {'match': {'content': 'deprecated'}}
            ],
            'filter': [
                # Must match but doesn't affect score
                {'term': {'content_type': 'paper'}},
                {'range': {'publication_date': {'gte': '2023-01-01'}}}
            ],
            'minimum_should_match': 1  # At least 1 should clause
        }
    }
}
```

### Boosting Queries

Boost or demote documents:

```python
query_dsl = {
    'query': {
        'boosting': {
            'positive': {
                # Boost documents matching this
                'match': {'title': 'neural networks'}
            },
            'negative': {
                # Demote documents matching this
                'match': {'content': 'outdated'}
            },
            'negative_boost': 0.3  # Reduce score to 30%
        }
    }
}
```

### Aggregations

Get statistics about your search results:

```python
query_dsl = {
    'query': {
        'match_all': {}
    },
    'size': 0,  # Don't return documents
    'aggs': {
        'by_content_type': {
            'terms': {
                'field': 'content_type',
                'size': 10
            }
        },
        'by_year': {
            'date_histogram': {
                'field': 'publication_date',
                'calendar_interval': 'year'
            }
        },
        'by_author': {
            'terms': {
                'field': 'authors',
                'size': 20
            }
        }
    }
}

results = manager.client.search(index='research_assistant', body=query_dsl)
aggregations = results['aggregations']
```

### Sorting

Custom sort order:

```python
query_dsl = {
    'query': {
        'match': {'title': 'machine learning'}
    },
    'sort': [
        {'publication_date': {'order': 'desc'}},  # Newest first
        {'_score': {'order': 'desc'}},             # Then by relevance
        {'title.keyword': {'order': 'asc'}}        # Then alphabetically
    ]
}
```

### Highlighting

Highlight matching terms in results:

```python
query_dsl = {
    'query': {
        'match': {'content': 'neural networks'}
    },
    'highlight': {
        'fields': {
            'content': {
                'fragment_size': 150,
                'number_of_fragments': 3,
                'pre_tags': ['<strong>'],
                'post_tags': ['</strong>']
            }
        }
    }
}

results = manager.client.search(index='research_assistant', body=query_dsl)
for hit in results['hits']['hits']:
    if 'highlight' in hit:
        print(hit['highlight']['content'])
```

## Optimizing Search Relevance

### Tuning the Hybrid Search

Modify the hybrid search in `opensearch_manager.py`:

```python
def custom_hybrid_search(self, index_name: str, query: str, k: int = 10) -> List[Dict]:
    """Custom hybrid search with adjusted weights"""

    # Generate query embedding
    query_embedding = self.embedding_model.encode(query).tolist()

    search_query = {
        'size': k,
        'query': {
            'bool': {
                'should': [
                    # Text search with custom weights
                    {
                        'multi_match': {
                            'query': query,
                            'fields': [
                                'title^5',           # Increase title weight
                                'abstract^3',        # Increase abstract weight
                                'key_concepts^4',    # Increase concepts weight
                                'content^1',
                                'transcript^1'
                            ],
                            'type': 'best_fields',
                            'tie_breaker': 0.3,
                            'fuzziness': 'AUTO'
                        },
                        'boost': 1.0  # Text search weight
                    },
                    # Add vector search if needed
                ]
            }
        }
    }

    response = self.client.search(index=index_name, body=search_query)
    return [{'score': hit['_score'], 'source': hit['_source']}
            for hit in response['hits']['hits']]
```

### Relevance Tuning Tips

**1. Adjust field weights based on your use case:**

For technical papers:
```python
'fields': ['abstract^4', 'title^3', 'key_concepts^3', 'content^1']
```

For finding specific concepts:
```python
'fields': ['key_concepts^5', 'title^2', 'abstract^2', 'content^1']
```

For broad topic search:
```python
'fields': ['title^2', 'abstract^2', 'content^2', 'transcript^2']
```

**2. Use minimum_should_match:**

```python
'multi_match': {
    'query': 'machine learning neural networks deep',
    'fields': ['title', 'abstract'],
    'minimum_should_match': '75%'  # Match at least 3 of 4 words
}
```

**3. Enable fuzzy matching for typo tolerance:**

```python
'match': {
    'title': {
        'query': 'transformr',  # Typo
        'fuzziness': 'AUTO'
    }
}
```

**4. Use phrase matching for exact terms:**

```python
'bool': {
    'must': [
        {'match_phrase': {'title': 'attention is all you need'}}
    ]
}
```

### Re-ranking Results

Implement custom re-ranking logic:

```python
from multi_modal_rag.indexing.opensearch_manager import OpenSearchManager

def rerank_results(results, query, boost_recent=True):
    """Custom re-ranking function"""
    from datetime import datetime

    reranked = []

    for result in results:
        score = result['score']
        source = result['source']

        # Boost recent papers
        if boost_recent and 'publication_date' in source:
            pub_date = datetime.fromisoformat(source['publication_date'])
            days_old = (datetime.now() - pub_date).days

            # Boost papers less than 1 year old
            if days_old < 365:
                recency_boost = 1.0 + (365 - days_old) / 365 * 0.5
                score *= recency_boost

        # Boost papers with more authors (collaborative work)
        if 'authors' in source and len(source['authors']) > 3:
            score *= 1.1

        # Boost papers with key concepts matching query terms
        if 'key_concepts' in source:
            query_terms = set(query.lower().split())
            concepts = set(c.lower() for c in source['key_concepts'])
            overlap = len(query_terms & concepts)
            if overlap > 0:
                score *= 1.0 + (overlap * 0.1)

        reranked.append({
            'score': score,
            'source': source
        })

    # Sort by new scores
    reranked.sort(key=lambda x: x['score'], reverse=True)
    return reranked

# Usage
manager = OpenSearchManager()
results = manager.hybrid_search('research_assistant', 'machine learning', k=50)
reranked = rerank_results(results, 'machine learning', boost_recent=True)
top_10 = reranked[:10]
```

## Practical Examples

### Example 1: Find Recent Papers on Specific Topic

```python
from multi_modal_rag.indexing.opensearch_manager import OpenSearchManager
from datetime import datetime, timedelta

manager = OpenSearchManager()

# Search for papers from last 3 months
three_months_ago = (datetime.now() - timedelta(days=90)).isoformat()

query = {
    'query': {
        'bool': {
            'must': [
                {
                    'multi_match': {
                        'query': 'large language models',
                        'fields': ['title^3', 'abstract^2', 'content'],
                        'fuzziness': 'AUTO'
                    }
                }
            ],
            'filter': [
                {'term': {'content_type': 'paper'}},
                {
                    'range': {
                        'publication_date': {
                            'gte': three_months_ago
                        }
                    }
                }
            ]
        }
    },
    'sort': [
        {'publication_date': {'order': 'desc'}},
        {'_score': {'order': 'desc'}}
    ],
    'size': 20
}

results = manager.client.search(index='research_assistant', body=query)

print(f"Found {results['hits']['total']['value']} recent papers")
for hit in results['hits']['hits']:
    source = hit['_source']
    print(f"\n{source['title']}")
    print(f"Published: {source['publication_date']}")
    print(f"Authors: {', '.join(source['authors'][:3])}")
```

### Example 2: Search with Author and Topic Filter

```python
# Find papers by specific author on a topic
query = {
    'query': {
        'bool': {
            'must': [
                {
                    'multi_match': {
                        'query': 'reinforcement learning',
                        'fields': ['title', 'abstract']
                    }
                }
            ],
            'filter': [
                {'term': {'authors': 'Sutton'}}
            ]
        }
    }
}

results = manager.client.search(index='research_assistant', body=query)
```

### Example 3: Multi-Source Search (Papers, Videos, Podcasts)

```python
# Search across all content types, group by type
query = {
    'query': {
        'multi_match': {
            'query': 'neural network architectures',
            'fields': ['title^3', 'abstract^2', 'content', 'transcript']
        }
    },
    'aggs': {
        'by_type': {
            'terms': {
                'field': 'content_type'
            },
            'aggs': {
                'top_by_type': {
                    'top_hits': {
                        'size': 5,
                        'sort': [{'_score': {'order': 'desc'}}]
                    }
                }
            }
        }
    },
    'size': 30
}

results = manager.client.search(index='research_assistant', body=query)

# Extract top items per type
for bucket in results['aggregations']['by_type']['buckets']:
    content_type = bucket['key']
    count = bucket['doc_count']
    top_items = bucket['top_by_type']['hits']['hits']

    print(f"\n{content_type.upper()} ({count} total):")
    for item in top_items:
        print(f"  - {item['_source']['title']}")
```

### Example 4: Similarity Search

Find papers similar to a specific paper:

```python
# Get a reference paper
reference_query = {
    'query': {
        'match': {'title': 'Attention is All You Need'}
    },
    'size': 1
}

ref_result = manager.client.search(index='research_assistant', body=reference_query)
reference_paper = ref_result['hits']['hits'][0]['_source']

# Search for similar papers using key concepts and abstract
similar_query = {
    'query': {
        'more_like_this': {
            'fields': ['abstract', 'key_concepts', 'content'],
            'like': [
                {
                    '_index': 'research_assistant',
                    '_id': ref_result['hits']['hits'][0]['_id']
                }
            ],
            'min_term_freq': 1,
            'max_query_terms': 25,
            'min_doc_freq': 1
        }
    },
    'size': 10
}

similar_results = manager.client.search(index='research_assistant', body=similar_query)

print(f"Papers similar to '{reference_paper['title']}':")
for hit in similar_results['hits']['hits']:
    print(f"  - {hit['_source']['title']} (score: {hit['_score']:.2f})")
```

### Example 5: Faceted Search

```python
# Faceted search with multiple filters
query = {
    'query': {
        'match': {'content': 'computer vision'}
    },
    'aggs': {
        'content_types': {
            'terms': {'field': 'content_type'}
        },
        'publication_years': {
            'date_histogram': {
                'field': 'publication_date',
                'calendar_interval': 'year'
            }
        },
        'top_authors': {
            'terms': {
                'field': 'authors',
                'size': 10
            }
        },
        'categories': {
            'terms': {
                'field': 'metadata.categories',
                'size': 20
            }
        }
    },
    'size': 0  # Only get facets, not documents
}

results = manager.client.search(index='research_assistant', body=query)

# Display facets
print("Content Types:")
for bucket in results['aggregations']['content_types']['buckets']:
    print(f"  {bucket['key']}: {bucket['doc_count']}")

print("\nTop Authors:")
for bucket in results['aggregations']['top_authors']['buckets']:
    print(f"  {bucket['key']}: {bucket['doc_count']} papers")
```

## Next Steps

- Learn about [Exporting Citations](export-citations.md) for your research
- Explore [Visualization Dashboard](visualization.md) to analyze search patterns
- Check [Extending the System](extending.md) to customize search behavior
- Review [Collecting Papers](collect-papers.md) to build your research database
