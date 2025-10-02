# Data Flow Architecture

## Overview

This document details how data flows through the Multi-Modal Academic Research System, from initial collection to final query response.

## Complete System Data Flow

```
External Sources (ArXiv, YouTube, Podcasts)
             │
             ▼
    ┌─────────────────┐
    │  Data Collectors│  ← User initiates via Gradio UI
    └────────┬────────┘
             │ Raw metadata + files
             ├──────────┬──────────────┐
             ▼          ▼              ▼
      ┌───────────┐ ┌──────────┐ ┌──────────┐
      │ File      │ │ Database │ │Processors│
      │ Storage   │ │ (SQLite) │ │          │
      └───────────┘ └──────────┘ └────┬─────┘
                                      │ Structured documents
                                      ▼
                               ┌──────────────┐
                               │  OpenSearch  │
                               │   Indexing   │
                               └──────┬───────┘
                                      │
                                      ▼
                         Indexed + Searchable Content
                                      │
                  ┌───────────────────┴────────────────┐
                  ▼                                    ▼
         ┌─────────────────┐                  ┌──────────────┐
         │  Query/Search   │                  │Visualization │
         │  (Orchestrator) │                  │     API      │
         └────────┬────────┘                  └──────────────┘
                  │
                  ▼
         Response with Citations
```

## 1. Data Collection Flow

### Step-by-Step Process

```
┌─────────────────────────────────────────────────────────────┐
│                    USER ACTION                               │
│  User clicks "Collect Data" in Gradio UI                    │
│  Selects: Source Type | Query | Max Results                 │
└──────────────────────┬──────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────┐
│               GRADIO UI (gradio_app.py)                      │
│  handle_data_collection()                                    │
│  - Validates input                                           │
│  - Routes to appropriate collector                           │
└──────────────────────┬──────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────┐
│          DATA COLLECTOR (paper_collector.py, etc)            │
│                                                              │
│  ArXiv Papers:                                               │
│   1. arxiv.Search(query, max_results)                       │
│   2. For each result:                                        │
│      - Extract metadata (title, authors, abstract, etc)     │
│      - Download PDF to data/papers/                         │
│      - Return metadata dict                                  │
│                                                              │
│  YouTube Videos:                                             │
│   1. yt_dlp.YoutubeDL.extract_info(search_query)           │
│   2. For each video:                                        │
│      - Extract metadata (title, channel, views, etc)        │
│      - Fetch transcript via YouTubeTranscriptApi            │
│      - Save metadata to data/videos/                        │
│      - Return metadata dict                                  │
│                                                              │
│  Podcasts:                                                   │
│   1. feedparser.parse(rss_url)                             │
│   2. For each episode:                                      │
│      - Extract metadata (title, description, audio_url)     │
│      - Optionally transcribe with Whisper                   │
│      - Save metadata to data/podcasts/                      │
│      - Return metadata dict                                  │
└──────────────────────┬──────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────┐
│          DATABASE TRACKING (db_manager.py)                   │
│                                                              │
│  For each collected item:                                    │
│   1. db_manager.add_collection()                            │
│      - INSERT INTO collections (type, title, source, url...)│
│      - Returns collection_id                                 │
│                                                              │
│   2. db_manager.add_paper/video/podcast(collection_id, data)│
│      - INSERT INTO papers/videos/podcasts (type-specific)   │
│                                                              │
│   3. db_manager.log_collection_stats()                      │
│      - INSERT INTO collection_stats (query, count, source)  │
└──────────────────────┬──────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────┐
│          DATA PROCESSING (pdf_processor.py, etc)             │
│                                                              │
│  Paper Processing:                                           │
│   1. PDFProcessor.extract_text(pdf_path)                   │
│      - Use PyMuPDF to extract full text                    │
│   2. PDFProcessor.extract_diagrams(pdf_path)               │
│      - Extract images from PDF                             │
│      - Send to Gemini Vision for description               │
│   3. Return structured document                             │
│                                                              │
│  Video Processing:                                           │
│   1. VideoProcessor.analyze_transcript(transcript)         │
│      - Send to Gemini for analysis                         │
│      - Extract key concepts                                 │
│   2. Return structured document                             │
└──────────────────────┬──────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────┐
│          OPENSEARCH INDEXING (opensearch_manager.py)         │
│                                                              │
│  For each document:                                          │
│   1. Format document for indexing:                          │
│      {                                                       │
│        content_type: 'paper'/'video'/'podcast',            │
│        title, abstract, content, authors,                   │
│        publication_date, url, metadata                      │
│      }                                                       │
│                                                              │
│   2. Generate embedding:                                     │
│      text = title + abstract + content[:1000]              │
│      embedding = SentenceTransformer.encode(text)          │
│      → 384-dimensional vector                               │
│                                                              │
│   3. Bulk index to OpenSearch:                              │
│      - Index with kNN vector + text fields                  │
│      - Indexed count returned                               │
└──────────────────────┬──────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────┐
│          MARK AS INDEXED (db_manager.py)                     │
│                                                              │
│  For each collection_id:                                     │
│   - UPDATE collections SET indexed = 1 WHERE id = ?         │
└──────────────────────┬──────────────────────────────────────┘
                       ▼
           ✅ Collection Complete!
           Data is now searchable
```

