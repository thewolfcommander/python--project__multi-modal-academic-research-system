# System Architecture Overview

## Introduction

The Multi-Modal Academic Research System is designed as a modular, scalable platform for collecting, processing, indexing, and querying academic content from multiple sources. The system leverages RAG (Retrieval-Augmented Generation) to provide intelligent responses with citations.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interfaces                          │
│  ┌─────────────────────┐         ┌──────────────────────────┐  │
│  │   Gradio Web UI     │         │  FastAPI Visualization   │  │
│  │  (Port 7860)        │         │  Dashboard (Port 8000)   │  │
│  └──────────┬──────────┘         └──────────┬───────────────┘  │
└─────────────┼──────────────────────────────┼──────────────────┘
              │                              │
              ▼                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Orchestration Layer                         │
│  ┌──────────────────────────┐   ┌──────────────────────────┐   │
│  │  Research Orchestrator   │   │   Citation Tracker       │   │
│  │  (LangChain + Gemini)    │   │   (Bibliography Export)  │   │
│  └────────────┬─────────────┘   └──────────────────────────┘   │
└───────────────┼──────────────────────────────────────────────────┘
                │
    ┌───────────┴───────────┬─────────────────┬──────────────┐
    ▼                       ▼                 ▼              ▼
┌─────────┐          ┌──────────┐      ┌──────────┐   ┌──────────┐
│ OpenSearch│          │ Database │      │Collectors│   │Processors│
│  Index   │◄─────────│ SQLite   │◄─────│  Layer   │◄──│  Layer   │
│  (Vector │          │ (Tracking)│      │          │   │          │
│  Search) │          │          │      │          │   │          │
└──────────┘          └──────────┘      └────┬─────┘   └──────────┘
                                             │
                          ┌──────────────────┼──────────────────┐
                          ▼                  ▼                  ▼
                    ┌──────────┐      ┌──────────┐      ┌──────────┐
                    │  ArXiv   │      │ YouTube  │      │ Podcasts │
                    │   API    │      │   API    │      │   RSS    │
                    └──────────┘      └──────────┘      └──────────┘
```

## Core Components

### 1. Data Collection Layer (`multi_modal_rag/data_collectors/`)

**Purpose**: Fetch raw academic content from external sources

**Components**:
- `AcademicPaperCollector`: Collects papers from ArXiv, PubMed Central, Semantic Scholar
- `YouTubeLectureCollector`: Collects educational videos with transcripts using yt-dlp
- `PodcastCollector`: Collects podcast episodes via RSS feeds

**Key Features**:
- Rate limiting to respect API quotas
- Automatic retry logic
- Metadata extraction
- Local file storage

**Dependencies**:
- External APIs (ArXiv, YouTube, RSS)
- File system for storage
- Database for tracking

### 2. Data Processing Layer (`multi_modal_rag/data_processors/`)

**Purpose**: Transform raw content into indexed, searchable format

**Components**:
- `PDFProcessor`: Extracts text and images from PDFs
  - Uses PyMuPDF for text extraction
  - Gemini Vision API for diagram analysis
- `VideoProcessor`: Analyzes video content
  - Uses Gemini for content analysis
  - Processes transcripts

**Key Features**:
- Multi-modal content extraction (text + visual)
- AI-powered diagram description
- Structured data output

**Dependencies**:
- Google Gemini API
- PyMuPDF, PyPDF libraries
- Sentence transformers

### 3. Indexing Layer (`multi_modal_rag/indexing/`)

**Purpose**: Store and retrieve content efficiently

**Component**: `OpenSearchManager`

**Key Features**:
- **Hybrid Search**: Combines keyword (BM25) + semantic (kNN vector) search
- **Embedding Generation**: Uses SentenceTransformer (all-MiniLM-L6-v2, 384 dimensions)
- **Schema Management**: Creates and manages indices
- **Bulk Operations**: Efficient batch indexing

**Search Strategy**:
1. Convert query to embedding vector
2. Perform multi-match text search with field boosting
3. Combine scores for ranking
4. Return top-k results

**Dependencies**:
- OpenSearch (Docker or local instance)
- sentence-transformers library

### 4. Database Layer (`multi_modal_rag/database/`)

**Purpose**: Track all collected data with metadata

**Component**: `CollectionDatabaseManager`

**Schema**:
- `collections`: Main table (id, type, title, source, url, status, indexed)
- `papers`: Paper-specific details (arxiv_id, abstract, authors, categories)
- `videos`: Video-specific details (video_id, channel, views, duration)
- `podcasts`: Podcast-specific details (episode_id, audio_url)
- `collection_stats`: Collection operation statistics

**Key Features**:
- Automatic tracking on collection
- Indexing status management
- Query history and statistics
- Metadata preservation

**Dependencies**:
- SQLite3 (built-in Python)

### 5. Orchestration Layer (`multi_modal_rag/orchestration/`)

**Purpose**: Coordinate research queries and generate responses

**Components**:

**a) `ResearchOrchestrator`**:
- Processes user queries
- Retrieves relevant documents from OpenSearch
- Uses LangChain + Gemini to generate responses
- Maintains conversation memory
- Provides source citations

**Query Flow**:
```
User Query → Hybrid Search → Document Retrieval → Context Formation
    ↓
