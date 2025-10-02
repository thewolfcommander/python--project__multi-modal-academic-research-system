# Frequently Asked Questions (FAQ)

Common questions and answers about the Multi-Modal Academic Research System.

## Table of Contents

- [Installation & Setup](#installation--setup)
- [Configuration](#configuration)
- [Data Collection](#data-collection)
- [Search & Retrieval](#search--retrieval)
- [Performance](#performance)
- [Features & Capabilities](#features--capabilities)
- [Troubleshooting](#troubleshooting)
- [Advanced Topics](#advanced-topics)

---

## Installation & Setup

### Q: What are the system requirements?

**A**: Minimum requirements:
- **Python**: 3.8 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Disk**: 10GB free space (more for storing papers/videos)
- **Docker**: For running OpenSearch
- **Internet**: Required for API calls and data collection

---

### Q: Do I need to pay for any services?

**A**: No, the system uses free services:
- **Gemini API**: Free tier (60 requests/minute)
- **OpenSearch**: Self-hosted locally (no cost)
- **ArXiv, YouTube, etc.**: Free public APIs
- **Embedding model**: Runs locally (no API costs)

---

### Q: Can I run this without Docker?

**A**: Docker is required only for OpenSearch. Alternatives:
1. Install OpenSearch locally without Docker
2. Use Elasticsearch instead (similar API)
3. Connect to a remote OpenSearch instance

However, Docker is the recommended and easiest method.

---

### Q: Why does installation take so long?

**A**: Common reasons:
- **Large dependencies**: PyTorch, transformers (can be 1-2GB)
- **Slow internet**: Downloads from PyPI
- **Compiling packages**: Some packages compile from source

Speed up installation:
```bash
# Use binary wheels when available
pip install --only-binary=:all: -r requirements.txt

# Or use conda for pre-compiled packages
conda install pytorch sentence-transformers
```

---

### Q: Can I use this on Windows?

**A**: Yes, but with some considerations:
- Use `venv\Scripts\activate` instead of `source venv/bin/activate`
- Docker Desktop required for Windows
- Path separators are different (`\` vs `/`)
- Some shell commands may differ

Consider using WSL2 (Windows Subsystem for Linux) for better compatibility.

---

## Configuration

### Q: How do I get a Gemini API key?

**A**: Follow these steps:
1. Visit https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key to your `.env` file:
   ```
   GEMINI_API_KEY=your_key_here
   ```

---

### Q: Can I use other LLMs instead of Gemini?

**A**: Yes, the system can be adapted for other LLMs:
- **OpenAI GPT**: Modify `research_orchestrator.py` to use OpenAI API
- **Local LLMs**: Use Ollama or LM Studio
- **Claude**: Use Anthropic API
- **Open-source models**: Use Hugging Face transformers

See [Advanced Topics](../advanced/custom-collectors.md) for implementation details.

---

### Q: Where are my downloaded papers stored?

**A**: Papers are stored in:
- **PDFs**: `data/papers/`
- **Videos**: `data/videos/`
- **Podcasts**: `data/podcasts/`
- **Processed data**: `data/processed/`

You can change locations in configuration files.

---

### Q: How do I change the OpenSearch port?

**A**: Update your `.env` file:
```bash
OPENSEARCH_HOST=localhost
OPENSEARCH_PORT=9201  # Change from default 9200
```

Then start OpenSearch with the new port:
```bash
docker run -p 9201:9200 opensearchproject/opensearch:latest
```

---

### Q: Can I use a remote OpenSearch instance?

**A**: Yes, update `.env`:
```bash
OPENSEARCH_HOST=your-opensearch-host.com
OPENSEARCH_PORT=9200
OPENSEARCH_USE_SSL=true
OPENSEARCH_USER=admin
OPENSEARCH_PASSWORD=your_password
```

---

## Data Collection

### Q: What data sources are supported?

**A**: Current sources:
- **Papers**: ArXiv, PubMed Central, Semantic Scholar
- **Videos**: YouTube (educational channels)
- **Podcasts**: RSS feeds

See [Custom Collectors](../advanced/custom-collectors.md) to add more sources.

---

### Q: How many papers can I collect at once?

**A**: Limits:
- **ArXiv**: 2000 per query (API limit)
- **Semantic Scholar**: Rate-limited (100/minute)
- **YouTube**: No hard limit, but respect rate limits
- **Local storage**: Limited by disk space

Recommended: Start with 10-50 papers for testing.

---

### Q: Can I collect papers from specific journals?

**A**: Partially:
- **ArXiv**: Yes, filter by category (e.g., `cs.LG` for ML)
- **PubMed**: Yes, filter by journal name
- **Semantic Scholar**: Yes, use field filters

Example ArXiv query:
```python
query = "cat:cs.LG AND ti:neural networks"
```

---

### Q: How do I collect papers published in a specific year?

**A**: Use date filters:

```python
# ArXiv
query = "submittedDate:[20230101 TO 20231231] AND all:machine learning"

# In the UI, you can filter after collection
# Or modify the collector to add date filters
```

---

### Q: Why can't I download some papers?

**A**: Common reasons:
- **Access restrictions**: Some papers require subscriptions
- **Invalid URLs**: Paper may have been removed
- **Rate limiting**: Too many requests too fast
- **Network issues**: Firewall or proxy blocking

The system focuses on open-access content (ArXiv, PMC).

---

### Q: Can I import my own PDFs?

**A**: Yes, you can:
1. Place PDFs in `data/papers/`
2. Use the processing pipeline:
   ```python
   from multi_modal_rag.data_processors import pdf_processor

   processor = pdf_processor.PDFProcessor()
   result = processor.process_pdf("path/to/paper.pdf")
   ```
3. Index the processed content

---

### Q: How do I collect videos from specific YouTube channels?

**A**: Modify `youtube_collector.py`:

```python
def collect_from_channel(channel_id, max_videos=50):
    """Collect videos from specific channel."""
    from googleapiclient.discovery import build

    youtube = build('youtube', 'v3', developerKey=api_key)

    request = youtube.search().list(
        part='snippet',
        channelId=channel_id,
        maxResults=max_videos,
        type='video'
    )

    response = request.execute()
    return response['items']
```

---

## Search & Retrieval

### Q: How does hybrid search work?

**A**: Hybrid search combines:
1. **Keyword search**: BM25 algorithm (like traditional search)
2. **Semantic search**: Vector similarity using embeddings

Results from both are combined and ranked. See [Hybrid Search Guide](../advanced/hybrid-search.md) for details.

---

### Q: Why are my search results not relevant?

**A**: Possible causes:
- **Mismatch between query and content**: Try different keywords
- **Not enough indexed content**: Add more documents
- **Poor field weights**: Adjust in `opensearch_manager.py`
- **Wrong search mode**: Try semantic-only or keyword-only

Tips:
- Use specific technical terms
- Try multiple phrasings
- Check if documents are actually indexed

---

### Q: How many documents should I index for good results?

**A**: Recommendations:
- **Minimum**: 10-20 papers for basic testing
- **Good**: 100-200 papers for decent coverage
- **Excellent**: 500+ papers for comprehensive results

More documents = better context, but slower indexing.

---

### Q: Can I search only specific content types?

**A**: Yes, filter by content type:

```python
query = {
    "query": {
        "bool": {
            "must": [
                {"match": {"content": "machine learning"}}
            ],
            "filter": [
                {"term": {"content_type": "paper"}}  # or "video", "podcast"
            ]
        }
    }
}
```

Or use the UI filters (if implemented).

---

### Q: How do I improve search speed?

**A**: Optimization strategies:
1. **Reduce result size**: Return fewer documents
2. **Use filters**: Pre-filter before searching
3. **Optimize OpenSearch**: Increase memory, reduce shards
4. **Cache results**: Cache common queries
5. **Use pagination**: Don't load all results at once

See [Performance Guide](../advanced/performance.md) for details.

---

### Q: Can I search by author name?

**A**: Yes:

```python
query = {
    "query": {
        "bool": {
            "must": [
                {"match": {"content": "neural networks"}}
            ],
            "filter": [
                {"term": {"authors": "Geoffrey Hinton"}}
            ]
        }
    }
}
```

---

## Performance

### Q: Why is the first query slow?

**A**: First query may be slow due to:
- **Model loading**: Embedding model loaded into memory
- **Index warming**: OpenSearch caches are cold
- **LLM initialization**: Gemini client initialization

Subsequent queries are faster (cached models, warm indices).

---

### Q: How much RAM does the system use?

**A**: Typical usage:
- **Python application**: 1-2GB
- **OpenSearch**: 2-4GB (configurable)
- **Embedding model**: 500MB-1GB
- **Total**: 4-8GB recommended

For large-scale usage, 16GB+ recommended.

---

### Q: Can I run this on a Raspberry Pi?

**A**: Possible but not recommended:
- **RAM limitation**: Need at least 4GB
- **CPU**: Will be very slow
- **Storage**: Need sufficient space

Better options: Use cloud instance or local machine.

---

### Q: How do I process documents faster?

**A**: Speed improvements:
1. **Use GPU**: For embedding generation
2. **Batch processing**: Process multiple docs at once
3. **Reduce Gemini calls**: Cache vision analysis results
4. **Parallel processing**: Use multiprocessing
5. **Skip large PDFs**: Set size limits

Example:
```python
# Process in parallel
from multiprocessing import Pool

with Pool(processes=4) as pool:
    results = pool.map(process_pdf, pdf_files)
```

---

### Q: Why is indexing slow?

**A**: Common bottlenecks:
- **Embedding generation**: CPU-bound operation
- **Gemini API calls**: Rate-limited to 60/min
- **OpenSearch indexing**: Network and disk I/O
- **PDF processing**: Complex PDFs with many images

Solutions: See [Performance Optimization](../advanced/performance.md).

---

## Features & Capabilities

### Q: Does the system support multiple languages?

**A**: Limited support:
- **Papers**: Primarily English (ArXiv, PMC)
- **Embeddings**: Model supports multiple languages
- **Gemini**: Supports many languages
- **Search**: Works with non-English content

For full multilingual support, you'd need:
- Multilingual embedding model
- Language-specific data sources
- Translation capabilities

---

### Q: Can I export search results?

**A**: Yes, export options:
- **Citations**: Export via Citation Manager tab
- **Results**: Save as JSON, CSV, or BibTeX
- **Summaries**: Copy from UI or save to file

Implementation:
```python
import json

# Export results
with open('results.json', 'w') as f:
    json.dump(search_results, f, indent=2)
```

---

### Q: Does the system support collaborative research?

**A**: Not built-in, but you could:
- **Shared index**: Multiple users connect to same OpenSearch
- **Cloud deployment**: Deploy on server, share URL
- **Export/import**: Share indexed content between instances

Future enhancement could add user accounts and sharing features.

---

### Q: Can I integrate this with Zotero or Mendeley?

**A**: Not directly, but possible:
1. Export papers from Zotero
2. Import PDFs into this system
3. Use citation export to import back

Or build a custom integration using their APIs.

---

### Q: Does it support citation management?

**A**: Yes, basic features:
- **Track citations**: From LLM responses
- **View bibliography**: In Citation Manager
- **Export citations**: BibTeX, JSON formats

For advanced features, use dedicated tools like Zotero.

---

### Q: Can I add annotations or notes to papers?

**A**: Not currently implemented, but could be added:
- Store notes in OpenSearch alongside documents
- Add UI for note-taking
- Include notes in search results

---

### Q: Does it support PDF highlighting or markup?

**A**: No, this is a retrieval and question-answering system, not a PDF reader. Use dedicated PDF tools for markup.

---

## Troubleshooting

### Q: OpenSearch won't start. What should I do?

**A**: Troubleshooting steps:
1. Check Docker is running: `docker ps`
2. Check port availability: `lsof -i :9200`
3. Check Docker logs: `docker logs <container_id>`
4. Try different port: `-p 9201:9200`
5. Increase memory: Add `--memory=4g`

See [OpenSearch Troubleshooting](./opensearch.md) for details.

---

### Q: I get "Gemini API key invalid". How do I fix this?

**A**: Steps to fix:
1. Verify key in `.env` file (no quotes, no spaces)
2. Test key at https://makersuite.google.com/
3. Generate new key if expired
4. Check for typos or extra characters
5. Ensure `.env` is in project root

---

### Q: Search returns no results. Why?

**A**: Check these:
1. **Index exists**: `curl http://localhost:9200/_cat/indices`
2. **Documents indexed**: `curl http://localhost:9200/research_assistant/_count`
3. **Query format**: Test with simple query
4. **Content mismatch**: Verify indexed content matches query

---

### Q: The UI won't load. What's wrong?

**A**: Common issues:
1. **Port in use**: Kill process using port 7860
2. **Python error**: Check terminal for stack trace
3. **Missing dependencies**: Reinstall requirements
4. **OpenSearch down**: Start OpenSearch first

---

### Q: How do I enable debug logging?

**A**: Add to your code:

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

Or set in main.py before launching.

---

### Q: Where can I find error logs?

**A**: Logs are in:
- **Console output**: Check terminal
- **Log files**: `logs/` directory (if enabled)
- **OpenSearch logs**: `docker logs opensearch-node`
- **Gradio logs**: In console output

---

## Advanced Topics

### Q: Can I use a different embedding model?

**A**: Yes, modify `opensearch_manager.py`:

```python
from sentence_transformers import SentenceTransformer

# Change model
model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')

# Update dimension in index mapping (768 for above model)
```

See [Embedding Models Guide](../advanced/embedding-models.md).

---

### Q: How do I add a custom data source?

**A**: Create a new collector:

1. Create `custom_collector.py` in `data_collectors/`
2. Implement collection logic
3. Register in `main.py`
4. Add UI option in `gradio_app.py`

See [Custom Collectors Guide](../advanced/custom-collectors.md).

---

### Q: Can I use this for non-academic content?

**A**: Yes, adapt for any content:
- Modify collectors for your sources
- Adjust data schema in OpenSearch
- Update UI for your use case

The architecture is general-purpose RAG.

---

### Q: How do I fine-tune the search ranking?

**A**: Adjust field weights:

```python
query = {
    "query": {
        "multi_match": {
            "query": query_text,
            "fields": [
                "title^3",      # 3x weight
                "abstract^2",   # 2x weight
                "content^1",    # 1x weight
                "key_concepts^2"
            ]
        }
    }
}
```

Test different weights for your use case.

---

### Q: Can I deploy this to production?

**A**: Yes, but consider:
- **Authentication**: Add user auth
- **Scaling**: Use managed OpenSearch (AWS, etc.)
- **Rate limiting**: Implement proper limits
- **Monitoring**: Add logging and metrics
- **Security**: Sanitize inputs, use HTTPS
- **Costs**: Monitor API usage

---

### Q: How do I backup my data?

**A**: Backup strategies:

1. **OpenSearch snapshots**:
```bash
curl -X PUT "localhost:9200/_snapshot/backup/snapshot_1?wait_for_completion=true"
```

2. **File backup**:
```bash
tar -czf backup.tar.gz data/
```

3. **Export to JSON**:
```python
# Export all documents
from opensearchpy import helpers

docs = helpers.scan(client, index='research_assistant')
with open('backup.json', 'w') as f:
    json.dump(list(docs), f)
```

---

### Q: Can I contribute to the project?

**A**: Yes! Contributions welcome:
- Submit bug reports
- Suggest features
- Submit pull requests
- Improve documentation

See CONTRIBUTING.md for guidelines (if available).

---

### Q: What's the difference between this and ChatGPT with plugins?

**A**: Key differences:
- **Local control**: You control the data and index
- **Free**: No subscription costs (except API usage)
- **Customizable**: Modify for your needs
- **Private**: Data stays local
- **Academic focus**: Specialized for research
- **Multi-modal**: Integrates papers, videos, podcasts

---

### Q: Is there a roadmap for future features?

**A**: Potential enhancements:
- More data sources (Google Scholar, JSTOR)
- Better visualization (knowledge graphs)
- Collaborative features (sharing, comments)
- Mobile app
- Better citation management
- Integration with reference managers
- Support for more file formats

---

## Still Have Questions?

If your question isn't answered here:

1. Check the [Troubleshooting Guide](./common-issues.md)
2. Review the [CLAUDE.md](../../../CLAUDE.md) project overview
3. Search GitHub issues
4. Create a new issue with your question

## Additional Resources

- [Common Issues](./common-issues.md)
- [OpenSearch Troubleshooting](./opensearch.md)
- [API Errors](./api-errors.md)
- [Performance Guide](../advanced/performance.md)
- [Custom Collectors](../advanced/custom-collectors.md)
- [Hybrid Search](../advanced/hybrid-search.md)
