# Orchestration Module

## Overview

The Orchestration module coordinates the end-to-end research query pipeline using LangChain and Google Gemini. It handles document retrieval, context formatting, response generation, citation extraction, and conversation memory management.

## Module Architecture

```
multi_modal_rag/orchestration/
├── research_orchestrator.py    # Main query pipeline
└── citation_tracker.py          # Citation management
```

---

## ResearchOrchestrator

**File**: `multi_modal_rag/orchestration/research_orchestrator.py`

### Class Overview

Orchestrates complex research queries by combining OpenSearch retrieval with LangChain-powered generation. Provides citation tracking, conversation memory, and related query suggestions.

### Initialization

```python
from multi_modal_rag.orchestration import ResearchOrchestrator
from multi_modal_rag.indexing import OpenSearchManager

opensearch = OpenSearchManager()
orchestrator = ResearchOrchestrator(
    gemini_api_key="YOUR_API_KEY",
    opensearch_manager=opensearch
)
```

**Parameters**:
- `gemini_api_key` (str): Google Gemini API key
- `opensearch_manager` (OpenSearchManager): Configured OpenSearch manager

**Components Initialized**:
- LangChain ChatGoogleGenerativeAI with `gemini-2.0-flash` model
- ConversationBufferMemory for chat history
- Temperature set to 0.3 (balanced creativity/accuracy)

---

### Methods

#### `create_research_chain() -> PromptTemplate`

Creates a LangChain prompt template for research queries.

**Returns**: PromptTemplate configured for research assistance

**Prompt Structure**:

```python
template = """
You are a research assistant analyzing multi-modal academic content.

Context from various sources:
{context}

Previous conversation:
{chat_history}

Question: {question}

Instructions:
1. Provide a comprehensive answer based on the context
2. Cite sources using [Author, Year] format
3. Mention if information comes from videos or podcasts
4. Highlight any diagrams or visual content that supports the answer
5. Suggest related topics for further exploration

Answer:
"""
```

**Input Variables**:
- `context`: Formatted search results with citations
- `chat_history`: Previous conversation messages
- `question`: User's research query

**Example**:

```python
orchestrator = ResearchOrchestrator(api_key, opensearch_manager)
prompt = orchestrator.create_research_chain()

# Manually format prompt
formatted = prompt.format(
    context="Context here...",
    chat_history="Previous Q&A...",
    question="What is attention mechanism?"
)
print(formatted)
```

---

#### `process_query(query: str, index_name: str) -> Dict`

Main pipeline for processing research queries.

**Parameters**:
- `query` (str): User's research question
- `index_name` (str): OpenSearch index to search (typically `"research_assistant"`)

**Returns**: Dictionary with results:

```python
{
    'answer': str,                    # Generated response
    'citations': List[Dict],          # Extracted citations
    'source_documents': List[Dict],   # Retrieved documents
    'related_queries': List[str]      # Suggested follow-up queries
}
```

**Pipeline Steps**:

1. **Retrieval**: Search OpenSearch for relevant documents
2. **Context Formatting**: Format results with citation markers
3. **Generation**: Generate response using Gemini
4. **Citation Extraction**: Extract citations from response
5. **Memory Update**: Save to conversation history
6. **Related Queries**: Generate follow-up suggestions

**Example**:

```python
from multi_modal_rag.orchestration import ResearchOrchestrator
from multi_modal_rag.indexing import OpenSearchManager

# Initialize
opensearch = OpenSearchManager()
orchestrator = ResearchOrchestrator("your_api_key", opensearch)

# Process query
result = orchestrator.process_query(
    query="How do transformers use attention mechanisms?",
    index_name="research_assistant"
)

# Access results
print("Answer:")
print(result['answer'])

print("\nCitations:")
for citation in result['citations']:
    print(f"  - {citation['citation_text']}: {citation['title']}")

print("\nSource Documents:")
for doc in result['source_documents']:
    print(f"  - {doc['source']['title']} (score: {doc['score']})")

print("\nRelated Queries:")
for query in result['related_queries']:
    print(f"  - {query}")
```

