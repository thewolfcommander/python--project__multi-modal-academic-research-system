# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Multi-Modal Academic Research System - A Python application that collects, processes, and queries academic content from multiple sources (papers, videos, podcasts) using RAG (Retrieval-Augmented Generation) with OpenSearch and Google Gemini.

## Setup and Running

### Environment Setup
1. Create virtual environment: `python -m venv venv`
2. Activate: `source venv/bin/activate` (Mac/Linux) or `venv\Scripts\activate` (Windows)
3. Install dependencies: `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and configure:
   - `GEMINI_API_KEY`: Required - Get from https://makersuite.google.com/app/apikey
   - `OPENSEARCH_HOST`: Default localhost
   - `OPENSEARCH_PORT`: Default 9200

### Running OpenSearch
OpenSearch must be running locally. Start with Docker:
```bash
docker run -p 9200:9200 -e "discovery.type=single-node" opensearchproject/opensearch:latest
```

### Starting the Application

**Main Application:**
```bash
python main.py
```
This launches a Gradio UI on `http://localhost:7860` with a public share link.

**Visualization API Server (Optional):**
```bash
python start_api_server.py
```
This starts a FastAPI server on `http://localhost:8000` for advanced data visualization and API access.

## Architecture

### Core Components

**Data Flow**: Collection → Processing → Indexing → Retrieval → Generation

1. **Data Collectors** (`multi_modal_rag/data_collectors/`)
   - `paper_collector.py`: Fetches from ArXiv, PubMed Central, Semantic Scholar
   - `youtube_collector.py`: Collects educational YouTube videos with transcripts
   - `podcast_collector.py`: Gathers podcast episodes with RSS feeds

2. **Data Processors** (`multi_modal_rag/data_processors/`)
   - `pdf_processor.py`: Extracts text and images from PDFs, uses Gemini Vision to describe diagrams
   - `video_processor.py`: Analyzes video content and transcripts with Gemini

3. **Indexing** (`multi_modal_rag/indexing/`)
   - `opensearch_manager.py`: Manages OpenSearch indices with hybrid search (keyword + semantic)
   - Uses `SentenceTransformer('all-MiniLM-L6-v2')` for embeddings (384 dimensions)
   - Supports kNN vector search combined with traditional text search

4. **Database** (`multi_modal_rag/database/`)
   - `db_manager.py`: SQLite database manager for tracking collected data
   - Stores metadata for all collected papers, videos, and podcasts
   - Tracks indexing status and collection statistics
   - Schema includes: collections, papers, videos, podcasts, collection_stats tables

5. **API** (`multi_modal_rag/api/`)
   - `api_server.py`: FastAPI server providing REST endpoints
   - Endpoints: `/api/collections`, `/api/statistics`, `/api/search`
   - Web visualization dashboard at `/viz`
   - Interactive HTML/CSS/JavaScript dashboard for data exploration

6. **Orchestration** (`multi_modal_rag/orchestration/`)
   - `research_orchestrator.py`: Main query pipeline using LangChain
     - Retrieves relevant documents via hybrid search
     - Formats context with citations
     - Generates responses using Gemini
     - Tracks conversation memory
   - `citation_tracker.py`: Manages citation tracking and bibliography export

7. **UI** (`multi_modal_rag/ui/`)
   - `gradio_app.py`: Multi-tab Gradio interface
     - Research: Query system with citation tracking
     - Data Collection: Collect content from sources
     - Citation Manager: View and export citations
     - Settings: Configure OpenSearch and API keys
     - Data Visualization: View collection statistics and data tables

### Key Design Patterns

**Hybrid Search Strategy**: The system combines keyword matching (BM25) with semantic similarity (cosine similarity on embeddings) for better retrieval quality.

**Multi-Modal Context**: Research queries pull from papers, videos, and podcasts simultaneously, with the LLM distinguishing source types in responses.

**Citation Tracking**: Citations are extracted from LLM responses using regex patterns and matched back to source documents to ensure accuracy.

**Gemini Vision Integration**: PDFs are processed to extract diagrams, which Gemini Vision analyzes to provide textual descriptions that become searchable.

