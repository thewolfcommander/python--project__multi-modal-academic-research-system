# Multi-Modal Academic Research System - Tutorials

Comprehensive hands-on tutorials for using and extending the Multi-Modal Academic Research System.

## Quick Start

If you're new to the system, we recommend following the tutorials in this order:

1. **[Collecting Papers](collect-papers.md)** - Learn how to collect academic content
2. **[Custom Searches](custom-searches.md)** - Master advanced search techniques
3. **[Exporting Citations](export-citations.md)** - Manage and export your research citations
4. **[Visualization Dashboard](visualization.md)** - Analyze your collection with visualizations
5. **[Extending the System](extending.md)** - Customize and extend functionality

## Tutorial Overview

### 1. Collecting Papers Tutorial

**File:** [collect-papers.md](collect-papers.md)
**Level:** Beginner
**Time:** 30-45 minutes

Learn how to collect academic papers from multiple sources including ArXiv, Semantic Scholar, and PubMed Central.

**Topics Covered:**
- Using the Gradio UI for data collection
- Python API for programmatic collection
- Different search strategies for each source
- Batch collection and automation
- Troubleshooting common issues
- Best practices for paper collection

**What You'll Build:**
- A collection of 100+ papers on your research topic
- Automated collection scripts
- Deduplication and filtering workflows

### 2. Custom Searches Tutorial

**File:** [custom-searches.md](custom-searches.md)
**Level:** Intermediate
**Time:** 45-60 minutes

Master advanced search techniques using Boolean operators, field boosting, filters, and OpenSearch Query DSL.

**Topics Covered:**
- Advanced query syntax (AND, OR, NOT, wildcards)
- Field-specific searches and boosting
- Combining multiple filters
- Date, author, and category filtering
- OpenSearch Query DSL
- Search relevance optimization
- Custom re-ranking algorithms

**What You'll Build:**
- Custom search queries for precise results
- Multi-criteria filtering scripts
- Relevance tuning configurations
- Similarity search functionality

### 3. Exporting Citations Tutorial

**File:** [export-citations.md](export-citations.md)
**Level:** Beginner to Intermediate
**Time:** 30-40 minutes

Learn how to export and manage citations in various formats for your research writing.

**Topics Covered:**
- Understanding citation tracking
- Exporting from the Gradio UI
- Programmatic export via Python
- Multiple citation formats (BibTeX, APA, MLA, Chicago)
- Integrating with Zotero, Mendeley, and EndNote
- Creating custom citation formats
- Automated export workflows

**What You'll Build:**
- Bibliography files in multiple formats
- Integration with reference managers
- Custom citation formatters
- Automated export scripts
- Citation usage reports

### 4. Visualization Dashboard Tutorial

**File:** [visualization.md](visualization.md)
**Level:** Intermediate
**Time:** 40-50 minutes

Explore and analyze your research collection using the FastAPI visualization dashboard.

**Topics Covered:**
- Starting the FastAPI dashboard
- Understanding collection statistics
- Filtering and searching data
- Exporting data in various formats
- Creating custom visualizations
- Using the REST API
- Real-time monitoring

**What You'll Build:**
- Interactive charts and graphs
- Custom analytics dashboards
- Data export pipelines
- API client for automation
- Collection monitoring tools

### 5. Extending the System Tutorial

**File:** [extending.md](extending.md)
**Level:** Advanced
**Time:** 60-90 minutes

Learn how to extend the system with new data collectors, processors, UI components, and search filters.

**Topics Covered:**
- System architecture overview
- Creating new data collectors
- Building custom processors
- Modifying the Gradio UI
- Adding search filters
- Writing tests
- Contributing to the project

**What You'll Build:**
- Custom blog post collector
- GitHub repository collector
- Custom data processors
- New UI components
- Advanced search filters
- Test suites

## Learning Paths

### For Researchers

Focus on using the system for your research:

1. **[Collecting Papers](collect-papers.md)** - Build your research database
2. **[Custom Searches](custom-searches.md)** - Find relevant papers efficiently
3. **[Exporting Citations](export-citations.md)** - Manage citations for writing
4. **[Visualization Dashboard](visualization.md)** - Analyze your collection

### For Developers

Focus on extending and customizing the system:

1. **[Collecting Papers](collect-papers.md)** - Understand data flow
2. **[Custom Searches](custom-searches.md)** - Learn search architecture
3. **[Extending the System](extending.md)** - Add new features
4. **[Visualization Dashboard](visualization.md)** - Build analytics tools

### For Data Scientists

Focus on data analysis and visualization:

1. **[Collecting Papers](collect-papers.md)** - Gather data
2. **[Visualization Dashboard](visualization.md)** - Analyze patterns
3. **[Custom Searches](custom-searches.md)** - Extract insights
4. **[Extending the System](extending.md)** - Add custom analytics

## Prerequisites

Before starting the tutorials, ensure you have:

1. **Python 3.8+** installed
2. **Virtual environment** activated
3. **Dependencies** installed (`pip install -r requirements.txt`)
4. **OpenSearch** running (via Docker)
5. **Gemini API key** configured in `.env`

Quick setup:

```bash
# Clone repository
git clone https://github.com/your-repo/multi-modal-academic-research-system.git
cd multi-modal-academic-research-system

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# Start OpenSearch
docker run -p 9200:9200 -e "discovery.type=single-node" opensearchproject/opensearch:latest

# Start application
python main.py
```

## Tutorial Features

Each tutorial includes:

- **Step-by-step instructions** with clear explanations
- **Complete code examples** that you can copy and run
- **Practical use cases** based on real research scenarios
- **Troubleshooting sections** for common issues
- **Best practices** and tips
- **Common pitfalls** to avoid
- **Next steps** and related tutorials

## Additional Resources

### Documentation
- [Main Documentation](../README.md)
- [API Reference](../api/)
- [Architecture Overview](../architecture/)
- [Setup Guide](../setup/)

### Code Examples
All code examples from the tutorials are available in the `examples/` directory:
- `examples/collection/` - Paper collection scripts
- `examples/search/` - Advanced search examples
- `examples/citations/` - Citation export scripts
- `examples/visualization/` - Visualization examples
- `examples/extensions/` - Custom extensions

### Community
- **GitHub Issues:** Report bugs or request features
- **Discussions:** Ask questions and share ideas
- **Pull Requests:** Contribute improvements

## Getting Help

If you encounter issues while following the tutorials:

1. **Check the troubleshooting section** in each tutorial
2. **Review the logs** in `logs/` directory
3. **Consult the main documentation** in `docs/`
4. **Search GitHub issues** for similar problems
5. **Ask for help** in GitHub Discussions

## Contributing to Tutorials

We welcome improvements to these tutorials! If you:

- Find an error or typo
- Have a suggestion for clarification
- Want to add a new example
- Discovered a better approach

Please submit a pull request or open an issue.

### Tutorial Writing Guidelines

If you'd like to contribute a new tutorial:

1. Follow the existing tutorial structure
2. Include practical, working code examples
3. Test all code examples before submitting
4. Add troubleshooting tips based on real issues
5. Include screenshots or diagrams where helpful
6. Link to related tutorials and documentation

## Feedback

We'd love to hear your feedback on these tutorials:

- What worked well?
- What was confusing?
- What's missing?
- What would you like to learn more about?

Please share your thoughts via GitHub issues or discussions.

---

**Last Updated:** October 2024
**Version:** 1.0.0
**Maintained by:** Multi-Modal Research System Team