**Output Example**:

```python
{
    'answer': '''
    Transformers use attention mechanisms to process sequences without recurrence.
    The self-attention mechanism [Vaswani, 2017] allows each position to attend to
    all positions in the previous layer. This is visualized in the architecture
    diagram showing multi-head attention layers. The model computes attention
    scores between query and key vectors, then uses these to weight value vectors.

    Related video content [Video: Illustrated Transformer, 3Blue1Brown] provides
    excellent visualizations of how attention weights are calculated.
    ''',

    'citations': [
        {
            'citation_text': ('Vaswani', '2017'),
            'source': {...},
            'content_type': 'paper',
            'url': 'https://arxiv.org/abs/1706.03762',
            'title': 'Attention Is All You Need'
        },
        {
            'citation_text': ('Illustrated Transformer, 3Blue1Brown',),
            'source': {...},
            'content_type': 'video',
            'url': 'https://youtube.com/watch?v=...',
            'title': 'Illustrated Transformer'
        }
    ],

    'source_documents': [
        {
            'score': 15.42,
            'source': {
                'title': 'Attention Is All You Need',
                'content_type': 'paper',
                'authors': ['Vaswani', 'Shazeer', ...],
                ...
            }
        },
        ...
    ],

    'related_queries': [
        'What are the different types of attention mechanisms?',
        'How does multi-head attention improve model performance?',
        'What are the computational costs of attention?',
        'How do transformers compare to RNNs?',
        'What are recent improvements to attention mechanisms?'
    ]
}
```

---

#### `format_context_with_citations(search_results: List[Dict]) -> str`

Formats search results into context string with citation markers.

**Parameters**:
- `search_results` (List[Dict]): Results from OpenSearch hybrid_search()

**Returns**: Formatted context string

**Citation Formats**:
- Papers: `[FirstAuthor, Year]` (e.g., `[Vaswani, 2017]`)
- Videos: `[Video: Channel, Title...]` (e.g., `[Video: 3Blue1Brown, Neural Networks...]`)
- Podcasts: `[Podcast: Title...]` (e.g., `[Podcast: Lex Fridman discusses...]`)

**Example**:

```python
search_results = [
    {
        'score': 15.42,
        'source': {
            'content_type': 'paper',
            'title': 'Attention Is All You Need',
            'authors': ['Ashish Vaswani', 'Noam Shazeer'],
            'publication_date': '2017-06-12',
            'abstract': 'The dominant sequence transduction models...',
            'diagram_descriptions': 'Architecture diagram showing...'
        }
    }
]

context = orchestrator.format_context_with_citations(search_results)
print(context)
```

**Output**:

```
Source 1 [Vaswani, 2017]:
Title: Attention Is All You Need
Type: paper
Content: The dominant sequence transduction models are based on complex...
Visual Content: Architecture diagram showing encoder-decoder structure with...
```

**Full Context Structure**:

```python
"""
Source 1 [Citation]:
Title: {title}
Type: {content_type}
Content: {first_500_chars}...
Visual Content: {diagram_descriptions}...

Source 2 [Citation]:
Title: {title}
...
"""
```

---

#### `extract_citations(response: str, search_results: List[Dict]) -> List[Dict]`

Extracts citations from generated response and matches them to source documents.

**Parameters**:
- `response` (str): Generated answer text
- `search_results` (List[Dict]): Original search results

**Returns**: List of citation dictionaries

**Citation Patterns** (Regex):
- `\[([^,\]]+),\s*(\d{4})\]` - Paper citations: [Author, Year]
- `\[Video:\s*([^\]]+)\]` - Video citations: [Video: Title]
- `\[Podcast:\s*([^\]]+)\]` - Podcast citations: [Podcast: Title]

