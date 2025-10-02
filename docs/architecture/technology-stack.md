# Technology Stack

Comprehensive documentation of all technologies, libraries, and frameworks used in the Multi-Modal Academic Research System.

## Table of Contents

- [Overview](#overview)
- [Core Technologies](#core-technologies)
- [AI and Machine Learning](#ai-and-machine-learning)
- [Search and Vector Database](#search-and-vector-database)
- [Data Collection and Processing](#data-collection-and-processing)
- [Web Framework and UI](#web-framework-and-ui)
- [Supporting Libraries](#supporting-libraries)
- [Development Tools](#development-tools)
- [Version Compatibility](#version-compatibility)
- [Architecture Decisions](#architecture-decisions)
- [Alternative Technologies Considered](#alternative-technologies-considered)

---

## Overview

The Multi-Modal Academic Research System is built on a modern Python stack, leveraging state-of-the-art AI models, vector search capabilities, and a user-friendly web interface. The technology choices prioritize:

- **Free and Open Source**: Minimize costs, maximize accessibility
- **Local-First**: Data and processing remain on your machine
- **Modern AI**: Latest language models and embedding techniques
- **Scalability**: Capable of handling thousands of documents
- **Ease of Use**: Simple installation and intuitive interface

---

## Core Technologies

### Python 3.9+

**Version**: 3.9+ (3.11 recommended)

**Why Python**:
- Rich ecosystem for AI/ML and data processing
- Extensive libraries for academic data collection
- Strong community support
- Easy integration with modern AI APIs
- Excellent for rapid prototyping and development

**Why Python 3.9+**:
- Type hints support (PEP 585, 604)
- Dictionary merge operators
- String methods improvements
- Required for modern dependency versions

**Official**: https://www.python.org/

---

## AI and Machine Learning

### 1. Google Gemini (google-generativeai 0.7.2)

**Purpose**: AI-powered text generation and vision analysis

**Why Gemini**:
- Free tier available (no credit card required)
- State-of-the-art multimodal capabilities
- Excellent for academic content analysis
- Vision API for diagram understanding
- Competitive with GPT-4 in many tasks
- Lower latency than other commercial APIs

**Models Used**:
- **Gemini 1.5 Pro** (`gemini-1.5-pro-latest`):
  - Research query responses
  - Text synthesis and analysis
  - Citation generation
  - Context window: 1M tokens

- **Gemini 1.5 Flash** (`gemini-1.5-flash`):
  - PDF diagram analysis
  - Image description
  - Faster, lower cost for vision tasks

**Alternatives Considered**:
- OpenAI GPT-4: Higher cost, requires payment
- Anthropic Claude: Limited free tier
- Local models (LLaMA): Higher compute requirements

**Official**: https://ai.google.dev/

---

### 2. LangChain (0.2.16)

**Purpose**: AI orchestration and prompt management framework

**Why LangChain**:
- Industry-standard for LLM applications
- Built-in memory management for conversations
- Excellent prompt templating
- Easy integration with multiple LLM providers
- Strong community and documentation
- Modular architecture for extensibility

**Key Features Used**:
- `ChatGoogleGenerativeAI`: Gemini integration
- `ConversationBufferWindowMemory`: Conversation tracking
- `PromptTemplate`: Structured prompts for research queries
- Chain composition for multi-step reasoning

**LangChain Google GenAI (1.0.10)**:
- Official LangChain integration for Google's AI
- Seamless Gemini model support
- Streaming responses
- Function calling support

**Alternatives Considered**:
- Direct API calls: More work, less abstraction
- LlamaIndex: Different focus (more on indexing)
- Haystack: Less mature Gemini integration

**Official**: https://python.langchain.com/

---

### 3. Sentence Transformers (2.7.0)

**Purpose**: Generate semantic embeddings for vector search

**Why Sentence Transformers**:
- State-of-the-art semantic similarity models
- Fast inference on CPU
- Excellent for retrieval tasks
- Easy to use and well-documented
- Large collection of pre-trained models
- Active development and updates

**Model Used**: `all-MiniLM-L6-v2`
- Dimensions: 384
- Speed: ~14,000 sentences/second (CPU)
- Performance: Excellent quality/speed tradeoff
- Size: ~90MB download
- Best for: Semantic search in medium-large corpora

**Why all-MiniLM-L6-v2**:
- Optimal balance of speed and quality
- Small embedding size (384d) = lower storage
- Fast retrieval with k-NN search
- Good performance on academic text
- Widely used and battle-tested

**Alternative Models Available**:
- `all-mpnet-base-v2`: Higher quality (768d), slower
- `all-MiniLM-L12-v2`: Similar size, slightly better quality
- `multi-qa-mpnet-base-dot-v1`: Optimized for Q&A tasks

**Official**: https://www.sbert.net/

---

## Search and Vector Database

### OpenSearch (opensearch-py 2.4.0)

**Purpose**: Vector database, full-text search, and document indexing

**Why OpenSearch**:
- **Open source**: Fork of Elasticsearch, Apache 2.0 license
- **Free to use**: No licensing costs
- **Hybrid search**: Combines keyword (BM25) and vector (k-NN) search
- **Scalable**: Handles millions of documents
- **Feature-rich**: Aggregations, filtering, faceting
- **Local deployment**: Runs on your machine, full control
- **Active development**: AWS-backed, regular updates

**Key Features Used**:

1. **k-NN Vector Search**:
   - 384-dimensional embeddings
   - Cosine similarity for semantic matching
   - Fast approximate nearest neighbors

2. **Full-Text Search**:
   - BM25 ranking algorithm
   - Multi-field queries
   - Field boosting (title^2)

3. **Hybrid Search**:
   - Combines keyword and vector results
   - Best of both worlds: precise and semantic
   - Configurable weighting

4. **Index Management**:
   - Custom mappings for multi-modal content
   - Nested objects for citations
   - Keyword arrays for metadata

**Schema Design**:
```python
{
    'content_type': 'keyword',      # paper/video/podcast
    'title': 'text',                # Searchable title
    'abstract': 'text',             # Paper abstract
    'content': 'text',              # Main content
    'authors': 'keyword',           # Author list
    'publication_date': 'date',     # Temporal filtering
    'embedding': 'knn_vector',      # 384-dim semantic vector
    'diagram_descriptions': 'text', # From Gemini Vision
    'key_concepts': 'keyword',      # Extracted concepts
    'citations': 'nested'           # Citation tracking
}
```

**Deployment**: Docker container for local development
```bash
docker run -p 9200:9200 -e "discovery.type=single-node" \
  opensearchproject/opensearch:latest
```

**Alternatives Considered**:
- **Elasticsearch**: Proprietary license, OpenSearch is the open fork
- **Pinecone**: Cloud-only, costs money, less control
- **Weaviate**: Good but more complex setup
- **Qdrant**: Excellent but newer, smaller ecosystem
- **ChromaDB**: Included but not primary (simpler use cases)
- **FAISS**: No full-text search, just vectors
- **Milvus**: More complex, higher overhead

**Why Not ChromaDB**:
- Included in dependencies (`chromadb==0.4.20`)
- Could be used for simpler deployments
- OpenSearch chosen for hybrid search capabilities
- ChromaDB better for pure vector search

**Official**: https://opensearch.org/

---

## Data Collection and Processing

### Academic Data Sources

#### 1. ArXiv (arxiv 2.0.0)

**Purpose**: Collect papers from ArXiv preprint server

**Why ArXiv**:
- Largest open-access preprint repository
- Covers CS, physics, math, and more
- Free API, no authentication required
- Rich metadata (authors, abstract, categories)
- Direct PDF download links

**Usage**:
```python
from arxiv import Search, Client
client.search(query="machine learning", max_results=10)
```

**Official**: https://arxiv.org/

---

#### 2. Scholarly (1.7.11)

**Purpose**: Collect papers from Google Scholar and Semantic Scholar

**Why Scholarly**:
- Access to Google Scholar's vast database
- Semantic Scholar integration
- Citation information
- No API key required (uses scraping)
- Author profiles and metrics

**Limitations**:
- Rate limiting required (avoid IP bans)
- May need proxies for heavy use
- Less reliable than official APIs

**Usage**:
```python
from scholarly import scholarly
search = scholarly.search_pubs('deep learning')
```

**Official**: https://github.com/scholarly-python-package/scholarly

---

#### 3. YouTube Transcript API (youtube-transcript-api 0.6.1)

**Purpose**: Extract transcripts from educational YouTube videos

**Why YouTube Transcript API**:
- Free and no API key required
- Accesses official YouTube transcripts
- Supports multiple languages
- Auto-generated and manual captions
- Timestamp information

**Usage**:
```python
from youtube_transcript_api import YouTubeTranscriptApi
transcript = YouTubeTranscriptApi.get_transcript(video_id)
```

**Alternatives**:
- YouTube Data API v3: Requires API key, quota limits
- pytube (0.15.0): Video metadata extraction
- yt-dlp (2024.3.10): Alternative downloader

**Official**: https://github.com/jdepoix/youtube-transcript-api

---

#### 4. Feedparser (6.0.10)

**Purpose**: Parse RSS/Atom feeds for podcast collection

**Why Feedparser**:
- Universal feed parser (RSS, Atom, RDF)
- Robust and battle-tested
- Handles malformed feeds gracefully
- Extract episode metadata
- Widely used and maintained

**Usage**:
```python
import feedparser
feed = feedparser.parse('https://podcast.rss.url')
```

**Official**: https://feedparser.readthedocs.io/

---

### Document Processing

#### 1. PyPDF (pypdf 3.17.0)

**Purpose**: Extract text and metadata from PDF files

**Why PyPDF**:
- Pure Python, no external dependencies
- Actively maintained (formerly PyPDF2)
- Good text extraction
- PDF metadata parsing
- Page-by-page processing

**Limitations**:
- May struggle with complex layouts
- Scanned PDFs need OCR

**Official**: https://pypdf.readthedocs.io/

---

#### 2. PyMuPDF (1.23.8)

**Purpose**: Advanced PDF processing and image extraction

**Why PyMuPDF (fitz)**:
- Fast C-based implementation
- Excellent image extraction
- Better handling of complex PDFs
- Page rendering capabilities
- Extract diagrams and figures

**Why Both PyPDF and PyMuPDF**:
- Fallback mechanism: Try PyMuPDF first, fallback to PyPDF
- Different PDFs work better with different libraries
- Maximize successful text extraction

**Usage**:
```python
import fitz  # PyMuPDF
doc = fitz.open("paper.pdf")
images = doc[page_num].get_images()
```

**Official**: https://pymupdf.readthedocs.io/

---

#### 3. Whisper (1.1.10)

**Purpose**: Audio transcription for videos and podcasts

**Why Whisper**:
- State-of-the-art speech recognition
- Multilingual support (99 languages)
- Open source from OpenAI
- Works offline (local processing)
- High accuracy on academic content

**Models**:
- `tiny`, `base`: Fast, lower accuracy
- `small`, `medium`: Balanced
- `large`: Best accuracy, slower

**Note**: Currently included but not fully integrated. YouTube uses existing transcripts.

**Official**: https://github.com/openai/whisper

---

## Web Framework and UI

### Gradio (4.8.0)

**Purpose**: Web-based user interface

**Why Gradio**:
- **Rapid development**: Build UIs in minutes
- **Beautiful defaults**: Professional look out of the box
- **Multi-tab support**: Organize complex applications
- **Real-time updates**: Live feedback during processing
- **Share functionality**: Create public URLs instantly
- **Python-native**: No JavaScript required
- **FastAPI integration**: Built on modern async framework

**Key Features Used**:
- Tabbed interface (Research, Data Collection, Citations, Settings)
- Text input/output components
- Buttons and interactive elements
- Real-time status updates
- File upload capabilities
- Markdown rendering for responses

**UI Structure**:
```python
with gr.Blocks() as app:
    with gr.Tab("Research"):
        # Query interface
    with gr.Tab("Data Collection"):
        # Collection controls
    with gr.Tab("Citation Manager"):
        # Citation export
    with gr.Tab("Settings"):
        # System configuration
```

**Why Gradio over alternatives**:
- **Streamlit**: Less flexible layout, page reloads
- **Dash**: More complex, steeper learning curve
- **Flask/FastAPI**: Would require frontend development
- **Jupyter**: Not ideal for production deployment

**FastAPI (0.109.0) + Uvicorn (0.27.0)**:
- Gradio runs on FastAPI (modern async framework)
- Uvicorn is the ASGI server
- High performance, async support
- Easy to extend with custom API endpoints

**Official**: https://gradio.app/

---

## Supporting Libraries

### 1. Python-dotenv (1.0.0)

**Purpose**: Environment variable management

**Why python-dotenv**:
- Load `.env` files automatically
- Keep secrets out of code
- Easy configuration management
- Development/production separation

**Usage**:
```python
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')
```

---

### 2. Requests (2.31.0)

**Purpose**: HTTP client for API calls

**Why Requests**:
- De facto standard for HTTP in Python
- Simple, elegant API
- Robust error handling
- Session management
- Wide adoption and support

---

### 3. BeautifulSoup4 (4.12.2)

**Purpose**: HTML and XML parsing

**Why BeautifulSoup**:
- Intuitive API for parsing HTML
- Robust handling of malformed HTML
- Multiple parser backends
- Used for web scraping when APIs unavailable

---

### 4. Pandas (2.1.3)

**Purpose**: Data manipulation and analysis

**Why Pandas**:
- DataFrame structure for tabular data
- Easy data transformation
- CSV export capabilities
- Integration with other tools
- Citation export and management

---

### 5. NumPy (>=1.25.2, <2.0)

**Purpose**: Numerical computing foundation

**Why NumPy**:
- Dependency for many libraries (Pandas, Sentence Transformers)
- Array operations for embeddings
- Mathematical computations
- Version <2.0 for compatibility

---

### 6. tqdm (4.66.1)

**Purpose**: Progress bars for long operations

**Why tqdm**:
- Visual feedback during collection/processing
- Works in terminal and notebooks
- Minimal overhead
- Easy integration

---

### 7. Pydub (0.25.1)

**Purpose**: Audio processing and manipulation

**Why Pydub**:
- Simple API for audio operations
- Format conversion
- Audio segmentation
- Required for Whisper integration

---

### 8. yt-dlp (2024.3.10)

**Purpose**: YouTube video metadata extraction

**Why yt-dlp**:
- Active fork of youtube-dl
- Regular updates for YouTube changes
- Robust error handling
- Alternative to pytube
- More reliable than pytube

---

## Development Tools

### Version Control
- **Git**: Source control and collaboration
- **.gitignore**: Excludes venv, .env, data, logs

### Virtual Environment
- **venv**: Isolate project dependencies
- Platform-independent
- Built into Python 3.3+

### Package Management
- **pip**: Python package installer
- **requirements.txt**: Dependency specification

---

## Version Compatibility

### Python Version Requirements

**Minimum**: Python 3.9
**Recommended**: Python 3.11

**Why 3.9+**:
- Type hint improvements (PEP 585, 604)
- Dictionary merge operators (|)
- String methods (removeprefix, removesuffix)
- Required for modern packages

**Why 3.11 recommended**:
- 10-60% faster than 3.10
- Better error messages
- Improved typing features
- Current stable release

### Critical Dependencies

**Must be compatible**:
1. `opensearch-py` with OpenSearch server version
2. `langchain` with `langchain-google-genai`
3. `numpy <2.0` (compatibility constraint)
4. `sentence-transformers` with PyTorch (auto-installed)

### Breaking Changes to Watch

**NumPy 2.0**:
- Many libraries not yet compatible
- Pinned to <2.0 in requirements
- Will update when ecosystem catches up

**LangChain**:
- Rapid development, frequent updates
- Pin to 0.2.x for stability
- Check migration guides for major versions

**OpenSearch**:
- Compatible with 1.x and 2.x servers
- Client version should match server major version

---

## Architecture Decisions

### Why Hybrid Search?

**Decision**: Combine BM25 keyword search with k-NN vector search

**Rationale**:
- **Keyword search (BM25)**: Precise matching, handles specific terms
- **Vector search (k-NN)**: Semantic similarity, understands meaning
- **Together**: Best of both worlds

**Example**:
- Query: "neural network training"
- BM25 finds: Papers with exact phrase
- k-NN finds: Papers about "model optimization", "gradient descent"
- Hybrid: Comprehensive results covering all aspects

### Why Local-First?

**Decision**: Run everything locally (OpenSearch, embeddings, processing)

**Rationale**:
- **Privacy**: Your data stays on your machine
- **Cost**: No cloud fees, only API costs for Gemini
- **Control**: Full control over infrastructure
- **Offline**: Works without constant internet
- **Speed**: No network latency for search

**Cloud usage limited to**:
- Gemini API calls (can be minimized)
- Public Gradio link (optional)

### Why Gemini over GPT?

**Decision**: Use Google Gemini as primary LLM

**Rationale**:
- **Free tier**: No credit card, generous limits
- **Multimodal**: Native vision support
- **Quality**: Competitive with GPT-4
- **Context**: 1M token window
- **Speed**: Fast response times
- **API**: Simple, well-documented

**Trade-offs**:
- GPT-4 may be slightly better for some tasks
- OpenAI ecosystem is more mature
- But cost and accessibility favor Gemini

### Why Gradio over Custom Frontend?

**Decision**: Use Gradio for UI instead of React/Vue

**Rationale**:
- **Speed**: Build in hours, not days
- **Python-only**: No JavaScript needed
- **Good enough**: Professional appearance
- **Share feature**: Instant public URLs
- **Maintenance**: Less code to maintain

**Trade-offs**:
- Less customization than custom frontend
- Tied to Gradio's update cycle
- Limited styling options
- But: Faster development and deployment

---

## Alternative Technologies Considered

### Vector Databases

**Evaluated**:
1. **Pinecone**: Cloud-only, paid service
2. **Weaviate**: More setup complexity
3. **Qdrant**: Excellent but newer
4. **Milvus**: Higher operational overhead
5. **FAISS**: No full-text search
6. **ChromaDB**: Simpler but less features

**Chosen**: OpenSearch (hybrid search, open source, free)

### LLM Providers

**Evaluated**:
1. **OpenAI GPT-4**: Better quality, higher cost, requires payment
2. **Anthropic Claude**: Good quality, limited free tier
3. **Cohere**: Commercial focus, pricing model
4. **Local models (LLaMA, Mistral)**: No API costs, high compute requirements

**Chosen**: Google Gemini (free, multimodal, good quality)

### Orchestration Frameworks

**Evaluated**:
1. **Direct API calls**: More control, more work
2. **LlamaIndex**: Better for pure indexing
3. **Haystack**: Less mature Gemini support

**Chosen**: LangChain (mature, flexible, good Gemini integration)

### UI Frameworks

**Evaluated**:
1. **Streamlit**: Popular but less flexible
2. **Dash**: Plotly-based, more complex
3. **Flask + React**: Full control, more development
4. **Jupyter**: Not production-ready

**Chosen**: Gradio (fast development, good features)

---

## Technology Roadmap

### Potential Future Additions

**Enhanced Search**:
- Reranking models (e.g., cross-encoders)
- Query expansion techniques
- Multi-vector search

**More Data Sources**:
- PubMed Central integration
- Springer/Nature APIs (if available)
- Podcast platforms (Spotify, Apple)

**Advanced AI**:
- Local LLM support (LLaMA, Mistral)
- Fine-tuned models for academic text
- Multi-agent systems

**Performance**:
- GPU acceleration for embeddings
- Distributed OpenSearch
- Caching layer (Redis)

**Features**:
- Document summarization
- Automatic concept extraction
- Knowledge graph generation
- Collaborative features

---

## Dependency Tree

```
Multi-Modal Academic Research System
│
├── AI & ML
│   ├── google-generativeai (Gemini API)
│   ├── google-genai (newer SDK)
│   ├── langchain (orchestration)
│   ├── langchain-google-genai (integration)
│   └── sentence-transformers (embeddings)
│       └── PyTorch (auto-installed)
│
├── Search & Database
│   ├── opensearch-py (vector DB)
│   └── chromadb (alternative)
│
├── Data Collection
│   ├── arxiv (papers)
│   ├── scholarly (Google Scholar)
│   ├── youtube-transcript-api (YouTube)
│   ├── pytube (video metadata)
│   ├── yt-dlp (alternative downloader)
│   └── feedparser (podcasts)
│
├── Document Processing
│   ├── pypdf (PDF text)
│   ├── PyMuPDF (PDF images)
│   ├── whisper (audio transcription)
│   └── pydub (audio processing)
│
├── Web & UI
│   ├── gradio (UI framework)
│   ├── fastapi (backend)
│   └── uvicorn (ASGI server)
│
└── Supporting
    ├── python-dotenv (config)
    ├── requests (HTTP)
    ├── beautifulsoup4 (parsing)
    ├── pandas (data manipulation)
    ├── numpy (numerical computing)
    └── tqdm (progress bars)
```

---

## Installation Impact

### Download Sizes (Approximate)

**Python Packages**: ~2GB total
- PyTorch (sentence-transformers dependency): ~800MB
- Gradio + FastAPI: ~200MB
- OpenSearch client: ~50MB
- Other packages: ~950MB combined

**Models** (downloaded on first use):
- all-MiniLM-L6-v2 embeddings: ~90MB
- Whisper models (optional):
  - tiny: ~75MB
  - base: ~150MB
  - small: ~500MB
  - medium: ~1.5GB
  - large: ~3GB

**Docker Images**:
- OpenSearch: ~1.2GB

**Total First Install**: ~3-4GB (without Whisper models)

### Installation Time

**On typical broadband** (50 Mbps):
- Python packages: 5-10 minutes
- Embedding model: 1-2 minutes
- OpenSearch Docker: 2-3 minutes
- **Total**: 10-15 minutes

---

## Summary

The Multi-Modal Academic Research System leverages a modern, open-source technology stack designed for:

1. **Accessibility**: Free tools, no paywalls
2. **Quality**: State-of-the-art AI and search
3. **Privacy**: Local-first architecture
4. **Flexibility**: Modular, extensible design
5. **Usability**: Simple installation, intuitive interface

**Core Stack**:
- **Python 3.11**: Modern language features
- **Google Gemini**: Free, powerful AI
- **OpenSearch**: Hybrid search capabilities
- **LangChain**: AI orchestration
- **Gradio**: Rapid UI development
- **Sentence Transformers**: Semantic embeddings

This technology combination enables sophisticated academic research workflows while maintaining simplicity and cost-effectiveness.

---

**For more information**:
- [Installation Guide](../setup/installation.md)
- [Quick Start](../setup/quick-start.md)
- [Configuration](../setup/configuration.md)
- [Main Documentation](../../CLAUDE.md)