**Collection Tracking**: All collected data is automatically tracked in a SQLite database with metadata, enabling visualization and analytics. The database records collection date, source, indexing status, and type-specific details.

## Data Storage

- `data/papers/`: Downloaded PDFs from academic sources
- `data/videos/`: Video metadata and transcripts
- `data/podcasts/`: Podcast episode data
- `data/processed/`: Processed content ready for indexing
- `data/collections.db`: SQLite database tracking all collected data with metadata
- `configs/`: Configuration files (currently empty)
- `logs/`: Application logs (currently empty)

## OpenSearch Index Schema

Index name: `research_assistant` (default)

Key fields:
- `content_type`: 'paper', 'video', or 'podcast'
- `title`, `abstract`, `content`, `transcript`: Text fields
- `authors`: Keyword array
- `publication_date`: Date field
- `diagram_descriptions`: Text from visual analysis
- `key_concepts`: Keyword array
- `embedding`: kNN vector (384 dimensions)
- `citations`: Nested objects with text and source

## SQLite Database Schema

Database file: `data/collections.db`

Key tables:
- `collections`: Main table tracking all collected items
  - Fields: id, content_type, title, source, url, collection_date, metadata, status, indexed
- `papers`: Paper-specific details (arxiv_id, abstract, authors, categories, pdf_path)
- `videos`: Video-specific details (video_id, channel, duration, views, thumbnail_url)
- `podcasts`: Podcast-specific details (episode_id, podcast_name, audio_url, duration)
- `collection_stats`: Collection operation statistics (content_type, query, results_count, source_api)

## Data Visualization

### Gradio UI Tab
- View collection statistics (total, by type, indexed/not indexed)
- Browse recent collections with filtering
- Export data tables
- Link to external visualization dashboard

### FastAPI Visualization Dashboard
Access at `http://localhost:8000/viz` (requires `python start_api_server.py`)

Features:
- Real-time statistics cards (total collections, by type, indexed status)
- Interactive data table with search and filtering
- Pagination for large datasets
- Content type filtering (papers, videos, podcasts)
- Direct links to source URLs
- Auto-refresh statistics

### API Endpoints
- `GET /api/collections`: List all collections (with pagination and filtering)
- `GET /api/collections/{id}`: Get detailed collection information
- `GET /api/statistics`: Get database statistics
- `GET /api/search?q={query}`: Search collections by title or source
- `GET /viz`: Web visualization dashboard
- `GET /health`: Health check endpoint
- `GET /docs`: Auto-generated API documentation (Swagger UI)

## Dependencies

Core libraries:
- **LangChain**: Orchestration framework with Google Gemini integration
- **OpenSearch**: Vector and text search
- **Gradio**: Web UI framework
- **FastAPI**: REST API framework for visualization endpoints
- **Uvicorn**: ASGI server for FastAPI
- **SQLite3**: Built-in Python database for collection tracking
- **Google Generative AI**: Gemini Pro and Gemini Vision models
- **sentence-transformers**: Embedding generation
- **PyPDF/PyMuPDF**: PDF processing
- **youtube-transcript-api**: Transcript extraction
- **arxiv**, **scholarly**: Academic paper APIs

## Common Patterns

### Adding a New Data Collector
1. Create collector in `data_collectors/`
2. Implement collection method returning List[Dict] with standard fields
3. Register in `main.py` data_collectors dict
4. Add UI option in `gradio_app.py`

### Processing New Content Types
1. Add processor in `data_processors/`
2. Extract text and visual content
3. Use Gemini to analyze and structure
4. Return Dict with fields matching OpenSearch schema

### Extending the Search
- Modify `opensearch_manager.py::hybrid_search()` query structure
- Adjust field weights in multi_match query (title^2 for higher weight)
- Add filters to the bool query

## Notes

- The system is designed for free/open-access content only
- Gemini API key is the only required external service
- OpenSearch runs locally (no cloud costs)
- Video processing is simplified - full frame extraction not implemented
- All collectors include rate limiting to be respectful of APIs