**Example**:

```python
response = """
Transformers were introduced by [Vaswani, 2017] and explained visually
in [Video: Illustrated Transformer]. The podcast [Podcast: AI Explained]
also covers this topic.
"""

citations = orchestrator.extract_citations(response, search_results)

for citation in citations:
    print(f"Found citation: {citation['citation_text']}")
    print(f"  Matched to: {citation['title']}")
    print(f"  Type: {citation['content_type']}")
    print(f"  URL: {citation['url']}")
```

**Output**:

```python
[
    {
        'citation_text': ('Vaswani', '2017'),
        'source': {...},  # Full source document
        'content_type': 'paper',
        'url': 'https://arxiv.org/abs/1706.03762',
        'title': 'Attention Is All You Need'
    },
    {
        'citation_text': ('Illustrated Transformer',),
        'source': {...},
        'content_type': 'video',
        'url': 'https://youtube.com/watch?v=...',
        'title': 'Illustrated Transformer'
    },
    {
        'citation_text': ('AI Explained',),
        'source': {...},
        'content_type': 'podcast',
        'url': 'https://...',
        'title': 'AI Explained Episode'
    }
]
```

---

#### `citation_matches_source(citation_match: tuple, source: Dict) -> bool`

Checks if a citation regex match corresponds to a source document.

**Parameters**:
- `citation_match` (tuple): Regex match groups
- `source` (Dict): Source document

**Returns**: Boolean indicating match

**Matching Logic**:
- Papers: Match author name in first author
- Videos: Match text in title
- Podcasts: Match text in title

**Example**:

```python
# Paper citation match
citation_match = ('Vaswani', '2017')
source = {
    'content_type': 'paper',
    'authors': ['Ashish Vaswani', 'Noam Shazeer']
}
matches = orchestrator.citation_matches_source(citation_match, source)
# Returns: True (Vaswani in first author)

# Video citation match
citation_match = ('Illustrated Transformer',)
source = {
    'content_type': 'video',
    'title': 'The Illustrated Transformer'
}
matches = orchestrator.citation_matches_source(citation_match, source)
# Returns: True (text in title)
```

---

#### `generate_related_queries(original_query: str, response: str) -> List[str]`

Generates related research queries based on original query and response.

**Parameters**:
- `original_query` (str): User's original question
- `response` (str): Generated answer (first 500 chars used)

**Returns**: List of 5 related query strings

**Prompt Template**:

```python
prompt = f"""
Based on this research query: "{original_query}"
And this response: "{response[:500]}..."

Generate 5 related research questions that would deepen understanding of this topic.
Format as a JSON list.
"""
```

**Example**:

```python
original = "How do transformers work?"
response = "Transformers use self-attention mechanisms to process sequences..."

related = orchestrator.generate_related_queries(original, response)

for query in related:
    print(f"  • {query}")
```

**Output**:

```python
[
    "What are the key differences between transformers and RNNs?",
    "How does multi-head attention improve model performance?",
    "What are the computational requirements of transformer models?",
    "How are transformers applied to computer vision tasks?",
    "What are recent innovations in transformer architectures?"
]
```

**Fallback** (if JSON parsing fails):

```python
[
    f"What are the key concepts in {original_query}?",
    f"How does {original_query} relate to current research?",
    f"What are recent developments in {original_query}?"
]
```

---

## CitationTracker

**File**: `multi_modal_rag/orchestration/citation_tracker.py`

### Class Overview

Tracks and manages citations across research sessions. Provides citation analytics, usage history, and bibliography export in multiple formats.

### Initialization

```python
from multi_modal_rag.orchestration import CitationTracker

tracker = CitationTracker(storage_path="data/citations.json")
```

**Parameters**:
- `storage_path` (str, optional): Path to JSON storage file. Default: `"data/citations.json"`

**Storage Structure**:

```json
{
    "papers": {
        "citation_id_1": {
            "title": "Attention Is All You Need",
            "authors": ["Ashish Vaswani", "Noam Shazeer"],
            "url": "https://arxiv.org/abs/1706.03762",
            "first_used": "2024-10-02T14:30:00",
            "use_count": 5,
            "queries": [
                {"query": "How do transformers work?", "timestamp": "2024-10-02T14:30:00"},
                ...
            ]
        }
    },
    "videos": {...},
    "podcasts": {...},
    "usage_history": [
        {
            "citation_id": "citation_id_1",
            "content_type": "paper",
            "query": "How do transformers work?",
            "timestamp": "2024-10-02T14:30:00"
        },
        ...
    ]
}
```

---

### Methods

#### `load_citations() -> Dict`

Loads existing citations from storage.

**Returns**: Dictionary with citations or empty structure if file doesn't exist

**Example**:

```python
tracker = CitationTracker("data/citations.json")
# Automatically loads on initialization

# Manual reload
citations = tracker.load_citations()
print(f"Papers: {len(citations['papers'])}")
print(f"Videos: {len(citations['videos'])}")
```

---

#### `save_citations()`

Saves citations to storage file.

**Example**:

```python
tracker = CitationTracker()
# Modify citations
tracker.citations['papers']['new_id'] = {...}
# Save changes
tracker.save_citations()
```

**Auto-save**: Called automatically by `add_citation()`

---

#### `add_citation(citation: Dict, query: str)`

Adds a new citation with usage tracking.

**Parameters**:
- `citation` (Dict): Citation information
- `query` (str): Query that generated this citation

**Citation Structure**:

```python
{
    'content_type': 'paper',  # or 'video', 'podcast'
    'title': str,
    'authors': List[str],
    'url': str
}
```

**Example**:

```python
tracker = CitationTracker()

citation = {
    'content_type': 'paper',
    'title': 'Attention Is All You Need',
    'authors': ['Ashish Vaswani', 'Noam Shazeer'],
    'url': 'https://arxiv.org/abs/1706.03762'
}

tracker.add_citation(citation, query="How do transformers work?")
```

**Tracking Features**:
- Generates unique ID for citation (MD5 hash of title + URL)
- Increments use count if citation exists
- Stores query and timestamp for each use
- Adds to usage history
- Auto-saves to storage

---

#### `generate_citation_id(citation: Dict) -> str`

Generates unique ID for citation.

**Parameters**:
- `citation` (Dict): Citation dictionary

**Returns**: 12-character MD5 hash

**Example**:

```python
citation = {
    'title': 'Attention Is All You Need',
    'url': 'https://arxiv.org/abs/1706.03762'
}

citation_id = tracker.generate_citation_id(citation)
print(citation_id)  # e.g., "a1b2c3d4e5f6"
```

---

#### `get_citation_report() -> Dict`

Generates citation usage report.

**Returns**: Dictionary with statistics:

```python
{
    'total_papers': int,
    'total_videos': int,
    'total_podcasts': int,
    'most_cited': List[Dict],      # Top 5 most used
    'recent_citations': List[Dict]  # Last 10 citations
}
```

**Example**:

```python
tracker = CitationTracker()
report = tracker.get_citation_report()

print(f"Total Papers: {report['total_papers']}")
print(f"Total Videos: {report['total_videos']}")

print("\nMost Cited Sources:")
for item in report['most_cited']:
    print(f"  {item['title']} - used {item['use_count']} times")

print("\nRecent Citations:")
for item in report['recent_citations']:
    print(f"  {item['query']} at {item['timestamp']}")
```

---

#### `get_most_cited(n: int = 5) -> List[Dict]`

Gets most frequently cited sources.

**Parameters**:
- `n` (int, optional): Number of results. Default: 5

**Returns**: List of citation dictionaries sorted by use count

**Example**:

