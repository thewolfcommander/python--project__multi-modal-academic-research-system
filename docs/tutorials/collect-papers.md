# Tutorial: Collecting Academic Papers

This tutorial provides step-by-step instructions for collecting academic papers using the Multi-Modal Academic Research System. You'll learn how to use both the Gradio UI and Python API directly to gather papers from multiple sources.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Using the Gradio UI](#using-the-gradio-ui)
3. [Using the Python API](#using-the-python-api)
4. [Different Search Strategies](#different-search-strategies)
5. [Troubleshooting](#troubleshooting)

## Prerequisites

Before collecting papers, ensure:

1. Your virtual environment is activated:
   ```bash
   source venv/bin/activate  # Mac/Linux
   venv\Scripts\activate     # Windows
   ```

2. OpenSearch is running (for automatic indexing):
   ```bash
   docker run -p 9200:9200 -e "discovery.type=single-node" opensearchproject/opensearch:latest
   ```

3. Your `.env` file contains your Gemini API key:
   ```
   GEMINI_API_KEY=your_api_key_here
   OPENSEARCH_HOST=localhost
   OPENSEARCH_PORT=9200
   ```

## Using the Gradio UI

### Step 1: Launch the Application

Start the main application:

```bash
python main.py
```

You should see output like:
```
Starting Multi-Modal Research Assistant Application
Connected to OpenSearch at localhost:9200
Research Assistant ready!
Opening web interface...
Running on local URL: http://0.0.0.0:7860
Running on public URL: https://xxxxx.gradio.live
```

### Step 2: Navigate to Data Collection Tab

1. Open the local URL (`http://localhost:7860`) in your web browser
2. Click on the **"Data Collection"** tab at the top
3. You'll see three main sections:
   - Left panel: Collection options and controls
   - Right panel: Status updates and results

### Step 3: Configure Your Search

**Select Data Source:**
- Choose **"ArXiv Papers"** from the radio button options
- Other options include "YouTube Lectures" and "Podcasts"

**Enter Search Query:**
- Type your research topic in the "Search Query" field
- Examples:
  - `machine learning`
  - `quantum computing`
  - `natural language processing`
  - `computer vision transformers`

**Set Maximum Results:**
- Use the slider to choose how many papers to collect (5-100)
- Start with 10-20 for testing
- Note: Larger values take longer to process

### Step 4: Collect Papers

1. Click the **"Collect Data"** button
2. Watch the status updates in the "Collection Status" box:
   ```
   Collecting papers from ArXiv...
   Collected 15 papers

   Indexing data into OpenSearch...
   Indexed 15 items into OpenSearch

   Collection and indexing complete!
   ```

3. Review the results in the "Collection Results" JSON output:
   ```json
   {
     "papers_collected": 15,
     "items_indexed": 15
   }
   ```

### Step 5: Verify Collection

**Option 1: Check the Data Visualization Tab**
1. Click on the **"Data Visualization"** tab
2. Click **"Refresh Statistics"**
3. You should see your newly collected papers in the totals

**Option 2: Use the Research Tab**
1. Go to the **"Research"** tab
2. Enter a query related to your collected papers
3. The system should retrieve relevant papers from your collection

### What Happens Behind the Scenes

When you collect papers via the UI:

1. **Collection Phase:**
   - System queries the ArXiv API with your search terms
   - Downloads PDFs to `data/papers/` directory
   - Extracts metadata (title, authors, abstract, etc.)

2. **Database Tracking:**
   - Each paper is logged in the SQLite database
   - Collection statistics are recorded
   - Metadata is stored for future reference

3. **Indexing Phase:**
   - Paper content is formatted for OpenSearch
   - Embeddings are generated using SentenceTransformer
   - Documents are bulk-indexed for fast retrieval

4. **Completion:**
   - Papers marked as indexed in the database
   - Ready for searching and querying

## Using the Python API

For more control or automation, use the Python API directly.

### Basic Example

Create a Python script (`collect_papers.py`):

```python
from dotenv import load_dotenv
from multi_modal_rag.data_collectors.paper_collector import AcademicPaperCollector
from multi_modal_rag.indexing.opensearch_manager import OpenSearchManager
from multi_modal_rag.database import CollectionDatabaseManager

# Load environment variables
load_dotenv()

# Initialize components
paper_collector = AcademicPaperCollector()
opensearch_manager = OpenSearchManager()
db_manager = CollectionDatabaseManager()

# Collect papers from ArXiv
query = "deep learning neural networks"
max_results = 20

print(f"Collecting papers for: {query}")
papers = paper_collector.collect_arxiv_papers(query, max_results)

print(f"Collected {len(papers)} papers")

# Process and track each paper
for paper in papers:
    # Add to database
    collection_id = db_manager.add_collection(
        content_type='paper',
        title=paper['title'],
        source='arxiv',
        url=paper.get('pdf_url', ''),
        metadata={'query': query}
    )

    # Store paper details
    db_manager.add_paper(collection_id, paper)

    # Index in OpenSearch
    document = {
        'content_type': 'paper',
        'title': paper['title'],
        'abstract': paper['abstract'],
        'authors': paper['authors'],
        'url': paper.get('pdf_url', ''),
        'publication_date': paper['published'],
        'metadata': {
            'arxiv_id': paper['arxiv_id'],
            'categories': paper['categories']
        }
    }

    opensearch_manager.index_document('research_assistant', document)
    db_manager.mark_as_indexed(collection_id)

    print(f"  - {paper['title'][:80]}...")

# Log collection statistics
db_manager.log_collection_stats('paper', query, len(papers), 'arxiv')

print("Collection complete!")
```

Run the script:

```bash
python collect_papers.py
```

### Advanced Example: Batch Collection

Collect papers for multiple topics:

```python
from multi_modal_rag.data_collectors.paper_collector import AcademicPaperCollector
from multi_modal_rag.indexing.opensearch_manager import OpenSearchManager
from multi_modal_rag.database import CollectionDatabaseManager
from dotenv import load_dotenv
import time

load_dotenv()

# Initialize
paper_collector = AcademicPaperCollector()
opensearch_manager = OpenSearchManager()
db_manager = CollectionDatabaseManager()

# Define topics
topics = [
    "transformer architecture attention mechanisms",
    "reinforcement learning robotics",
    "graph neural networks",
    "few-shot learning meta-learning",
    "generative adversarial networks"
]

# Collect for each topic
for topic in topics:
    print(f"\nCollecting papers for: {topic}")

    papers = paper_collector.collect_arxiv_papers(topic, max_results=10)

    # Prepare documents for bulk indexing
    documents = []
    for paper in papers:
        # Track in database
        collection_id = db_manager.add_collection(
            content_type='paper',
            title=paper['title'],
            source='arxiv',
            url=paper.get('pdf_url', ''),
            metadata={'query': topic, 'categories': paper['categories']}
        )
        db_manager.add_paper(collection_id, paper)

        # Prepare for indexing
        doc = {
            'content_type': 'paper',
            'title': paper['title'],
            'abstract': paper['abstract'],
            'authors': paper['authors'],
            'url': paper.get('pdf_url', ''),
            'publication_date': paper['published'],
            'metadata': {
                'arxiv_id': paper['arxiv_id'],
                'categories': paper['categories']
            }
        }
        documents.append(doc)

    # Bulk index
    if documents:
        opensearch_manager.bulk_index('research_assistant', documents)
        print(f"Indexed {len(documents)} papers")

        # Mark as indexed
        for paper in papers:
            # Get collection_id and mark
            pass  # Simplified for brevity

    # Log stats
    db_manager.log_collection_stats('paper', topic, len(papers), 'arxiv')

    # Be respectful to the API
    time.sleep(3)

print("\nBatch collection complete!")
```

### Using Collection Filters

Filter papers by specific criteria:

```python
# Collect only recent papers (ArXiv example)
papers = paper_collector.collect_arxiv_papers(
    "machine learning",
    max_results=50
)

# Filter by publication year
from datetime import datetime, timedelta

recent_papers = [
    p for p in papers
    if datetime.fromisoformat(p['published']) > datetime.now() - timedelta(days=365)
]

print(f"Found {len(recent_papers)} papers from the last year")

# Filter by category
ml_papers = [
    p for p in papers
    if any(cat.startswith('cs.LG') for cat in p['categories'])
]

print(f"Found {len(ml_papers)} machine learning papers")
```

## Different Search Strategies

### 1. ArXiv Papers

**Best for:** Computer science, physics, mathematics, quantitative biology

**Search Tips:**
- Use specific technical terms: `"attention mechanisms"` instead of `"AI"`
- Include category codes: `cat:cs.LG` for machine learning
- Use Boolean operators: `machine learning AND interpretability`
- Filter by date: `submittedDate:[20230101 TO 20231231]`

**Example Searches:**
```python
# Specific subfield
papers = paper_collector.collect_arxiv_papers(
    "cat:cs.CV AND (object detection OR semantic segmentation)",
    max_results=30
)

# Recent papers on a topic
papers = paper_collector.collect_arxiv_papers(
    "large language models AND submittedDate:[20230101 TO *]",
    max_results=50
)

# Papers by specific author
papers = paper_collector.collect_arxiv_papers(
    "au:Hinton AND cat:cs.LG",
    max_results=20
)
```

### 2. Semantic Scholar

**Best for:** Open access papers across all disciplines

**Search Tips:**
- Broader coverage than ArXiv
- Automatically filters for open access PDFs
- Good for interdisciplinary research

**Example:**
```python
# Collect from Semantic Scholar
papers = paper_collector.collect_semantic_scholar(
    "climate change machine learning",
    max_results=30
)

# Filter for papers with PDFs
papers_with_pdfs = [p for p in papers if p.get('pdf_url')]
```

### 3. PubMed Central

**Best for:** Biomedical and life sciences research

**Search Tips:**
- Use MeSH terms for better results
- Filter for open access content
- Combine with Boolean operators

**Example:**
```python
# Collect biomedical papers
papers = paper_collector.collect_pubmed_central(
    "CRISPR gene editing",
    max_results=25
)

# Search with MeSH terms
papers = paper_collector.collect_pubmed_central(
    '"Machine Learning"[MeSH] AND "Cancer"[MeSH]',
    max_results=30
)
```

### 4. Combined Strategy

Collect from multiple sources:

```python
from multi_modal_rag.data_collectors.paper_collector import AcademicPaperCollector

collector = AcademicPaperCollector()
all_papers = []

# Collect from ArXiv
arxiv_papers = collector.collect_arxiv_papers("neural networks", 20)
all_papers.extend(arxiv_papers)

# Collect from Semantic Scholar
ss_papers = collector.collect_semantic_scholar("neural networks", 20)
all_papers.extend(ss_papers)

# Collect from PubMed Central (if biomedical topic)
pmc_papers = collector.collect_pubmed_central("neural networks medical imaging", 15)
all_papers.extend(pmc_papers)

# Deduplicate by title
unique_papers = []
seen_titles = set()

for paper in all_papers:
    title = paper['title'].lower().strip()
    if title not in seen_titles:
        unique_papers.append(paper)
        seen_titles.add(title)

print(f"Collected {len(unique_papers)} unique papers from {len(all_papers)} total")
```

## Troubleshooting

### Common Issues and Solutions

#### Issue 1: No Papers Collected

**Symptoms:**
```
Collected 0 papers
```

**Solutions:**
1. **Check your query:** Make it more general
   ```python
   # Too specific
   papers = collector.collect_arxiv_papers("very specific rare topic XYZ123", 50)

   # Better
   papers = collector.collect_arxiv_papers("machine learning", 50)
   ```

2. **Verify internet connection:** ArXiv requires network access
   ```bash
   curl https://arxiv.org
   ```

3. **Check for API rate limits:** Add delays between requests
   ```python
   import time
   time.sleep(3)  # Wait 3 seconds between collections
   ```

#### Issue 2: OpenSearch Not Available

**Symptoms:**
```
Cannot index document - OpenSearch not connected
```

**Solutions:**
1. **Start OpenSearch:**
   ```bash
   docker run -p 9200:9200 -e "discovery.type=single-node" opensearchproject/opensearch:latest
   ```

2. **Verify OpenSearch is running:**
   ```bash
   curl http://localhost:9200
   ```

3. **Check your .env file:**
   ```
   OPENSEARCH_HOST=localhost
   OPENSEARCH_PORT=9200
   ```

#### Issue 3: PDF Download Failures

**Symptoms:**
```
Error downloading PDF for paper: Connection timeout
```

**Solutions:**
1. **Increase timeout in paper_collector.py:**
   ```python
   result.download_pdf(dirpath=self.save_dir, timeout=120)
   ```

2. **Skip PDFs and index metadata only:**
   ```python
   # Don't download PDFs, just index metadata
   for result in search.results():
       paper_data = {
           'title': result.title,
           'abstract': result.summary,
           # ... other metadata
           'local_path': None  # Skip PDF download
       }
       papers.append(paper_data)
   ```

3. **Check disk space:**
   ```bash
   df -h data/papers/
   ```

#### Issue 4: Duplicate Papers

**Symptoms:**
Multiple copies of the same paper in search results

**Solutions:**
1. **Implement deduplication:**
   ```python
   def deduplicate_papers(papers):
       seen = set()
       unique = []

       for paper in papers:
           # Use arxiv_id or URL as unique identifier
           identifier = paper.get('arxiv_id') or paper.get('pdf_url')

           if identifier and identifier not in seen:
               seen.add(identifier)
               unique.append(paper)

       return unique

   papers = deduplicate_papers(collected_papers)
   ```

2. **Check database for existing entries:**
   ```python
   from multi_modal_rag.database import CollectionDatabaseManager

   db = CollectionDatabaseManager()

   # Before adding, check if URL exists
   existing = db.search_collections(paper['pdf_url'], limit=1)
   if not existing:
       # Add paper
       pass
   ```

#### Issue 5: Memory Issues with Large Collections

**Symptoms:**
```
MemoryError: Unable to allocate array
```

**Solutions:**
1. **Process papers in batches:**
   ```python
   batch_size = 10
   total_papers = 100

   for i in range(0, total_papers, batch_size):
       batch_papers = collector.collect_arxiv_papers(
           query,
           max_results=min(batch_size, total_papers - i)
       )

       # Process batch
       opensearch_manager.bulk_index('research_assistant', batch_papers)

       # Clear memory
       del batch_papers
   ```

2. **Reduce embedding model memory:**
   ```python
   # Use smaller model
   from sentence_transformers import SentenceTransformer
   model = SentenceTransformer('all-MiniLM-L6-v2')  # Smaller, faster
   ```

#### Issue 6: Slow Collection

**Symptoms:**
Collecting papers takes a very long time

**Solutions:**
1. **Reduce max_results:**
   ```python
   # Instead of
   papers = collector.collect_arxiv_papers(query, max_results=100)

   # Try
   papers = collector.collect_arxiv_papers(query, max_results=20)
   ```

2. **Skip PDF processing (index metadata only):**
   ```python
   # Modify collection to skip downloads
   for result in search.results():
       # Don't call result.download_pdf()
       papers.append(metadata_only)
   ```

3. **Use parallel processing:**
   ```python
   from concurrent.futures import ThreadPoolExecutor

   def collect_batch(query_batch):
       return collector.collect_arxiv_papers(query_batch, 10)

   queries = ["ML topic 1", "ML topic 2", "ML topic 3"]

   with ThreadPoolExecutor(max_workers=3) as executor:
       results = list(executor.map(collect_batch, queries))
   ```

### Getting Help

If you encounter issues not covered here:

1. **Check the logs:**
   ```bash
   tail -f logs/research_assistant_YYYYMMDD_HHMMSS.log
   ```

2. **Enable debug logging:**
   Edit `multi_modal_rag/logging_config.py` and set level to `DEBUG`

3. **Test components individually:**
   ```python
   # Test collector
   from multi_modal_rag.data_collectors.paper_collector import AcademicPaperCollector
   collector = AcademicPaperCollector()
   papers = collector.collect_arxiv_papers("test", 1)
   print(papers)

   # Test OpenSearch
   from multi_modal_rag.indexing.opensearch_manager import OpenSearchManager
   manager = OpenSearchManager()
   print(manager.connected)
   ```

4. **Check database integrity:**
   ```python
   from multi_modal_rag.database import CollectionDatabaseManager
   db = CollectionDatabaseManager()
   stats = db.get_statistics()
   print(stats)
   ```

## Best Practices

1. **Start Small:** Begin with 10-20 papers to test your setup
2. **Use Specific Queries:** More specific queries yield better results
3. **Monitor Resources:** Watch disk space and memory usage
4. **Regular Backups:** Backup your `data/` directory regularly
5. **Respect APIs:** Use appropriate delays between requests
6. **Verify Indexing:** Always check that papers are indexed successfully
7. **Track Collections:** Use the database to avoid duplicate collections

## Next Steps

- Learn about [Custom Searches](custom-searches.md) to query your collected papers
- Explore [Exporting Citations](export-citations.md) for research writing
- Check [Visualization Dashboard](visualization.md) to analyze your collection
- Read [Extending the System](extending.md) to add new data sources
