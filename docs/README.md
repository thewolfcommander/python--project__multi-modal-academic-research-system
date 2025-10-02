# Documentation

Comprehensive documentation for the Multi-Modal Academic Research System.

## Quick Navigation

### 📚 Start Here

**[Documentation Index](DOCUMENTATION_INDEX.md)** - Complete guide to all documentation files, quick links, and common tasks.

### 📖 Module Documentation

All module documentation is located in [`docs/modules/`](modules/):

1. **[Data Collectors](modules/data-collectors.md)** (16KB)
   - Collecting papers from ArXiv, PubMed Central, Semantic Scholar
   - YouTube educational video collection with transcripts
   - Podcast episode collection from RSS feeds

2. **[Data Processors](modules/data-processors.md)** (21KB)
   - PDF text and image extraction
   - Gemini Vision for diagram analysis
   - Video content processing

3. **[Indexing](modules/indexing.md)** (25KB)
   - OpenSearch index management
   - Hybrid search (BM25 + semantic)
   - Embedding generation

4. **[Database](modules/database.md)** (24KB)
   - SQLite collection tracking
   - Statistics and analytics
   - Search and filtering

5. **[API](modules/api.md)** (22KB)
   - FastAPI REST endpoints
   - Request/response formats
   - Deployment guides

6. **[Orchestration](modules/orchestration.md)** (24KB)
   - LangChain query pipeline
   - Citation extraction and tracking
   - Bibliography export

7. **[UI](modules/ui.md)** (23KB)
   - Gradio interface
   - User workflows
   - Tab-by-tab guide

## Documentation Structure

```
docs/
├── README.md                      # This file
├── DOCUMENTATION_INDEX.md         # Complete documentation index
└── modules/
    ├── data-collectors.md        # Data collection from various sources
    ├── data-processors.md        # Content processing with Gemini
    ├── indexing.md               # OpenSearch integration
    ├── database.md               # SQLite tracking
    ├── api.md                    # FastAPI REST API
    ├── orchestration.md          # LangChain query pipeline
    └── ui.md                     # Gradio interface
```

## Getting Started

### For New Users

1. Read **[UI Documentation](modules/ui.md)** to understand the interface
2. Check **[Data Collectors](modules/data-collectors.md)** to learn about data sources
3. Explore **[Orchestration](modules/orchestration.md)** to understand how queries work

### For Developers

1. Start with **[Documentation Index](DOCUMENTATION_INDEX.md)** for architecture overview
2. Read **[Indexing](modules/indexing.md)** and **[Database](modules/database.md)** for core infrastructure
3. Study **[Data Processors](modules/data-processors.md)** for content processing pipeline
4. Review **[API](modules/api.md)** for programmatic access

### For API Users

1. Go directly to **[API Documentation](modules/api.md)**
2. Check **[Database](modules/database.md)** for data models
3. See **[Indexing](modules/indexing.md)** for search capabilities

## Key Features Documented

### Data Collection
- ✅ ArXiv papers with PDF download
- ✅ YouTube videos with transcripts
- ✅ Podcasts from RSS feeds
- ✅ Semantic Scholar integration
- ✅ PubMed Central open access

### Content Processing
- ✅ PDF text extraction (PyMuPDF)
- ✅ Image extraction from PDFs
- ✅ Gemini Vision diagram analysis
- ✅ Video transcript processing
- ✅ Multi-modal content understanding

### Search & Retrieval
- ✅ Hybrid search (keyword + semantic)
- ✅ Field boosting (title^3, abstract^2)
- ✅ Embedding generation (384-dim)
- ✅ Multi-index search
- ✅ Aggregations and analytics

### Query Pipeline
- ✅ LangChain integration
- ✅ Conversation memory
- ✅ Citation extraction
- ✅ Related query generation
- ✅ Bibliography export (BibTeX, APA)

### User Interfaces
- ✅ Gradio web UI (5 tabs)
- ✅ FastAPI REST API
- ✅ Visualization dashboard
- ✅ Collection management
- ✅ Citation tracking