```python
top_citations = tracker.get_most_cited(n=10)

for i, citation in enumerate(top_citations, 1):
    print(f"{i}. {citation['title']}")
    print(f"   Type: {citation['type']}, Used: {citation['use_count']} times")
```

---

#### `get_recent_citations(n: int = 10) -> List[Dict]`

Gets most recent citations.

**Parameters**:
- `n` (int, optional): Number of results. Default: 10

**Returns**: List of recent citation events (reversed chronological order)

**Example**:

```python
recent = tracker.get_recent_citations(n=5)

for citation in recent:
    print(f"Query: {citation['query']}")
    print(f"ID: {citation['citation_id']}")
    print(f"Time: {citation['timestamp']}")
    print()
```

---

#### `export_bibliography(format: str = 'bibtex') -> str`

Exports citations in standard bibliography format.

**Parameters**:
- `format` (str, optional): Export format ('bibtex', 'apa', 'json'). Default: 'bibtex'

**Returns**: Formatted bibliography string

**Supported Formats**:
- `'bibtex'`: BibTeX format
- `'apa'`: APA citation format
- `'json'`: JSON export

**Example**:

```python
tracker = CitationTracker()

# BibTeX export
bibtex = tracker.export_bibliography('bibtex')
print(bibtex)

# APA export
apa = tracker.export_bibliography('apa')
print(apa)

# JSON export
json_export = tracker.export_bibliography('json')
print(json_export)
```

---

#### `export_bibtex() -> str`

Exports citations in BibTeX format.

**Returns**: BibTeX-formatted string

**Example Output**:

```bibtex
@article{a1b2c3d4e5f6,
    title={Attention Is All You Need},
    author={Ashish Vaswani and Noam Shazeer and Niki Parmar},
    year={2017},
    url={https://arxiv.org/abs/1706.03762}
}

@article{b2c3d4e5f6g7,
    title={BERT: Pre-training of Deep Bidirectional Transformers},
    author={Jacob Devlin and Ming-Wei Chang},
    year={2018},
    url={https://arxiv.org/abs/1810.04805}
}
```

**Usage**:

```python
bibtex = tracker.export_bibtex()

# Save to file
with open('references.bib', 'w') as f:
    f.write(bibtex)

# Use in LaTeX
# \bibliography{references}
```

---

#### `export_apa() -> str`

Exports citations in APA format.

**Returns**: APA-formatted string

**Example Output**:

```
Devlin, J. et al. (2018). BERT: Pre-training of Deep Bidirectional Transformers. Retrieved from https://arxiv.org/abs/1810.04805

Vaswani, A. et al. (2017). Attention Is All You Need. Retrieved from https://arxiv.org/abs/1706.03762
```

**Format Details**:
- Single author: `LastName, F. (Year).`
- Multiple authors: `FirstAuthor et al. (Year).`
- No date: Uses `n.d.`
- Sorted alphabetically

---

## Integration Examples

### Complete Research Workflow

```python
from multi_modal_rag.orchestration import ResearchOrchestrator, CitationTracker
from multi_modal_rag.indexing import OpenSearchManager

# Initialize components
opensearch = OpenSearchManager()
orchestrator = ResearchOrchestrator("gemini_api_key", opensearch)
tracker = CitationTracker()

# Process query
query = "How do attention mechanisms work in transformers?"
result = orchestrator.process_query(query, "research_assistant")

# Display answer
print("Answer:")
print(result['answer'])
print()

# Track citations
for citation in result['citations']:
    tracker.add_citation(citation, query)

# View citation report
report = tracker.get_citation_report()
print(f"Total citations tracked: {sum([report['total_papers'], report['total_videos'], report['total_podcasts']])}")

# Export bibliography
bibtex = tracker.export_bibliography('bibtex')
with open('references.bib', 'w') as f:
    f.write(bibtex)
```

### Multi-Turn Conversation

