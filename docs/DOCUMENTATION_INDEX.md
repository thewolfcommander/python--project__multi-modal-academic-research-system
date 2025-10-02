# Multi-Modal Academic Research System - Documentation Index

## Overview

Comprehensive documentation for all modules in the Multi-Modal Academic Research System. This index provides quick access to detailed module documentation with code examples, API references, and integration guides.

---

## Documentation Files

### 1. Data Collectors Module
**File**: [`docs/modules/data-collectors.md`](modules/data-collectors.md) (16KB)

**Key Sections**:
- **AcademicPaperCollector**
  - `collect_arxiv_papers()` - Collect from ArXiv with PDF download
  - `collect_pubmed_central()` - PubMed Central Open Access papers
  - `collect_semantic_scholar()` - Semantic Scholar API integration

- **YouTubeLectureCollector**
  - `search_youtube_lectures()` - Search educational videos
  - `collect_video_metadata()` - Extract metadata and transcripts
  - `extract_video_id()` - Parse YouTube URLs

- **PodcastCollector**
  - `collect_podcast_episodes()` - RSS feed parsing
  - `transcribe_audio()` - Whisper-based transcription
  - `get_educational_podcasts()` - Curated podcast list

**Topics Covered**:
- API integration examples (ArXiv, YouTube, RSS)
- Rate limiting and best practices
- Error handling patterns
- Complete code examples for each collector
- Troubleshooting common issues

---

### 2. Data Processors Module
**File**: [`docs/modules/data-processors.md`](modules/data-processors.md) (21KB)

**Key Sections**:
- **PDFProcessor**
  - `extract_text_and_images()` - PyMuPDF-based extraction
  - `analyze_with_gemini()` - AI-powered content analysis
  - Gemini Vision for diagram understanding

- **VideoProcessor**
  - `analyze_video_content()` - Transcript and metadata analysis
  - `extract_key_frames()` - Frame extraction (placeholder)

**Topics Covered**:
- PDF text and image extraction with PyMuPDF
- Gemini Vision integration for diagrams
- Multimodal AI prompts and responses
- Document structuring for indexing
- Performance optimization tips
- Gemini SDK usage patterns

---

### 3. Indexing Module
**File**: [`docs/modules/indexing.md`](modules/indexing.md) (25KB)

**Key Sections**:
- **OpenSearchManager**
  - `create_index()` - Index schema creation
  - `index_document()` - Single document indexing
  - `bulk_index()` - Efficient batch indexing
  - `hybrid_search()` - Multi-field text search

**Topics Covered**:
- Index schema design for multi-modal content
- Embedding generation with SentenceTransformer
- Hybrid search strategy (BM25 + vector search)
- Field boosting and relevance tuning
- Performance optimization
- Advanced search queries and aggregations
- kNN vector search concepts

---

### 4. Database Module
**File**: [`docs/modules/database.md`](modules/database.md) (24KB)

**Key Sections**:
- **CollectionDatabaseManager**
  - `add_collection()` - Track new collections
  - `add_paper()`, `add_video()`, `add_podcast()` - Type-specific data
  - `mark_as_indexed()` - Update indexing status
  - `get_statistics()` - Analytics and reporting
  - `search_collections()` - Database search

**Topics Covered**:
- Complete database schema (SQLite)
- CRUD operations for all content types
- Collection statistics and analytics
- Search and filtering
- Data export (JSON, CSV)
- Performance considerations
- Backup and recovery

---

### 5. API Module
**File**: [`docs/modules/api.md`](modules/api.md) (22KB)

**Key Sections**:
- **FastAPI Endpoints**
  - `GET /api/collections` - Retrieve collections with filtering
  - `GET /api/collections/{id}` - Get collection details
  - `GET /api/statistics` - Database statistics
  - `GET /api/search` - Search collections
  - `GET /viz` - Visualization dashboard
  - `GET /health` - Health check

**Topics Covered**:
- Complete REST API reference
- Request/response formats
- Query parameters and validation
- Error handling and status codes
- CORS configuration
- Frontend integration examples (React, Python)
- CLI tool example
- Deployment guides (Docker, Kubernetes)
- Security considerations

---

### 6. Orchestration Module
**File**: [`docs/modules/orchestration.md`](modules/orchestration.md) (24KB)

**Key Sections**:
- **ResearchOrchestrator**
  - `process_query()` - End-to-end query pipeline
  - `format_context_with_citations()` - Context formatting
  - `extract_citations()` - Citation extraction from responses
  - `generate_related_queries()` - Suggestion generation

- **CitationTracker**
  - `add_citation()` - Track citation usage
  - `get_citation_report()` - Analytics
  - `export_bibliography()` - BibTeX/APA export

**Topics Covered**:
- LangChain integration patterns
- Prompt engineering for research
- Citation extraction with regex
- Conversation memory management
- Related query generation
- Bibliography export formats
- Multi-turn conversations

---

### 7. UI Module
**File**: [`docs/modules/ui.md`](modules/ui.md) (23KB)