### Collection Flow Diagram

```
User Input
    │
    ├─→ Query: "machine learning"
    ├─→ Source: ArXiv Papers
    └─→ Max: 20 results
         │
         ▼
ArXiv API Call ─→ 20 Papers Retrieved
         │
         ├─→ Paper 1 → [PDF Download] → data/papers/2304.05133v2.pdf
         │                │
         │                └─→ [DB Insert] → collections.id=1, papers.id=1
         │                         │
         │                         └─→ [Process] → Extract text + diagrams
         │                                  │
         │                                  └─→ [Index] → OpenSearch doc_1
         │                                           │
         │                                           └─→ [Mark] → indexed=True
         │
         ├─→ Paper 2 → ... (repeat process)
         │
         └─→ Paper 20 → ... (repeat process)
              │
              ▼
         Statistics Updated
         Database: 20 new papers
         OpenSearch: 20 new documents
```

## 2. Query/Search Flow

### Step-by-Step Process

```
┌─────────────────────────────────────────────────────────────┐
│                    USER ACTION                               │
│  User enters query: "What is RAG?"                          │
│  Clicks "Search" in Gradio UI                               │
└──────────────────────┬──────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────┐
│          RESEARCH ORCHESTRATOR (research_orchestrator.py)    │
│                                                              │
│  process_query(query, index_name):                          │
│   1. Clean and normalize query                              │
│   2. Call OpenSearchManager.hybrid_search(query, k=10)     │
└──────────────────────┬──────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────┐
│          OPENSEARCH HYBRID SEARCH (opensearch_manager.py)    │
│                                                              │
│  hybrid_search(query, k=10):                                │
│   1. Text Search (BM25):                                    │
│      - Multi-match query on:                                │
│        * title^3 (3x weight)                                │
│        * abstract^2 (2x weight)                             │
│        * content (1x weight)                                │
│        * transcript (1x weight)                             │
│        * key_concepts^2 (2x weight)                         │
│      - Fuzzy matching enabled                               │
│                                                              │
│   2. Execute search on OpenSearch index                     │
│                                                              │
│   3. Return top-k results with scores:                      │
│      [{score: 8.5, source: {...}}, ...]                    │
└──────────────────────┬──────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────┐
│          CONTEXT FORMATION (research_orchestrator.py)        │
│                                                              │
│  Format retrieved documents as context:                      │
│                                                              │
│  "You are a research assistant. Use these sources:          │
│                                                              │
│   Source 1 [paper]:                                         │
│   Title: Attention Is All You Need                          │
│   Content: Transformers are neural network...               │
│                                                              │
│   Source 2 [video]:                                         │
│   Title: Understanding Transformers                          │
│   Transcript: In this lecture we discuss...                 │
│                                                              │
│   ...                                                        │
│                                                              │
│   Answer the question: {query}                              │
│   Provide citations using [Source N] format."               │
└──────────────────────┬──────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────┐
│          GEMINI LLM PROCESSING (via LangChain)               │
│                                                              │
│  Input: Context + Query                                      │
│  Model: Gemini Pro                                           │
│                                                              │
│  LLM generates response:                                     │
│   "RAG (Retrieval-Augmented Generation) is a technique     │
│    that combines information retrieval with text generation │
│    [Source 1]. It works by first retrieving relevant        │
│    documents from a knowledge base, then using those        │
│    documents as context for an LLM to generate accurate     │
│    responses [Source 3]..."                                 │
│                                                              │
│  Output: Generated text with citation markers               │
└──────────────────────┬──────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────┐
│          CITATION EXTRACTION (citation_tracker.py)           │
│                                                              │
│  extract_citations(response_text):                          │
│   1. Regex pattern: \[Source (\d+)\]                       │
│   2. Find all matches → [1, 1, 3]                          │
│   3. Map to actual source documents                         │
│   4. Create citation objects:                               │
│      [{                                                      │
│        text: "Source 1",                                    │
│        title: "Attention Is All You Need",                 │
│        authors: ["Vaswani, A.", ...],                      │
│        url: "https://arxiv.org/abs/..."                    │
│      }, ...]                                                │
│                                                              │
│  track_citations(citations):                                │
│   - Increment citation count for each source                │
│   - Store in citation database                              │
└──────────────────────┬──────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────┐
│          RESPONSE FORMATTING (gradio_app.py)                 │
│                                                              │
│  Format for display:                                         │
│                                                              │
│  ## Answer                                                   │
│  RAG (Retrieval-Augmented Generation) is a technique...    │
│                                                              │
│  ---                                                         │
│  **Sources Used:** 3                                         │
│                                                              │
│  Citations (JSON):                                           │
│  [                                                           │
│    {title: "...", authors: [...], url: "..."},            │
│    ...                                                       │
│  ]                                                           │
│                                                              │
│  Related Queries:                                            │
│  1. What are transformers in deep learning?                 │
│  2. How does attention mechanism work?                      │
└──────────────────────┬──────────────────────────────────────┘
                       ▼
           Display to User in Gradio UI
```