```python
orchestrator = ResearchOrchestrator("api_key", opensearch_manager)

queries = [
    "What is a transformer model?",
    "How does self-attention work?",
    "What are the advantages over RNNs?"
]

for query in queries:
    result = orchestrator.process_query(query, "research_assistant")
    print(f"Q: {query}")
    print(f"A: {result['answer']}\n")

# Memory is preserved across queries
# Later queries can reference earlier answers
```

### Citation Analysis

```python
tracker = CitationTracker()

# Get analytics
report = tracker.get_citation_report()

print("=== Citation Analytics ===\n")

print("Most Cited Sources:")
for i, item in enumerate(report['most_cited'][:5], 1):
    print(f"{i}. {item['title']} ({item['type']})")
    print(f"   Used {item['use_count']} times")
    print()

print("Citation Distribution:")
print(f"  Papers: {report['total_papers']}")
print(f"  Videos: {report['total_videos']}")
print(f"  Podcasts: {report['total_podcasts']}")

# Export for different uses
bibtex = tracker.export_bibliography('bibtex')
apa = tracker.export_bibliography('apa')

with open('references.bib', 'w') as f:
    f.write(bibtex)

with open('references.txt', 'w') as f:
    f.write(apa)
```

---

## LangChain Integration

### Components Used

**LLM**:
```python
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=api_key,
    temperature=0.3,
    convert_system_message_to_human=True
)
```

**Memory**:
```python
from langchain.memory import ConversationBufferMemory

memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)
```

**Prompts**:
```python
from langchain.prompts import PromptTemplate

prompt = PromptTemplate(
    template=template_string,
    input_variables=["context", "chat_history", "question"]
)
```

### Invocation Pattern

```python
# Format prompt
full_prompt = prompt.format(
    context=formatted_context,
    chat_history=str(memory.chat_memory),
    question=query
)

# Generate response
response = llm.invoke(full_prompt).content

# Update memory
memory.save_context(
    {"input": query},
    {"output": response}
)
```

---

## Error Handling

### Query Processing Errors

```python
try:
    result = orchestrator.process_query(query, index_name)
except Exception as e:
    logger.error(f"Error processing query: {e}")
    result = {
        'answer': f"Error processing query: {str(e)}",
        'citations': [],
        'source_documents': [],
        'related_queries': []
    }
```

### Citation Tracking Errors

```python
try:
    tracker.add_citation(citation, query)
except Exception as e:
    logger.error(f"Error tracking citation: {e}")
    # Continue without tracking (non-critical)
```

---

## Dependencies

```python
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory
from langchain.schema import Document
```

**Installation**:
```bash
pip install langchain langchain-google-genai
```

---

## Troubleshooting

### Issue: Related queries not JSON

**Error**: `json.decoder.JSONDecodeError`

**Cause**: LLM doesn't always return valid JSON

**Solution**: Use fallback queries (already implemented)

### Issue: Citations not extracted

**Cause**: Response doesn't match regex patterns

**Solution**: Modify patterns or prompt engineering:
```python
# Add to prompt
"IMPORTANT: Cite sources using exactly this format: [Author, Year]"
```

### Issue: Memory grows too large

**Cause**: Long conversation history

**Solution**: Use ConversationSummaryMemory or limit messages:
```python
from langchain.memory import ConversationSummaryMemory

memory = ConversationSummaryMemory(
    llm=llm,
    memory_key="chat_history"
)
```

---

## Performance Considerations

**Query Processing Time**:
- OpenSearch retrieval: 10-50ms
- Context formatting: 1-5ms
- Gemini generation: 2-5 seconds
- Citation extraction: 10-50ms
- Related query generation: 2-3 seconds
- **Total**: ~4-8 seconds per query

**Optimization Tips**:
1. Cache frequent queries
2. Reduce retrieval count (k=5 instead of k=10)
3. Limit context size (truncate long documents)
4. Skip related query generation for faster responses