**Key Sections**:
- **ResearchAssistantUI**
  - `create_interface()` - Gradio app creation
  - `handle_search()` - Research query processing
  - `handle_data_collection()` - Content collection workflow
  - `get_database_statistics()` - Statistics display

**Topics Covered**:
- Complete Gradio interface guide
- 5 main tabs (Research, Data Collection, Citation Manager, Settings, Visualization)
- Event handlers and workflows
- UI customization and theming
- Launch configurations
- User workflows and examples
- Performance optimization
- Accessibility features

---

## Quick Start Guide

### 1. Reading Order for New Users

1. **Start with**: `data-collectors.md` - Understand data sources
2. **Then**: `data-processors.md` - Learn content processing
3. **Next**: `indexing.md` - Understand search infrastructure
4. **Follow with**: `orchestration.md` - See how queries work
5. **Finally**: `ui.md` - Explore the user interface

### 2. Reading Order for Developers

1. **Architecture**: `indexing.md` + `database.md` - Core infrastructure
2. **Data Flow**: `data-collectors.md` → `data-processors.md` → `indexing.md`
3. **Query Pipeline**: `orchestration.md` - LangChain integration
4. **Interfaces**: `ui.md` + `api.md` - User/programmatic access

### 3. Reading Order for API Users

1. **API Reference**: `api.md` - REST endpoints
2. **Data Structure**: `database.md` - Schema and models
3. **Search**: `indexing.md` - Query capabilities
4. **Integration**: Examples in `api.md`

---

## Code Examples Index

### Data Collection Examples

```python
# Collect papers from ArXiv
from multi_modal_rag.data_collectors import AcademicPaperCollector

collector = AcademicPaperCollector()
papers = collector.collect_arxiv_papers("machine learning", max_results=50)
```
**See**: `data-collectors.md` - Section: AcademicPaperCollector

### PDF Processing Examples

```python
# Extract and analyze PDF
from multi_modal_rag.data_processors import PDFProcessor

processor = PDFProcessor(gemini_api_key="your_key")
content = processor.extract_text_and_images("paper.pdf")
analysis = processor.analyze_with_gemini(content)
```
**See**: `data-processors.md` - Section: PDFProcessor

### Search Examples

```python
# Hybrid search
from multi_modal_rag.indexing import OpenSearchManager

manager = OpenSearchManager()
results = manager.hybrid_search("research_assistant", "transformers", k=10)
```
**See**: `indexing.md` - Section: hybrid_search()

### Research Query Examples

```python
# Process research query
from multi_modal_rag.orchestration import ResearchOrchestrator

orchestrator = ResearchOrchestrator(api_key, opensearch_manager)
result = orchestrator.process_query("How do transformers work?", "research_assistant")
```
**See**: `orchestration.md` - Section: process_query()

### API Usage Examples

```python
# Fetch collections via API
import requests

response = requests.get("http://localhost:8000/api/collections?content_type=paper")
papers = response.json()['collections']
```
**See**: `api.md` - Section: GET /api/collections

---

## Integration Patterns

### Complete Pipeline Example

Location in docs:
- Collection: `data-collectors.md` - Integration Example section
- Processing: `data-processors.md` - Integration Workflow section
- Indexing: `indexing.md` - Usage examples
- Querying: `orchestration.md` - Complete Research Workflow section

### UI Integration

Location: `ui.md` - Section: Integration with Main Application

Example: `main.py` setup connecting all components

### API Integration

Location: `api.md` - Section: Integration Examples

Examples: React frontend, Python client, CLI tool

---

## Architecture Diagrams

### Data Flow

```
Data Sources → Collectors → Processors → Indexing → Search
                                ↓
                          Database Tracking
```

**Detailed docs**:
- Collectors: `data-collectors.md`
- Processors: `data-processors.md`
- Indexing: `indexing.md`
- Database: `database.md`

### Query Pipeline

```
User Query → Orchestrator → OpenSearch → Context Formatting
                ↓                              ↓
            Memory ←─────── Gemini LLM ←───────┘
                ↓
         Citation Extraction
```

**Detailed docs**:
- Orchestrator: `orchestration.md`
- Search: `indexing.md`
- Citations: `orchestration.md` - CitationTracker section

---

## Common Tasks

### Task: Collect and Index Papers

**Docs**:
1. `data-collectors.md` - collect_arxiv_papers()
2. `indexing.md` - bulk_index()
3. `database.md` - add_collection()

### Task: Process PDF with Diagram Analysis

**Docs**:
1. `data-processors.md` - extract_text_and_images()
2. `data-processors.md` - analyze_with_gemini()

### Task: Build Custom Search Interface

**Docs**:
1. `indexing.md` - hybrid_search()
2. `api.md` - Frontend Integration
3. `orchestration.md` - process_query()

### Task: Export Citations

**Docs**:
1. `orchestration.md` - CitationTracker
2. `orchestration.md` - export_bibliography()

### Task: Deploy API Server

**Docs**:
1. `api.md` - Deployment section
2. `api.md` - Docker Deployment

---

## Troubleshooting Index

### By Module