### Query Flow Diagram

```
"What is RAG?"
      │
      ▼
Hybrid Search ──→ OpenSearch Query
      │              │
      │              ├─→ BM25 Text Match: title^3, abstract^2, content
      │              │
      │              └─→ Results: Top 10 documents by relevance score
      │
      ▼
Context Assembly
      │
      ├─→ Source 1: [paper] "RAG Paper" (score: 9.2)
      ├─→ Source 2: [video] "RAG Explained" (score: 8.5)
      └─→ Source 3: [paper] "LLM Survey" (score: 7.8)
      │
      ▼
LLM Processing (Gemini)
      │
      ├─→ Prompt: Context + Sources + Query
      │
      └─→ Response: "RAG is... [Source 1] ... [Source 3]"
           │
           ▼
Citation Extraction
      │
      └─→ Extracted: [Source 1, Source 3]
           │
           ▼
Response Display
```

## 3. Visualization Flow

### Dashboard Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    USER ACTION                               │
│  User opens http://localhost:8000/viz                       │
└──────────────────────┬──────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────┐
│          FASTAPI SERVER (api_server.py)                      │
│                                                              │
│  GET /viz:                                                   │
│   - Serve static HTML file                                   │
│   - visualization.html loaded in browser                     │
└──────────────────────┬──────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────┐
│          BROWSER JAVASCRIPT (visualization.html)             │
│                                                              │
│  On page load:                                               │
│   1. fetch('http://localhost:8000/api/statistics')         │
│   2. fetch('http://localhost:8000/api/collections?limit=50')│
└──────────────────────┬──────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────┐
│          API ENDPOINTS (api_server.py)                       │
│                                                              │
│  GET /api/statistics:                                        │
│   1. db_manager.get_statistics()                            │
│   2. Query aggregations:                                     │
│      - SELECT content_type, COUNT(*) ... GROUP BY ...       │
│      - SELECT indexed, COUNT(*) ... GROUP BY ...            │
│      - SELECT ... WHERE date > NOW() - 7 days               │
│   3. Return JSON:                                            │
│      {                                                       │
│        by_type: {paper: 120, video: 45, podcast: 30},      │
│        indexed: 150,                                         │
│        not_indexed: 45,                                      │
│        recent_7_days: 25                                     │
│      }                                                       │
│                                                              │
│  GET /api/collections:                                       │
│   1. db_manager.get_all_collections(limit, offset)         │
│   2. Query:                                                  │
│      SELECT * FROM collections                              │
│      ORDER BY collection_date DESC                          │
│      LIMIT ? OFFSET ?                                        │
│   3. Return JSON array:                                      │
│      {                                                       │
│        count: 50,                                            │
│        collections: [{id, type, title, ...}, ...]          │
│      }                                                       │
└──────────────────────┬──────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────┐
│          JAVASCRIPT RENDERING (visualization.html)           │
│                                                              │
│  Update Statistics Cards:                                    │
│   document.getElementById('total-count').textContent = 195  │
│   document.getElementById('paper-count').textContent = 120  │
│   ...                                                        │
│                                                              │
│  Populate Data Table:                                        │
│   <table>                                                    │
│     <tr>                                                     │
│       <td>1</td>                                            │
│       <td><badge>paper</badge></td>                         │
│       <td>Attention Is All You Need</td>                    │
│       <td>arxiv</td>                                        │
│       <td><badge green>Indexed</badge></td>                 │
│       <td>2025-10-02</td>                                   │
│       <td><a href="...">View</a></td>                       │
│     </tr>                                                    │
│     ...                                                      │
│   </table>                                                   │
└─────────────────────────────────────────────────────────────┘
```

## 4. File System Data Flow

### Directory Structure and Data Storage

```
project_root/
│
├── data/
│   ├── papers/               ← PDF files downloaded
│   │   ├── 2304.05133v2.pdf
│   │   └── ...
│   │
│   ├── videos/               ← Video metadata JSON
│   │   └── (future: video files)
│   │
│   ├── podcasts/             ← Podcast audio + transcripts
│   │   └── (future: audio files)
│   │
│   ├── processed/            ← Processed documents
│   │   └── (extracted text, structured data)
│   │
│   └── collections.db        ← SQLite tracking database
│
└── logs/                     ← Application logs
    └── research_system_YYYYMMDD_HHMMSS.log
