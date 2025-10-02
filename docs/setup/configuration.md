# Configuration Guide

Comprehensive guide to configuring the Multi-Modal Academic Research System for optimal performance.

## Table of Contents

- [Environment Variables](#environment-variables)
- [OpenSearch Configuration](#opensearch-configuration)
- [API Configuration](#api-configuration)
- [Logging Configuration](#logging-configuration)
- [Application Settings](#application-settings)
- [Advanced Configuration](#advanced-configuration)
- [Performance Tuning](#performance-tuning)
- [Security Considerations](#security-considerations)

---

## Environment Variables

The system uses a `.env` file in the project root to manage configuration. All environment variables are optional except `GEMINI_API_KEY`.

### Creating the Configuration File

```bash
# Copy the example file
cp .env.example .env

# Edit with your preferred editor
nano .env
# or
code .env
# or
vim .env
```

### Available Environment Variables

#### Required Variables

**`GEMINI_API_KEY`** (Required)
- **Description**: Google Gemini API key for AI-powered analysis and generation
- **Default**: None (must be provided)
- **How to get**: https://makersuite.google.com/app/apikey
- **Example**: `GEMINI_API_KEY=AIzaSyAbc123def456ghi789jkl012mno345pqr`
- **Notes**:
  - Free tier available (no credit card required)
  - Used for PDF diagram analysis and research query responses
  - Do NOT use quotes around the key

#### OpenSearch Variables

**`OPENSEARCH_HOST`**
- **Description**: Hostname or IP address of the OpenSearch server
- **Default**: `localhost`
- **Example**: `OPENSEARCH_HOST=localhost`
- **Valid values**:
  - `localhost` (local Docker container)
  - `127.0.0.1` (local IP)
  - Any valid hostname or IP address

**`OPENSEARCH_PORT`**
- **Description**: Port number for OpenSearch connection
- **Default**: `9200`
- **Example**: `OPENSEARCH_PORT=9200`
- **Valid values**: Any valid port number (1-65535)
- **Notes**: Default OpenSearch port is 9200

**`OPENSEARCH_USERNAME`** (Not in .env.example, but supported)
- **Description**: Username for OpenSearch authentication
- **Default**: `admin` (hardcoded in opensearch_manager.py)
- **Example**: `OPENSEARCH_USERNAME=admin`
- **Notes**: Currently not exposed in .env but can be added

**`OPENSEARCH_PASSWORD`** (Not in .env.example, but supported)
- **Description**: Password for OpenSearch authentication
- **Default**: `MyStrongPassword@2024!` (hardcoded in opensearch_manager.py)
- **Example**: `OPENSEARCH_PASSWORD=MyStrongPassword@2024!`
- **Security**: Should match the password set when starting OpenSearch container

### Example .env File

**Minimal configuration**:
```env
GEMINI_API_KEY=AIzaSyAbc123def456ghi789jkl012mno345pqr
OPENSEARCH_HOST=localhost
OPENSEARCH_PORT=9200
```

**Custom OpenSearch server**:
```env
GEMINI_API_KEY=AIzaSyAbc123def456ghi789jkl012mno345pqr
OPENSEARCH_HOST=192.168.1.100
OPENSEARCH_PORT=9201
```

**Development environment**:
```env
# Gemini API
GEMINI_API_KEY=AIzaSyAbc123def456ghi789jkl012mno345pqr

# OpenSearch (local Docker)
OPENSEARCH_HOST=localhost
OPENSEARCH_PORT=9200

# Optional: Add comments for clarity
# Get API key from: https://makersuite.google.com/app/apikey
```

### Environment Variable Best Practices

1. **Never commit .env to version control**
   - Already in `.gitignore`
   - Keep sensitive keys private

2. **Use separate .env files for different environments**
   - `.env.development`
   - `.env.production`
   - `.env.testing`

3. **No quotes around values**
   ```env
   # Correct
   GEMINI_API_KEY=AIzaSyAbc123

   # Incorrect (will include quotes in the value)
   GEMINI_API_KEY="AIzaSyAbc123"
   ```

4. **No spaces around equals sign**
   ```env
   # Correct
   OPENSEARCH_HOST=localhost

   # Incorrect
   OPENSEARCH_HOST = localhost
   ```

---

## OpenSearch Configuration

OpenSearch is the vector database and search engine powering the research system.

### Local Development Setup (Docker)

**Standard configuration**:
```bash
docker run -d \
  --name opensearch-research \
  -p 9200:9200 \
  -p 9600:9600 \
  -e "discovery.type=single-node" \
  -e "OPENSEARCH_INITIAL_ADMIN_PASSWORD=MyStrongPassword@2024!" \
  opensearchproject/opensearch:latest
```

**With persistent storage**:
```bash
docker run -d \
  --name opensearch-research \
  -p 9200:9200 \
  -p 9600:9600 \
  -e "discovery.type=single-node" \
  -e "OPENSEARCH_INITIAL_ADMIN_PASSWORD=MyStrongPassword@2024!" \
  -v opensearch-data:/usr/share/opensearch/data \
  opensearchproject/opensearch:latest
```

**With custom memory limits**:
```bash
docker run -d \
  --name opensearch-research \
  -p 9200:9200 \
  -p 9600:9600 \
  -e "discovery.type=single-node" \
  -e "OPENSEARCH_INITIAL_ADMIN_PASSWORD=MyStrongPassword@2024!" \
  -e "OPENSEARCH_JAVA_OPTS=-Xms512m -Xmx512m" \
  opensearchproject/opensearch:latest
```

### Index Configuration

The system creates a `research_assistant` index with the following settings:

**Default Index Settings** (defined in `opensearch_manager.py`):
```python
{
    'settings': {
        'index': {
            'number_of_shards': 2,
            'number_of_replicas': 1,
            'knn': True  # Enable k-nearest neighbors for vector search
        }
    }
}
```

**Index Mappings**:
- `content_type`: Keyword (paper, video, podcast)
- `title`: Text with keyword sub-field
- `abstract`: Text
- `content`: Text (main searchable content)
- `authors`: Keyword array
- `publication_date`: Date
- `url`: Keyword
- `transcript`: Text (for videos/podcasts)
- `diagram_descriptions`: Text (from Gemini Vision)
- `key_concepts`: Keyword array
- `citations`: Nested objects
- `embedding`: kNN vector (384 dimensions, all-MiniLM-L6-v2)
- `metadata`: Object (flexible additional data)

### Index Management

**Check index status** (via Settings tab in UI):
- View connection status
- See index statistics
- Verify document count

**Delete and recreate index**:
```python
# Via Python console
from multi_modal_rag.indexing.opensearch_manager import OpenSearchManager
manager = OpenSearchManager()
manager.client.indices.delete(index='research_assistant')
manager.create_index('research_assistant')
```

**Backup index data**:
```bash
# Using OpenSearch API
curl -X POST "https://localhost:9200/_snapshot/my_backup/snapshot_1?wait_for_completion=true" \
  -ku admin:MyStrongPassword@2024!
```

### Connection Settings

**SSL Configuration** (in `opensearch_manager.py`):
```python
OpenSearch(
    hosts=[{'host': host, 'port': port}],
    http_auth=(username, password),
    http_compress=True,
    use_ssl=True,              # Enable SSL
    verify_certs=False,        # Disable cert verification (local dev)
    ssl_assert_hostname=False,
    ssl_show_warn=False,
    timeout=5                  # 5 second timeout
)
```

**Modify connection timeout**:
Edit `multi_modal_rag/indexing/opensearch_manager.py`:
```python
timeout=30  # Increase for slow networks
```

---

## API Configuration

### Google Gemini API

**API Key Setup**:
1. Visit: https://makersuite.google.com/app/apikey
2. Sign in with Google account
3. Create new API key
4. Copy to `.env` file

**Rate Limits** (Free Tier):
- 60 requests per minute
- 1,500 requests per day
- The system includes rate limiting to avoid exceeding these limits

**Models Used**:
1. **Gemini Pro** (`gemini-1.5-pro-latest`):
   - Research query responses
   - Text analysis and synthesis
   - Citation generation

2. **Gemini Vision** (`gemini-1.5-flash`):
   - PDF diagram analysis
   - Image description generation
   - Visual content understanding

**Switching Models** (in code):
Edit `multi_modal_rag/orchestration/research_orchestrator.py`:
```python
# Current
self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest")

# Alternative (faster, less capable)
self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
```

### Academic Data Source APIs

**ArXiv** (via `arxiv` package):
- No API key required
- Rate limit: 1 request per 3 seconds (built-in)
- Free and unlimited

**Semantic Scholar** (via `scholarly` package):
- No API key required
- May require rate limiting for heavy use
- Free tier available

**YouTube** (via `youtube-transcript-api`):
- No API key required
- Uses public transcript API
- Subject to YouTube rate limits

**PubMed Central**:
- No API key required
- E-utilities API (free)
- Rate limit: 3 requests per second

---

## Logging Configuration

The system uses Python's built-in logging with custom configuration.

### Log File Location

**Default**: `logs/research_system_YYYYMMDD_HHMMSS.log`

**Example**: `logs/research_system_20241002_143022.log`

### Log Levels

**File Handler** (detailed logging):
- Level: `DEBUG`
- Captures all events including debug information
- Format: `timestamp - module - level - file:line - function() - message`

**Console Handler** (important messages):
- Level: `INFO`
- Shows only important events in terminal
- Format: `level - module - message`

### Log Configuration

**Defined in**: `multi_modal_rag/logging_config.py`

**File Handler Configuration**:
```python
file_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')
file_handler.setLevel(logging.DEBUG)

file_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s() - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
```

**Console Handler Configuration**:
```python
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

console_formatter = logging.Formatter(
    '%(levelname)s - %(name)s - %(message)s'
)
```

### Customizing Logging

**Change log level** (more or less verbose):

Edit `multi_modal_rag/logging_config.py`:
```python
# More verbose (show everything)
logger.setLevel(logging.DEBUG)
console_handler.setLevel(logging.DEBUG)

# Less verbose (errors only)
logger.setLevel(logging.ERROR)
console_handler.setLevel(logging.ERROR)
```

**Change log file location**:
```python
# In setup_logging() function
log_dir = "custom_logs"  # Change from "logs"
```

**Disable console output**:
```python
# Comment out console handler
# logger.addHandler(console_handler)
```

**Log rotation** (for long-running applications):
```python
from logging.handlers import RotatingFileHandler

file_handler = RotatingFileHandler(
    log_file,
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
```

### Log File Management

**Automatic**: Log files accumulate in `logs/` directory

**Manual cleanup**:
```bash
# Delete logs older than 7 days
find logs/ -name "*.log" -mtime +7 -delete

# Keep only last 10 log files
ls -t logs/*.log | tail -n +11 | xargs rm
```

**Archive logs**:
```bash
# Compress old logs
tar -czf logs_archive_$(date +%Y%m%d).tar.gz logs/*.log
```

---

## Application Settings

### Gradio UI Configuration

**Defined in**: `main.py`

**Default settings**:
```python
app.launch(
    server_name="0.0.0.0",  # Listen on all interfaces
    server_port=7860,        # Default Gradio port
    share=True               # Create public URL
)
```

**Custom port**:
```python
app.launch(
    server_name="0.0.0.0",
    server_port=8080,  # Custom port
    share=True
)
```

**Disable public sharing**:
```python
app.launch(
    server_name="127.0.0.1",  # Localhost only
    server_port=7860,
    share=False  # No public URL
)
```

**Authentication** (add password protection):
```python
app.launch(
    server_name="0.0.0.0",
    server_port=7860,
    share=True,
    auth=("username", "password")  # Basic auth
)
```

### Data Storage Locations

**Default directories** (created automatically):
```
data/
├── papers/          # Downloaded PDFs
├── videos/          # Video metadata and transcripts
├── podcasts/        # Podcast episode data
└── processed/       # Processed content ready for indexing
```

**Change data location** (edit collector classes):
```python
# In data_collectors/paper_collector.py
self.download_dir = "custom_papers_location"
```

### Embedding Model Configuration

**Default model**: `all-MiniLM-L6-v2`
- Dimension: 384
- Speed: Fast
- Quality: Good for most use cases

**Change model** (in `opensearch_manager.py`):
```python
# Higher quality, slower
self.embedding_model = SentenceTransformer('all-mpnet-base-v2')  # 768 dim

# Faster, lower quality
self.embedding_model = SentenceTransformer('all-MiniLM-L12-v2')  # 384 dim
```

**Important**: If you change the embedding model, you must:
1. Update the dimension in index mapping
2. Delete and recreate the index
3. Re-index all documents

---

## Advanced Configuration

### Hybrid Search Parameters

**Defined in**: `multi_modal_rag/indexing/opensearch_manager.py`

**Search query structure**:
```python
query = {
    "query": {
        "bool": {
            "should": [
                # Keyword search (BM25)
                {
                    "multi_match": {
                        "query": query_text,
                        "fields": ["title^2", "abstract", "content", "transcript"],
                        "type": "best_fields"
                    }
                },
                # Vector similarity search
                {
                    "knn": {
                        "embedding": {
                            "vector": query_embedding,
                            "k": 10
                        }
                    }
                }
            ]
        }
    }
}
```

**Adjust field weights**:
```python
"fields": ["title^3", "abstract^2", "content", "transcript"]
# title is 3x more important
# abstract is 2x more important
```

**Change k-NN neighbors**:
```python
"k": 20  # Consider top 20 nearest neighbors instead of 10
```

### LangChain Configuration

**Memory settings** (in `research_orchestrator.py`):
```python
# Current: Last 10 messages
self.memory = ConversationBufferWindowMemory(k=10)

# More context (uses more tokens)
self.memory = ConversationBufferWindowMemory(k=20)

# Full conversation history
self.memory = ConversationBufferMemory()
```

**Prompt template customization**:
```python
# Edit in research_orchestrator.py
RESEARCH_TEMPLATE = """
Custom instructions here...

Context: {context}
Question: {question}
"""
```

### PDF Processing Configuration

**Defined in**: `multi_modal_rag/data_processors/pdf_processor.py`

**Diagram extraction settings**:
- Currently uses Gemini Vision for analysis
- Can be configured to extract specific image types
- Adjustable image resolution and quality

**Text extraction**:
- Uses PyPDF2 and PyMuPDF
- Fallback mechanisms for different PDF formats

---

## Performance Tuning

### Memory Optimization

**OpenSearch JVM heap**:
```bash
# Start with more memory
docker run -d \
  -e "OPENSEARCH_JAVA_OPTS=-Xms2g -Xmx2g" \
  opensearchproject/opensearch:latest
```

**Python process**:
- Process documents in batches
- Clear memory between large operations
- Use generators for large datasets

### Indexing Performance

**Bulk indexing** (already implemented):
```python
# Batch multiple documents
helpers.bulk(client, actions, chunk_size=100)
```

**Optimize for speed**:
```python
# Reduce replicas during bulk indexing
index_settings = {
    'number_of_shards': 2,
    'number_of_replicas': 0,  # Restore to 1 after indexing
    'refresh_interval': '30s'  # Default is 1s
}
```

### Query Performance

**Limit result size**:
```python
# In hybrid_search()
results = self.client.search(
    index=index_name,
    body=query,
    size=5  # Return top 5 instead of 10
)
```

**Cache embeddings**:
- Embeddings are generated once during indexing
- Reused for all searches (already optimized)

### Network Optimization

**OpenSearch connection pooling** (already enabled):
```python
http_compress=True  # Compress HTTP traffic
```

**Timeout tuning**:
```python
timeout=30  # Increase for slow networks
```

---

## Security Considerations

### API Key Security

**Best practices**:
1. Never commit `.env` to version control (already in `.gitignore`)
2. Use separate API keys for development/production
3. Rotate keys periodically
4. Limit API key permissions when possible

**Environment-specific keys**:
```bash
# Development
GEMINI_API_KEY=dev_key_here

# Production
GEMINI_API_KEY=prod_key_here
```

### OpenSearch Security

**Production recommendations**:
1. **Enable SSL certificate verification**:
   ```python
   verify_certs=True,
   ssl_assert_hostname=True
   ```

2. **Use strong passwords**:
   ```bash
   OPENSEARCH_INITIAL_ADMIN_PASSWORD=VeryStr0ng!P@ssw0rd#2024
   ```

3. **Network security**:
   - Don't expose OpenSearch port (9200) publicly
   - Use firewall rules
   - Run on private network

4. **Authentication**:
   - Change default admin credentials
   - Create role-based access
   - Use separate users for read/write operations

### Gradio UI Security

**For production**:
```python
app.launch(
    server_name="127.0.0.1",  # Localhost only
    share=False,              # No public URL
    auth=("admin", "secure_password"),  # Require authentication
    ssl_keyfile="path/to/key.pem",
    ssl_certfile="path/to/cert.pem"
)
```

**Behind reverse proxy** (recommended):
- Use nginx or Apache as reverse proxy
- Handle SSL/TLS termination at proxy
- Add rate limiting
- Implement authentication at proxy level

### Data Privacy

**Sensitive data handling**:
1. Review PDFs before indexing (no proprietary content)
2. Clear conversation history regularly
3. Don't index personal or confidential information
4. Consider data retention policies

**Local-first approach**:
- All data stored locally by default
- No data sent to third parties except API calls
- OpenSearch runs on your machine
- Control your own data

---

## Configuration Checklist

### Initial Setup
- [ ] Copy `.env.example` to `.env`
- [ ] Add Gemini API key
- [ ] Configure OpenSearch host/port
- [ ] Start OpenSearch container
- [ ] Verify connection in Settings tab

### Production Deployment
- [ ] Use strong OpenSearch password
- [ ] Enable SSL certificate verification
- [ ] Set up Gradio authentication
- [ ] Configure firewall rules
- [ ] Set up log rotation
- [ ] Configure backups for OpenSearch data
- [ ] Use environment-specific API keys
- [ ] Implement rate limiting
- [ ] Set up monitoring and alerts

### Performance Optimization
- [ ] Adjust OpenSearch JVM heap size
- [ ] Configure index refresh interval
- [ ] Tune k-NN parameters
- [ ] Optimize field weights for your use case
- [ ] Set appropriate timeout values
- [ ] Enable HTTP compression

### Maintenance
- [ ] Regular log cleanup
- [ ] Periodic API key rotation
- [ ] Index optimization
- [ ] Data backup schedule
- [ ] Update dependencies regularly

---

## Troubleshooting Configuration Issues

### Issue: Changes to .env not taking effect

**Solution**:
1. Restart the application (Ctrl+C and run `python main.py` again)
2. Verify `.env` is in project root directory
3. Check for syntax errors (no quotes, no spaces around `=`)
4. Ensure variable names are spelled correctly

### Issue: OpenSearch connection fails with SSL error

**Solution**:
1. Check `verify_certs=False` in opensearch_manager.py
2. Verify OpenSearch is running: `docker ps`
3. Test connection: `curl -k https://localhost:9200`
4. Check firewall settings

### Issue: Logs not being created

**Solution**:
1. Verify `logs/` directory exists and is writable
2. Check disk space
3. Review file permissions
4. Check logging configuration in `logging_config.py`

### Issue: Out of memory during PDF processing

**Solution**:
1. Increase Docker memory limit
2. Process fewer documents at once
3. Reduce OpenSearch JVM heap size if needed
4. Close other applications

---

## Next Steps

After configuring your system:

1. **Test Configuration**: Run through [Quick Start Guide](quick-start.md) to verify everything works
2. **Explore Features**: Learn about the system in [Technology Stack](../architecture/technology-stack.md)
3. **Optimize**: Use this guide to tune performance for your use case
4. **Monitor**: Check logs regularly for issues

---

**Your Multi-Modal Academic Research System is now fully configured and ready for production use!**