Gemini LLM Processing → Response Generation → Citation Extraction
    ↓
Formatted Response + Sources
```

**b) `CitationTracker`**:
- Extracts citations from LLM responses
- Matches citations to source documents
- Tracks citation usage statistics
- Exports bibliographies (BibTeX, APA, JSON)

**Dependencies**:
- LangChain framework
- Google Gemini API
- OpenSearchManager

### 6. API Layer (`multi_modal_rag/api/`)

**Purpose**: Provide REST API and visualization interface

**Component**: `FastAPI Server`

**Endpoints**:
- `GET /api/collections`: List all collections
- `GET /api/collections/{id}`: Get collection details
- `GET /api/statistics`: Database statistics
- `GET /api/search`: Search collections
- `GET /viz`: Interactive visualization dashboard
- `GET /docs`: Auto-generated API docs

**Key Features**:
- CORS-enabled for web access
- Pagination support
- Real-time statistics
- Interactive HTML dashboard

**Dependencies**:
- FastAPI framework
- Uvicorn ASGI server
- Database layer

### 7. User Interface Layer (`multi_modal_rag/ui/`)

**Purpose**: Provide user-friendly web interface

**Component**: `ResearchAssistantUI` (Gradio)

**Tabs**:
1. **Research**: Query system, view answers with citations
2. **Data Collection**: Collect papers/videos/podcasts
3. **Citation Manager**: View and export citations
4. **Settings**: Configure OpenSearch, API keys
5. **Data Visualization**: View collection statistics

**Key Features**:
- Real-time collection status
- Citation formatting
- Statistics dashboard
- Index management

**Dependencies**:
- Gradio framework
- All backend modules

## Data Flow

### Collection Flow

```
1. User initiates collection (via Gradio UI)
   ↓
2. Collector fetches data from external API
   ↓
3. Raw data saved to local storage (data/papers, data/videos, data/podcasts)
   ↓
4. Metadata recorded in SQLite database
   ↓
5. Processor extracts and structures content
   ↓
6. Document indexed in OpenSearch with embeddings
   ↓
7. Collection marked as "indexed" in database
```

### Query Flow

```
1. User submits research query (via Gradio UI)
   ↓
2. ResearchOrchestrator receives query
   ↓
3. Hybrid search performed on OpenSearch
   ↓
4. Top-k relevant documents retrieved
   ↓
5. Documents formatted as context for LLM
   ↓
6. Gemini generates response with citations
   ↓
7. Citations extracted and tracked
   ↓
8. Response displayed to user with sources
```

### Visualization Flow

```
1. User accesses visualization dashboard
   ↓
2. FastAPI endpoint queries SQLite database
   ↓
3. Statistics aggregated and formatted
   ↓
4. JSON response sent to frontend
   ↓
5. JavaScript renders interactive charts/tables
```

## Design Principles

### 1. Modularity
Each component has a single, well-defined responsibility and can operate independently.

### 2. Separation of Concerns
- Collection ≠ Processing ≠ Indexing
- Each layer has distinct interfaces

### 3. Scalability
- Bulk operations for efficiency
- Stateless API design
- Database-backed persistence

### 4. Extensibility
- Plugin architecture for new collectors
- Configurable search strategies
- Customizable UI tabs

### 5. Resilience
- Graceful degradation (e.g., works without OpenSearch)
- Comprehensive error handling
- Detailed logging

### 6. Free/Open Technologies
- Local OpenSearch (Docker)
- SQLite (built-in)
- Free APIs (ArXiv, YouTube)
- Open-source libraries

## Technology Choices

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Search Engine | OpenSearch | Open-source, supports vector search, BM25 |
| Vector Embeddings | SentenceTransformers | Fast, local, no API costs |
| LLM | Google Gemini | Free tier, multimodal, good quality |
| Database | SQLite | Zero-config, serverless, embedded |
| API Framework | FastAPI | Fast, auto-docs, type hints |
| UI Framework | Gradio | Rapid prototyping, Python-native |
| PDF Processing | PyMuPDF | Fast, accurate text extraction |
| Video Metadata | yt-dlp | Robust, actively maintained |

## Security Considerations

1. **API Keys**: Stored in `.env` file, never committed to git
2. **OpenSearch**: Local-only deployment by default
3. **CORS**: Configured for localhost only in production
4. **Input Validation**: All API endpoints validate inputs
5. **SQL Injection**: Prevented via parameterized queries

## Performance Characteristics

- **Indexing Speed**: ~10-50 documents/second (bulk)
- **Query Latency**: ~1-3 seconds (including LLM)
- **Embedding Generation**: ~50ms per document
- **Database Queries**: <10ms for most operations
- **Storage**: ~1MB per paper (PDF + metadata + embeddings)

## Future Enhancements

1. **Distributed Search**: Multi-node OpenSearch cluster
2. **Caching Layer**: Redis for frequently accessed data
3. **Background Workers**: Celery for async processing
4. **Advanced Analytics**: Time-series analysis of collection trends
5. **Collaborative Features**: Shared collections, annotations
6. **Mobile Interface**: Responsive UI for mobile devices

## Related Documentation

- [Data Flow Diagram](./data-flow.md)
- [Module Dependencies](./dependencies.md)
- [Technology Stack Details](./technology-stack.md)
