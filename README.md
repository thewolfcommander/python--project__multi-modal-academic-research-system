# Multi-Modal Academic Research System

> A comprehensive Python application for collecting, processing, and querying academic content from multiple sources using RAG (Retrieval-Augmented Generation) with OpenSearch and Google Gemini.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Documentation](https://img.shields.io/badge/docs-comprehensive-brightgreen.svg)](docs/README.md)

## 🎯 Overview

The Multi-Modal Academic Research System is a sophisticated platform that enables researchers, students, and professionals to:

- **Collect** academic papers from ArXiv, PubMed Central, and Semantic Scholar
- **Process** PDFs with text extraction and AI-powered diagram analysis
- **Index** content using hybrid search (keyword + semantic) with OpenSearch
- **Query** your knowledge base with natural language using Google Gemini
- **Track** citations automatically with bibliography export (BibTeX, APA)
- **Visualize** your collection with interactive dashboards

### Key Features

✅ **Multi-Source Collection**: Papers, YouTube lectures, and podcasts
✅ **AI-Powered Processing**: Gemini Vision for diagram analysis
✅ **Hybrid Search**: BM25 + semantic vector search
✅ **Citation Tracking**: Automatic extraction and bibliography export
✅ **Interactive UI**: Gradio web interface + FastAPI REST API
✅ **Data Visualization**: Real-time statistics and analytics
✅ **SQLite Tracking**: Complete metadata and collection history
✅ **Free Technologies**: Local deployment, no cloud costs

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- Docker (for OpenSearch)
- Google Gemini API key ([Get free key](https://makersuite.google.com/app/apikey))

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/multi-modal-academic-research-system.git
cd multi-modal-academic-research-system

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# 5. Start OpenSearch
docker run -p 9200:9200 -e "discovery.type=single-node" opensearchproject/opensearch:latest

# 6. Run the application
python main.py
```

The Gradio UI will open at `http://localhost:7860`

**📖 Detailed Instructions**: See [Installation Guide](docs/setup/installation.md) and [Quick Start Guide](docs/setup/quick-start.md)

## 📚 Documentation

### 📘 Documentation Options

**Option 1: Interactive Documentation Site (Recommended)**
```bash
# Serve documentation with live search and navigation
./serve_docs.sh  # Linux/Mac
serve_docs.bat   # Windows

# Visit http://127.0.0.1:8000
```

Built with **MkDocs Material** theme featuring:
- 🔍 Full-text search
- 🎨 Dark/light mode
- 📱 Mobile responsive
- 🔗 Auto-generated navigation
- 📊 Built-in analytics

**Option 2: Static Documentation**

**[View Full Documentation →](docs/README.md)**

Our documentation includes 40+ comprehensive guides totaling 31,000+ lines:

### Getting Started
- **[Installation Guide](docs/setup/installation.md)** - Complete setup instructions
- **[Quick Start](docs/setup/quick-start.md)** - Get running in 5 minutes
- **[Configuration Guide](docs/setup/configuration.md)** - Environment and settings

### Architecture
- **[System Architecture](docs/architecture/overview.md)** - High-level design
- **[Data Flow](docs/architecture/data-flow.md)** - How data moves through the system
- **[Technology Stack](docs/architecture/technology-stack.md)** - Technologies and rationale

### Core Modules
- **[Data Collectors](docs/modules/data-collectors.md)** - ArXiv, YouTube, Podcasts
- **[Data Processors](docs/modules/data-processors.md)** - PDF and video processing
- **[Indexing System](docs/modules/indexing.md)** - OpenSearch hybrid search
- **[Database](docs/modules/database.md)** - SQLite tracking
- **[API Server](docs/modules/api.md)** - FastAPI REST endpoints
- **[Orchestration](docs/modules/orchestration.md)** - LangChain + Gemini
- **[User Interface](docs/modules/ui.md)** - Gradio UI

### Tutorials
- **[Collecting Papers](docs/tutorials/collect-papers.md)** - Step-by-step collection
- **[Custom Searches](docs/tutorials/custom-searches.md)** - Advanced queries
- **[Export Citations](docs/tutorials/export-citations.md)** - Bibliography management
- **[Visualization](docs/tutorials/visualization.md)** - Analytics dashboard
- **[Extending System](docs/tutorials/extending.md)** - Add new features

### Deployment
- **[Local Deployment](docs/deployment/local.md)** - Development setup
- **[Docker Setup](docs/deployment/docker.md)** - Containerization
- **[OpenSearch](docs/deployment/opensearch.md)** - Search engine setup
- **[Production](docs/deployment/production.md)** - Scaling and HA

### Reference
- **[REST API](docs/api/rest-api.md)** - Complete API reference
- **[Database Schema](docs/database/schema.md)** - SQLite structure
- **[Troubleshooting](docs/troubleshooting/common-issues.md)** - Common issues
- **[FAQ](docs/troubleshooting/faq.md)** - Frequently asked questions

## 🎨 Features

### 1. Multi-Source Data Collection

**Supported Sources:**
- **ArXiv**: Preprint scientific papers
- **PubMed Central**: Open-access biomedical papers
- **Semantic Scholar**: Academic search engine
- **YouTube**: Educational videos with transcripts
- **Podcasts**: RSS feed-based podcast episodes

**[Learn More →](docs/modules/data-collectors.md)**

### 2. AI-Powered Processing

**Capabilities:**
- PDF text extraction with PyMuPDF
- Diagram extraction and AI description using Gemini Vision
- Video transcript analysis
- Multi-modal content understanding

**[Learn More →](docs/modules/data-processors.md)**

### 3. Hybrid Search Engine

**Search Strategy:**
- **BM25**: Traditional keyword matching
- **Semantic Search**: Vector embeddings (384-dim)
- **Field Boosting**: title^3, abstract^2
- **Combined Ranking**: Optimized relevance

**[Learn More →](docs/modules/indexing.md)**

### 4. Intelligent Query System

**Features:**
- Natural language queries via Google Gemini
- Automatic citation extraction
- Source tracking and attribution
- Related query suggestions
- Conversation memory

**[Learn More →](docs/modules/orchestration.md)**

### 5. Data Visualization

**Dashboards:**
- Collection statistics (by type, date, source)
- Search analytics
- Citation usage tracking
- Interactive filtering and export

**[Learn More →](docs/tutorials/visualization.md)**

## 🏗️ Architecture

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
│OpenSearch│         │ Database │      │Collectors│   │Processors│
│  Index  │◄─────────│ SQLite   │◄─────│  Layer   │◄──│  Layer   │
│ (Vector │         │(Tracking)│      │          │   │          │
│ Search) │         │          │      │          │   │          │
└──────────┘         └──────────┘      └────┬─────┘   └──────────┘
                                             │
                          ┌──────────────────┼──────────────────┐
                          ▼                  ▼                  ▼
                    ┌──────────┐      ┌──────────┐      ┌──────────┐
                    │  ArXiv   │      │ YouTube  │      │ Podcasts │
                    │   API    │      │   API    │      │   RSS    │
                    └──────────┘      └──────────┘      └──────────┘
```

**[Detailed Architecture →](docs/architecture/overview.md)**

## 💻 Usage Examples

### Collecting Papers

```python
from multi_modal_rag.data_collectors import AcademicPaperCollector

# Initialize collector
collector = AcademicPaperCollector()

# Collect papers from ArXiv
papers = collector.collect_arxiv_papers("machine learning", max_results=20)

# Papers are automatically saved and tracked
print(f"Collected {len(papers)} papers")
```

### Querying the System

```python
from multi_modal_rag.orchestration import ResearchOrchestrator
from multi_modal_rag.indexing import OpenSearchManager

# Initialize components
opensearch = OpenSearchManager()
orchestrator = ResearchOrchestrator("your-gemini-api-key", opensearch)

# Query the system
result = orchestrator.process_query(
    "What is retrieval-augmented generation?",
    "research_assistant"
)

print("Answer:", result['answer'])
print("Citations:", result['citations'])
print("Related Queries:", result['related_queries'])
```

### Using the REST API

```python
import requests

# Get collection statistics
response = requests.get("http://localhost:8000/api/statistics")
stats = response.json()

print(f"Total papers: {stats['by_type']['paper']}")
print(f"Total videos: {stats['by_type']['video']}")
print(f"Indexed items: {stats['indexed']}")

# Search collections
response = requests.get(
    "http://localhost:8000/api/search",
    params={"q": "transformers", "limit": 10}
)
results = response.json()
```

**[More Examples →](docs/tutorials/)**

## 🛠️ Technology Stack

### Core Technologies

- **Python 3.9+** - Main programming language
- **OpenSearch** - Search and vector database
- **Google Gemini** - AI generation and vision analysis
- **SQLite** - Metadata tracking
- **FastAPI** - REST API framework
- **Gradio** - Web UI framework

### Key Libraries

- **LangChain** - AI orchestration
- **SentenceTransformers** - Semantic embeddings
- **PyMuPDF** - PDF processing
- **yt-dlp** - YouTube data extraction
- **arxiv** - ArXiv API client

**[Full Technology Stack →](docs/architecture/technology-stack.md)**

## 📊 Project Statistics

- **Total Code**: ~3,000 lines of Python
- **Documentation**: 40 markdown files, 31,000+ lines
- **Modules**: 7 core modules
- **API Endpoints**: 6 REST endpoints
- **Supported Sources**: 5+ data sources
- **Test Coverage**: Comprehensive error handling

## 🗂️ Project Structure

```
multi-modal-academic-research-system/
├── main.py                          # Application entry point
├── start_api_server.py              # FastAPI server launcher
├── requirements.txt                 # Python dependencies
├── .env.example                     # Environment template
├── CLAUDE.md                        # Claude Code instructions
│
├── multi_modal_rag/                 # Main package
│   ├── data_collectors/             # Data collection modules
│   │   ├── paper_collector.py       # ArXiv, PubMed, Scholar
│   │   ├── youtube_collector.py     # YouTube videos
│   │   └── podcast_collector.py     # Podcast RSS feeds
│   │
│   ├── data_processors/             # Content processing
│   │   ├── pdf_processor.py         # PDF extraction + Gemini Vision
│   │   └── video_processor.py       # Video analysis
│   │
│   ├── indexing/                    # Search infrastructure
│   │   └── opensearch_manager.py    # Hybrid search engine
│   │
│   ├── database/                    # Data tracking
│   │   └── db_manager.py            # SQLite manager
│   │
│   ├── api/                         # REST API
│   │   ├── api_server.py            # FastAPI server
│   │   └── static/                  # Visualization dashboard
│   │       └── visualization.html
│   │
│   ├── orchestration/               # Query pipeline
│   │   ├── research_orchestrator.py # LangChain integration
│   │   └── citation_tracker.py      # Citation management
│   │
│   ├── ui/                          # User interface
│   │   └── gradio_app.py            # Gradio UI
│   │
│   └── logging_config.py            # Logging setup
│
├── data/                            # Data storage
│   ├── papers/                      # Downloaded PDFs
│   ├── videos/                      # Video metadata
│   ├── podcasts/                    # Podcast data
│   ├── processed/                   # Processed content
│   └── collections.db               # SQLite database
│
├── logs/                            # Application logs
│
└── docs/                            # Comprehensive documentation
    ├── README.md                    # Documentation index
    ├── architecture/                # System design
    ├── modules/                     # Module documentation
    ├── setup/                       # Installation & config
    ├── tutorials/                   # Step-by-step guides
    ├── deployment/                  # Deployment guides
    ├── database/                    # Database reference
    ├── api/                         # API reference
    ├── troubleshooting/             # Problem solving
    └── advanced/                    # Advanced topics
```

**[Detailed Project Structure →](docs/development/project-structure.md)**

## 🔧 Configuration

### Environment Variables

```bash
# Required
GEMINI_API_KEY=your_api_key_here

# Optional (defaults shown)
OPENSEARCH_HOST=localhost
OPENSEARCH_PORT=9200
```

### OpenSearch Setup

**Quick Start (Docker):**
```bash
docker run -p 9200:9200 \
  -e "discovery.type=single-node" \
  opensearchproject/opensearch:latest
```

**[Complete OpenSearch Setup →](docs/deployment/opensearch.md)**

## 🚢 Deployment Options

### Local Development
```bash
python main.py  # Gradio UI on port 7860
python start_api_server.py  # FastAPI on port 8000
```

### Docker Deployment
```bash
docker-compose up -d
```

### Production Deployment
- Load balancing with Nginx
- Multi-node OpenSearch cluster
- Redis caching layer
- Automated backups

**[Deployment Guides →](docs/deployment/)**

## 📈 Performance

- **Indexing Speed**: 10-50 documents/second (bulk)
- **Query Latency**: 1-3 seconds (including LLM)
- **Embedding Generation**: ~50ms per document
- **Database Queries**: <10ms
- **Storage**: ~1MB per paper (PDF + metadata + embeddings)

**[Performance Optimization →](docs/advanced/performance.md)**

## 🔒 Security

- API keys stored in `.env` (gitignored)
- Local-only OpenSearch deployment
- CORS configured for localhost
- Input validation on all endpoints
- SQL injection prevention via parameterized queries

**[Security Guide →](docs/deployment/production.md#security)**

## 🐛 Troubleshooting

### Common Issues

**OpenSearch won't connect**
```bash
# Check if OpenSearch is running
curl -X GET "localhost:9200"

# Restart OpenSearch
docker restart opensearch
```

**Gemini API errors**
- Verify API key in `.env`
- Check rate limits
- Ensure internet connection

**Import errors**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**[Complete Troubleshooting Guide →](docs/troubleshooting/common-issues.md)**

## 📚 Learning Resources

### For Beginners
1. [Quick Start Guide](docs/setup/quick-start.md) - Get started in 5 minutes
2. [Collecting Papers Tutorial](docs/tutorials/collect-papers.md) - First data collection
3. [UI Guide](docs/modules/ui.md) - Navigate the interface

### For Developers
1. [Architecture Overview](docs/architecture/overview.md) - System design
2. [Module Documentation](docs/modules/) - Detailed API reference
3. [Extending Guide](docs/tutorials/extending.md) - Add new features

### For Advanced Users
1. [Hybrid Search Algorithm](docs/advanced/hybrid-search.md) - Search internals
2. [Performance Optimization](docs/advanced/performance.md) - Speed improvements
3. [Custom Collectors](docs/advanced/custom-collectors.md) - Add data sources

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Format code
black .

# Lint
flake8 .
```

**[Contributing Guide →](docs/development/contributing.md)**

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

### Open Source Projects
- **OpenSearch** - Powerful search and analytics
- **LangChain** - AI orchestration framework
- **Google Gemini** - Advanced AI capabilities
- **Gradio** - Beautiful UI components

### Data Sources
- **ArXiv** - Open-access scientific papers
- **Semantic Scholar** - Academic search engine
- **YouTube** - Educational video content
- **PubMed Central** - Biomedical literature

## 📞 Support & Contact

- **Documentation**: [docs/README.md](docs/README.md)
- **Issues**: [GitHub Issues](https://github.com/yourusername/multi-modal-academic-research-system/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/multi-modal-academic-research-system/discussions)

## 🗺️ Roadmap

### Version 1.x (Current)
- ✅ Multi-source data collection
- ✅ Hybrid search with OpenSearch
- ✅ Gemini integration
- ✅ Citation tracking
- ✅ Visualization dashboard

### Version 2.0 (Planned)
- 🔲 Collaborative features (shared collections)
- 🔲 Advanced analytics (trends, network graphs)
- 🔲 Mobile-responsive UI
- 🔲 Batch processing improvements
- 🔲 Multi-language support

### Version 3.0 (Future)
- 🔲 Distributed search cluster
- 🔲 Real-time collaboration
- 🔲 Plugin architecture
- 🔲 Advanced ML features
- 🔲 Cloud deployment options

**[Full Roadmap →](docs/development/roadmap.md)**

## ⭐ Star History

If you find this project useful, please consider giving it a star! ⭐

---

**Made with ❤️ for the research community**

**[📖 Read the Full Documentation →](docs/README.md)**