- **Data Collectors**: `data-collectors.md` - Troubleshooting section
  - yt-dlp not found
  - YouTube transcript unavailable
  - RSS feed parsing fails

- **Data Processors**: `data-processors.md` - Troubleshooting section
  - Gemini API authentication
  - PDF extraction errors
  - Image analysis failures

- **Indexing**: `indexing.md` - Troubleshooting section
  - OpenSearch connection refused
  - SSL certificate errors
  - Search returns no results

- **Database**: `database.md` - Troubleshooting section
  - Database locked errors
  - Corrupted database recovery
  - JSON parse errors

- **API**: `api.md` - Troubleshooting section
  - Port already in use
  - CORS errors
  - 422 validation errors

- **Orchestration**: `orchestration.md` - Troubleshooting section
  - Related queries not JSON
  - Citations not extracted
  - Memory grows too large

- **UI**: `ui.md` - Troubleshooting section
  - Gradio won't launch
  - Share link doesn't work
  - UI freezes during collection

---

## Performance Optimization Index

### Indexing Performance

**Doc**: `indexing.md` - Performance Tuning section

Key topics:
- Bulk indexing vs single documents
- Batch embedding generation
- Shard configuration
- Query optimization

### Search Performance

**Doc**: `indexing.md` - Search Performance section

Key topics:
- Result size limits
- Filter optimization
- Field selection
- Caching strategies

### Processing Performance

**Doc**: `data-processors.md` - Performance Optimization section

Key topics:
- Image limit (5 max)
- Batch processing
- Result caching
- Transcript truncation

### UI Performance

**Doc**: `ui.md` - Performance Considerations section

Key topics:
- Loading states
- Result display limits
- Async operations
- Queue management

---

## Security Best Practices

### API Security

**Doc**: `api.md` - Security Considerations section

Topics:
- CORS configuration
- API authentication
- Rate limiting
- HTTPS deployment

### Database Security

**Doc**: `database.md` - Error Handling section

Topics:
- Transaction safety
- SQL injection prevention
- Backup strategies

---

## Dependencies Summary

### Core Dependencies

| Module | Key Dependencies | Doc Reference |
|--------|-----------------|---------------|
| Data Collectors | arxiv, yt-dlp, feedparser, whisper | `data-collectors.md` |
| Data Processors | google-generativeai, pypdf, pymupdf | `data-processors.md` |
| Indexing | opensearch-py, sentence-transformers | `indexing.md` |
| Database | sqlite3 (built-in) | `database.md` |
| API | fastapi, uvicorn | `api.md` |
| Orchestration | langchain, langchain-google-genai | `orchestration.md` |
| UI | gradio | `ui.md` |

### Installation Commands

```bash
# All dependencies
pip install -r requirements.txt

# By module (see individual docs for details)
pip install arxiv yt-dlp youtube-transcript-api feedparser openai-whisper
pip install google-generativeai pypdf pymupdf pillow
pip install opensearch-py sentence-transformers
pip install fastapi uvicorn
pip install langchain langchain-google-genai
pip install gradio
```

---

## API Reference Quick Links

### REST Endpoints

- `GET /` - API info → `api.md`
- `GET /api/collections` - List collections → `api.md`
- `GET /api/collections/{id}` - Get details → `api.md`
- `GET /api/statistics` - Statistics → `api.md`
- `GET /api/search` - Search → `api.md`
- `GET /viz` - Dashboard → `api.md`
- `GET /health` - Health check → `api.md`

### Python API

- **Collectors**: `data-collectors.md` - Methods section
- **Processors**: `data-processors.md` - Methods section
- **Indexing**: `indexing.md` - Methods section
- **Database**: `database.md` - Methods section
- **Orchestrator**: `orchestration.md` - Methods section
- **UI**: `ui.md` - Event Handler Methods section

---

## File Sizes

- `data-collectors.md`: 16KB
- `data-processors.md`: 21KB
- `indexing.md`: 25KB
- `database.md`: 24KB
- `api.md`: 22KB
- `orchestration.md`: 24KB
- `ui.md`: 23KB

**Total**: 155KB of comprehensive documentation

---

## Documentation Standards

Each documentation file includes:

1. **Overview** - Module purpose and architecture
2. **Class/Function Reference** - Complete API documentation
3. **Parameters & Returns** - Detailed type information
4. **Code Examples** - Working examples for all features
5. **Integration Examples** - How modules work together
6. **Error Handling** - Common errors and solutions
7. **Performance Tips** - Optimization strategies
8. **Troubleshooting** - Common issues and fixes
9. **Dependencies** - Required packages
10. **Future Enhancements** - Planned features

---

## Contributing to Documentation

When updating documentation:

1. Follow existing structure and format
2. Include code examples for all new features
3. Add troubleshooting entries for common issues
4. Update this index with new sections
5. Keep examples tested and working
6. Update file sizes if significantly changed

---

## Feedback and Issues

For documentation improvements or corrections:

1. Create issue with `documentation` label
2. Specify file and section
3. Provide suggested changes
4. Include code examples if applicable

---

**Last Updated**: October 2024
**Documentation Version**: 1.0
**Total Modules Documented**: 7