```

### File Operations Flow

1. **Paper Collection**:
   ```
   ArXiv API → Download PDF → data/papers/[arxiv_id].pdf
                             ↓
                   Record path in database
   ```

2. **Processing**:
   ```
   data/papers/[id].pdf → PDFProcessor → Extracted text
                                        ↓
                              data/processed/[id].json
   ```

3. **Database Recording**:
   ```
   All metadata → SQLite → data/collections.db
                          ↓
                 Permanent record with references to files
   ```

## Inter-Module Communication

### Module Dependencies

```
UI Layer (Gradio)
    ↓ calls
Orchestrator
    ↓ calls
┌────────────┬─────────────┬──────────────┐
│            │             │              │
▼            ▼             ▼              ▼
OpenSearch   Database   Collectors   Processors
│            │             │              │
└────────────┴─────────────┴──────────────┘
             All modules use
          Logging System (logging_config.py)
```

### Function Call Flow

```
main.py
  │
  ├─→ Initializes all components
  │   ├─→ DataCollectors (paper, video, podcast)
  │   ├─→ DataProcessors (pdf, video)
  │   ├─→ OpenSearchManager
  │   ├─→ DatabaseManager
  │   ├─→ ResearchOrchestrator
  │   ├─→ CitationTracker
  │   └─→ ResearchAssistantUI
  │
  └─→ Launches Gradio UI
       │
       └─→ User interactions trigger:
            ├─→ handle_data_collection() → Collectors → DB → Indexing
            ├─→ handle_search() → Orchestrator → OpenSearch → LLM
            ├─→ get_database_statistics() → DatabaseManager
            └─→ export_citations() → CitationTracker
```

## Data Transformation Pipeline

### Raw Data → Indexed Document

```
1. Raw Source Data
   {arxiv_id, title, authors[], abstract, pdf_url, published, categories[]}

2. Downloaded File
   data/papers/2304.05133v2.pdf

3. Processed Document
   {
     extracted_text: "Full paper text...",
     diagrams: [{description: "Architecture diagram showing..."}],
     key_concepts: ["transformers", "attention", "NLP"]
   }

4. Indexed Document
   {
     content_type: "paper",
     title: "...",
     abstract: "...",
     content: "...",
     authors: [...],
     publication_date: "2023-04-12",
     url: "https://arxiv.org/abs/2304.05133",
     embedding: [0.123, -0.456, ...],  // 384 dimensions
     metadata: {arxiv_id: "2304.05133", categories: [...]}
   }

5. Database Record
   collections: {id: 1, content_type: "paper", title: "...", indexed: true}
   papers: {id: 1, collection_id: 1, arxiv_id: "2304.05133", ...}
```

## Error Handling Flow

```
Operation Attempt
      │
      ├─→ Try: Execute operation
      │        │
      │        ├─→ Success → Log info → Continue
      │        │
      │        └─→ Exception → Catch
      │                       │
      │                       ├─→ Log error (with stack trace)
      │                       │
      │                       ├─→ Update UI with error message
      │                       │
      │                       ├─→ Graceful degradation
      │                       │   (e.g., continue with partial results)
      │                       │
      │                       └─→ Return error response
      │
      └─→ Finally: Cleanup resources
```

## Related Documentation

- [System Architecture Overview](./overview.md)
- [Module Dependencies](./dependencies.md)
- [Database Schema](../database/schema.md)