## Code Examples

### Quick Start: Collect and Search

```python
from multi_modal_rag.data_collectors import AcademicPaperCollector
from multi_modal_rag.indexing import OpenSearchManager
from multi_modal_rag.orchestration import ResearchOrchestrator

# Collect papers
collector = AcademicPaperCollector()
papers = collector.collect_arxiv_papers("machine learning", max_results=10)

# Index papers
opensearch = OpenSearchManager()
for paper in papers:
    opensearch.index_document("research_assistant", {
        'content_type': 'paper',
        'title': paper['title'],
        'abstract': paper['abstract'],
        'authors': paper['authors']
    })

# Query system
orchestrator = ResearchOrchestrator("gemini_api_key", opensearch)
result = orchestrator.process_query("Explain neural networks", "research_assistant")

print(result['answer'])
```

**See**: [Documentation Index](DOCUMENTATION_INDEX.md) for more examples

## Common Tasks

### Task: Collect New Content
- **Doc**: [Data Collectors](modules/data-collectors.md)
- **UI**: [UI Module - Data Collection Tab](modules/ui.md#2-data-collection-tab)

### Task: Process PDFs with Diagrams
- **Doc**: [Data Processors](modules/data-processors.md)
- **Example**: PDFProcessor section

### Task: Search Content
- **Doc**: [Indexing](modules/indexing.md)
- **API**: [API Module - Search Endpoint](modules/api.md#get-apisearch)

### Task: Export Citations
- **Doc**: [Orchestration](modules/orchestration.md)
- **UI**: [UI Module - Citation Manager](modules/ui.md#3-citation-manager-tab)

### Task: View Statistics
- **API**: [API Module - Statistics](modules/api.md#get-apistatistics)
- **Database**: [Database Module](modules/database.md)

## Architecture Overview

### Data Flow

```
┌─────────────┐
│ Data Sources │ (ArXiv, YouTube, Podcasts)
└──────┬──────┘
       │
       ↓
┌─────────────┐
│  Collectors │ (Paper, Video, Podcast Collectors)
└──────┬──────┘
       │
       ↓
┌─────────────┐
│  Processors │ (PDF, Video Processing + Gemini)
└──────┬──────┘
       │
       ↓
┌─────────────────────┐
│ Indexing + Database │ (OpenSearch + SQLite)
└──────┬──────────────┘
       │
       ↓
┌──────────────────┐
│  Orchestration   │ (LangChain + Citations)
└──────┬───────────┘
       │
       ↓
┌──────────────────┐
│ User Interfaces  │ (Gradio UI + FastAPI)
└──────────────────┘
```

**Detailed Docs**: Each arrow documented in respective module files

### Query Pipeline

```
User Query
    ↓
Orchestrator (orchestration.md)
    ↓
OpenSearch Retrieval (indexing.md)
    ↓
Context Formatting (orchestration.md)
    ↓
Gemini Generation (orchestration.md)
    ↓
Citation Extraction (orchestration.md)
    ↓
Response + Citations + Related Queries
```

## Troubleshooting Guide

### Common Issues

| Issue | Module | Doc Section |
|-------|--------|------------|
| OpenSearch connection failed | Indexing | [Troubleshooting](modules/indexing.md#troubleshooting) |
| Gemini API errors | Data Processors | [Troubleshooting](modules/data-processors.md#troubleshooting) |
| YouTube transcript unavailable | Data Collectors | [Troubleshooting](modules/data-collectors.md#troubleshooting) |
| Database locked | Database | [Troubleshooting](modules/database.md#troubleshooting) |
| CORS errors | API | [Troubleshooting](modules/api.md#troubleshooting) |
| UI won't launch | UI | [Troubleshooting](modules/ui.md#troubleshooting) |

**Complete Guide**: [Documentation Index - Troubleshooting Index](DOCUMENTATION_INDEX.md#troubleshooting-index)

## Performance Optimization

### Quick Tips

- **Indexing**: Use bulk_index() for >10 documents → [Indexing Docs](modules/indexing.md#performance-tuning)
- **Search**: Limit results with k parameter → [Indexing Docs](modules/indexing.md#search-performance)
- **Processing**: Limit images to 5 per PDF → [Processors Docs](modules/data-processors.md#performance-optimization)
- **API**: Use pagination for large result sets → [API Docs](modules/api.md#performance-considerations)
- **UI**: Enable queuing for better responsiveness → [UI Docs](modules/ui.md#performance-considerations)

**Complete Guide**: [Documentation Index - Performance Optimization Index](DOCUMENTATION_INDEX.md#performance-optimization-index)

## API Reference

### REST Endpoints

- `GET /api/collections` - List collections → [Docs](modules/api.md#get-apicollections)
- `GET /api/collections/{id}` - Get details → [Docs](modules/api.md#get-apicollectionsid)
- `GET /api/statistics` - Statistics → [Docs](modules/api.md#get-apistatistics)
- `GET /api/search` - Search → [Docs](modules/api.md#get-apisearch)
- `GET /viz` - Dashboard → [Docs](modules/api.md#get-viz)

**Complete Reference**: [API Module Documentation](modules/api.md)

### Python API

Each module has complete Python API documentation:

- **Collectors**: [Methods](modules/data-collectors.md#methods)
- **Processors**: [Methods](modules/data-processors.md#methods)
- **Indexing**: [Methods](modules/indexing.md#methods)
- **Database**: [Methods](modules/database.md#methods)
- **Orchestrator**: [Methods](modules/orchestration.md#methods)
- **UI**: [Event Handlers](modules/ui.md#event-handler-methods)

## Dependencies

### Core Libraries

```bash
# Data Collection
pip install arxiv yt-dlp youtube-transcript-api feedparser openai-whisper

# Processing
pip install google-generativeai pypdf pymupdf pillow

# Indexing
pip install opensearch-py sentence-transformers

# Orchestration
pip install langchain langchain-google-genai

# Interfaces
pip install fastapi uvicorn gradio
```

**Detailed Info**: Each module docs has Dependencies section

## Documentation Standards

Each module documentation includes:

✅ Overview and architecture
✅ Complete class/function reference
✅ Parameters and return types
✅ Working code examples
✅ Integration patterns
✅ Error handling
✅ Performance tips
✅ Troubleshooting
✅ Dependencies

## File Sizes

| File | Size | Lines |
|------|------|-------|
| data-collectors.md | 16KB | ~550 |
| data-processors.md | 21KB | ~700 |
| indexing.md | 25KB | ~850 |
| database.md | 24KB | ~800 |
| api.md | 22KB | ~750 |
| orchestration.md | 24KB | ~800 |
| ui.md | 23KB | ~800 |
| **Total** | **155KB** | **~5,250** |

## Contributing

### Adding Documentation

1. Follow existing structure in module docs
2. Include code examples for all features
3. Add troubleshooting entries
4. Update this README with new sections
5. Update [Documentation Index](DOCUMENTATION_INDEX.md)

### Updating Documentation

1. Keep examples tested and working
2. Update related sections in other docs
3. Increment version numbers if major changes
4. Update file sizes if significantly changed

## Support

### Getting Help

1. Check relevant module documentation
2. Review [Documentation Index](DOCUMENTATION_INDEX.md) for quick links
3. Search troubleshooting sections
4. Check code examples

### Reporting Issues

For documentation issues:

1. Specify file and section
2. Describe the problem
3. Suggest improvements
4. Include code examples if applicable

## Version Information

- **Documentation Version**: 1.0
- **Last Updated**: October 2024
- **Modules Documented**: 7
- **Total Pages**: ~155KB
- **Code Examples**: 100+

---

**Quick Links**:
- [Documentation Index](DOCUMENTATION_INDEX.md)
- [Data Collectors](modules/data-collectors.md)
- [Data Processors](modules/data-processors.md)
- [Indexing](modules/indexing.md)
- [Database](modules/database.md)
- [API](modules/api.md)
- [Orchestration](modules/orchestration.md)
- [UI](modules/ui.md)
