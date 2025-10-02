# Database Module

## Overview

The Database module provides SQLite-based tracking for all collected academic content. It maintains a comprehensive record of papers, videos, and podcasts, including collection metadata, indexing status, and usage statistics.

## Module Architecture

```
multi_modal_rag/database/
└── db_manager.py    # SQLite database manager
```

---

## CollectionDatabaseManager

**File**: `multi_modal_rag/database/db_manager.py`

### Class Overview

Manages a SQLite database for tracking collected research data, providing CRUD operations, search functionality, and analytics.

### Database Location

**Default Path**: `data/collections.db`

The database file is automatically created with all necessary tables on first initialization.

### Initialization

```python
from multi_modal_rag.database import CollectionDatabaseManager

db_manager = CollectionDatabaseManager(db_path="data/collections.db")
```

**Parameters**:
- `db_path` (str, optional): Path to SQLite database file. Default: `"data/collections.db"`

**Automatic Setup**:
- Creates directory if it doesn't exist
- Initializes database schema automatically
- Creates all tables on first run

---

## Database Schema

### Tables Overview

```
collections.db
├── collections         # Main collection tracking
├── papers             # Paper-specific data
├── videos             # Video-specific data
├── podcasts           # Podcast-specific data
└── collection_stats   # Collection analytics
```

---

### Collections Table

Main table tracking all collected items across content types.

```sql
CREATE TABLE collections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content_type TEXT NOT NULL,           -- 'paper', 'video', 'podcast'
    title TEXT NOT NULL,
    source TEXT,                           -- 'arxiv', 'youtube', 'rss', etc.
    url TEXT,
    collection_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT,                         -- JSON string
    status TEXT DEFAULT 'collected',       -- 'collected', 'processed', 'indexed'
    indexed BOOLEAN DEFAULT 0              -- 0 = not indexed, 1 = indexed
)
```

**Fields**:
- `id`: Unique identifier (auto-increment)
- `content_type`: Type of content (paper/video/podcast)
- `title`: Content title
- `source`: Source API/platform (arxiv, youtube, rss, etc.)
- `url`: Original URL
- `collection_date`: When item was collected (auto-set)
- `metadata`: JSON string with additional metadata
- `status`: Processing status
- `indexed`: Whether item is indexed in OpenSearch

---

### Papers Table

Stores paper-specific metadata.

```sql
CREATE TABLE papers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    collection_id INTEGER,                 -- Foreign key to collections
    arxiv_id TEXT,
    pmc_id TEXT,
    abstract TEXT,
    authors TEXT,                          -- JSON array
    published_date TEXT,
    categories TEXT,                       -- JSON array
    pdf_path TEXT,
    FOREIGN KEY (collection_id) REFERENCES collections(id)
)
```

**Fields**:
- `collection_id`: Links to main collections table
- `arxiv_id`: ArXiv identifier (if applicable)
- `pmc_id`: PubMed Central ID (if applicable)
- `abstract`: Paper abstract
- `authors`: JSON array of author names
- `published_date`: Publication date (ISO format)
- `categories`: JSON array of categories/topics
- `pdf_path`: Local path to downloaded PDF

---

### Videos Table

Stores video-specific metadata.

```sql
CREATE TABLE videos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    collection_id INTEGER,                 -- Foreign key to collections
    video_id TEXT,                         -- YouTube video ID
    channel TEXT,                          -- Channel/uploader name
    duration INTEGER,                      -- Duration in seconds
    views INTEGER,                         -- View count
    thumbnail_url TEXT,
    transcript_available BOOLEAN DEFAULT 0,
    FOREIGN KEY (collection_id) REFERENCES collections(id)
)
```

**Fields**:
- `video_id`: YouTube video identifier
- `channel`: Channel name
- `duration`: Video length in seconds
- `views`: View count at collection time
- `thumbnail_url`: Thumbnail image URL
- `transcript_available`: Whether transcript was retrieved

---

### Podcasts Table

Stores podcast-specific metadata.

```sql
CREATE TABLE podcasts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    collection_id INTEGER,                 -- Foreign key to collections
    episode_id TEXT,
    podcast_name TEXT,
    audio_url TEXT,                        -- Direct audio file URL
    duration INTEGER,                      -- Duration in seconds
    FOREIGN KEY (collection_id) REFERENCES collections(id)
)
```

**Fields**:
- `episode_id`: Unique episode identifier
- `podcast_name`: Name of podcast show
- `audio_url`: Direct link to audio file
- `duration`: Episode length in seconds

---

### Collection Stats Table

Tracks collection operations for analytics.

```sql
CREATE TABLE collection_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content_type TEXT,                     -- 'paper', 'video', 'podcast'
    query TEXT,                            -- Search query used
    results_count INTEGER,                 -- Number of results
    collection_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source_api TEXT                        -- API used (arxiv, youtube, etc.)
)
```

**Purpose**: Tracks collection history for analytics and debugging.

---

## Methods

### Collection Management

#### `add_collection(content_type: str, title: str, source: str, url: str, metadata: Dict, indexed: bool = False) -> int`

Adds a new collection item to the database.

**Parameters**:
- `content_type` (str): 'paper', 'video', or 'podcast'
- `title` (str): Content title
- `source` (str): Source identifier (e.g., 'arxiv', 'youtube')
- `url` (str): Content URL
- `metadata` (Dict): Additional metadata (stored as JSON)
- `indexed` (bool, optional): Whether already indexed. Default: False

**Returns**: Collection ID (int) of the newly created record

**Example**:

```python
db_manager = CollectionDatabaseManager()

collection_id = db_manager.add_collection(
    content_type='paper',
    title='Attention Is All You Need',
    source='arxiv',
    url='https://arxiv.org/abs/1706.03762',
    metadata={
        'query': 'transformer models',
        'categories': ['cs.CL', 'cs.LG']
    },
    indexed=False
)

print(f"Created collection with ID: {collection_id}")
```

**Database Operations**:
1. Inserts record into `collections` table
2. Serializes `metadata` dict to JSON string
3. Returns auto-generated ID
4. Commits transaction automatically

**Error Handling**:
- Rolls back transaction on error
- Raises exception for database errors
- Logs error details

---

#### `add_paper(collection_id: int, paper_data: Dict)`

Adds paper-specific data linked to a collection.

**Parameters**:
- `collection_id` (int): ID from `add_collection()`
- `paper_data` (Dict): Paper metadata

```python
{
    'arxiv_id': str,              # Optional
    'pmc_id': str,                # Optional
    'abstract': str,
    'authors': List[str],
    'published': str,             # ISO date
    'categories': List[str],
    'local_path': str             # Path to PDF
}
```

**Example**:

```python
# Step 1: Add to main collections
collection_id = db_manager.add_collection(
    content_type='paper',
    title='BERT: Pre-training of Deep Bidirectional Transformers',
    source='arxiv',
    url='https://arxiv.org/abs/1810.04805',
    metadata={}
)

# Step 2: Add paper-specific details
paper_data = {
    'arxiv_id': '1810.04805',
    'abstract': 'We introduce a new language representation model...',
    'authors': ['Jacob Devlin', 'Ming-Wei Chang', 'Kenton Lee'],
    'published': '2018-10-11',
    'categories': ['cs.CL'],
    'local_path': 'data/papers/1810.04805.pdf'
}

db_manager.add_paper(collection_id, paper_data)
```

**Database Operations**:
- Inserts into `papers` table
- Serializes `authors` and `categories` to JSON
- Links via `collection_id` foreign key

---

#### `add_video(collection_id: int, video_data: Dict)`

Adds video-specific data.

**Parameters**:
- `collection_id` (int): ID from `add_collection()`
- `video_data` (Dict): Video metadata

```python
{
    'video_id': str,
    'author': str,              # Channel name
    'length': int,              # Duration in seconds
    'views': int,
    'thumbnail_url': str,
    'transcript': str           # Or None
}
```

**Example**:

```python
collection_id = db_manager.add_collection(
    content_type='video',
    title='Neural Networks Explained',
    source='youtube',
    url='https://youtube.com/watch?v=...',
    metadata={'query': 'deep learning'}
)

video_data = {
    'video_id': 'aircAruvnKk',
    'author': '3Blue1Brown',
    'length': 1140,
    'views': 5000000,
    'thumbnail_url': 'https://...',
    'transcript': 'Welcome to this video about neural networks...'
}

db_manager.add_video(collection_id, video_data)
```

---

#### `add_podcast(collection_id: int, podcast_data: Dict)`

Adds podcast-specific data.

**Parameters**:
- `collection_id` (int): ID from `add_collection()`
- `podcast_data` (Dict): Podcast metadata

```python
{
    'episode_id': str,
    'podcast_name': str,
    'audio_url': str,
    'duration': int              # Optional
}
```

**Example**:

```python
collection_id = db_manager.add_collection(
    content_type='podcast',
    title='The Future of AI with Yann LeCun',
    source='podcast',
    url='https://lexfridman.com/yann-lecun',
    metadata={'query': 'artificial intelligence'}
)

podcast_data = {
    'episode_id': 'lex_001',
    'podcast_name': 'Lex Fridman Podcast',
    'audio_url': 'https://media.blubrry.com/.../lex_001.mp3',
    'duration': 7200
}

db_manager.add_podcast(collection_id, podcast_data)
```

---

#### `mark_as_indexed(collection_id: int)`

Marks a collection item as indexed in OpenSearch.

**Parameters**:
- `collection_id` (int): ID to mark as indexed

**Example**:

```python
# After successful indexing
db_manager.mark_as_indexed(collection_id)

# Later, query indexed items
indexed_items = db_manager.get_all_collections()
for item in indexed_items:
    if item['indexed']:
        print(f"✅ {item['title']} - Indexed")
```

**Database Operation**:
```sql
UPDATE collections SET indexed = 1 WHERE id = ?
```

---

### Statistics and Logging

#### `log_collection_stats(content_type: str, query: str, results_count: int, source_api: str)`

Logs collection operation statistics.

**Parameters**:
- `content_type` (str): Type of content collected
- `query` (str): Search query used
- `results_count` (int): Number of results collected
- `source_api` (str): API source (arxiv, youtube, rss)

**Example**:

```python
# After collecting papers
papers = paper_collector.collect_arxiv_papers("quantum computing", max_results=50)

db_manager.log_collection_stats(
    content_type='paper',
    query='quantum computing',
    results_count=len(papers),
    source_api='arxiv'
)
```

**Usage**: Tracks collection patterns for analytics and debugging.

---

#### `get_statistics() -> Dict`

Retrieves comprehensive database statistics.

**Returns**: Dictionary with statistics:

```python
{
    'by_type': {                     # Count by content type
        'paper': int,
        'video': int,
        'podcast': int
    },
    'indexed': int,                  # Total indexed items
    'not_indexed': int,              # Total not indexed
    'recent_7_days': int,            # Items collected in last 7 days
    'collection_history': [          # Collection operation history
        {
            'type': str,
            'source': str,
            'total': int
        },
        # ... more stats
    ]
}
```

**Example**:

```python
stats = db_manager.get_statistics()

print(f"Total papers: {stats['by_type'].get('paper', 0)}")
print(f"Total videos: {stats['by_type'].get('video', 0)}")
print(f"Indexed: {stats['indexed']}")
print(f"Not indexed: {stats['not_indexed']}")
print(f"Recent (7 days): {stats['recent_7_days']}")

print("\nCollection History:")
for entry in stats['collection_history']:
    print(f"  {entry['type']} from {entry['source']}: {entry['total']}")
```

**SQL Queries Used**:

```sql
-- By type
SELECT content_type, COUNT(*) as count
FROM collections
GROUP BY content_type

-- Indexed vs not indexed
SELECT indexed, COUNT(*) as count
FROM collections
GROUP BY indexed

-- Recent collections
SELECT COUNT(*) FROM collections
WHERE collection_date >= datetime('now', '-7 days')

-- Collection history
SELECT content_type, source_api, SUM(results_count) as total
FROM collection_stats
GROUP BY content_type, source_api
```

---

### Retrieval Methods

#### `get_all_collections(limit: int = 100, offset: int = 0) -> List[Dict]`

Retrieves all collections with pagination.

**Parameters**:
- `limit` (int, optional): Maximum results. Default: 100
- `offset` (int, optional): Offset for pagination. Default: 0

**Returns**: List of collection dictionaries

**Example**:

```python
# Get first page (100 items)
collections = db_manager.get_all_collections(limit=100, offset=0)

# Get second page
collections_page2 = db_manager.get_all_collections(limit=100, offset=100)

for item in collections:
    print(f"{item['id']}: {item['title']} ({item['content_type']})")
    print(f"  Source: {item['source']}")
    print(f"  Indexed: {item['indexed']}")
    print(f"  Collected: {item['collection_date']}")
```

**Return Structure**:

```python
[
    {
        'id': int,
        'content_type': str,
        'title': str,
        'source': str,
        'url': str,
        'collection_date': str,
        'metadata': dict,          # Parsed from JSON
        'status': str,
        'indexed': bool
    },
    # ... more items
]
```

---

#### `get_collections_by_type(content_type: str, limit: int = 100) -> List[Dict]`

Retrieves collections filtered by content type.

**Parameters**:
- `content_type` (str): 'paper', 'video', or 'podcast'
- `limit` (int, optional): Maximum results. Default: 100

**Example**:

```python
# Get all papers
papers = db_manager.get_collections_by_type('paper', limit=50)

# Get all videos
videos = db_manager.get_collections_by_type('video', limit=30)

# Get all podcasts
podcasts = db_manager.get_collections_by_type('podcast')
```

---

#### `get_collection_with_details(collection_id: int) -> Optional[Dict]`

Retrieves complete details for a collection, including type-specific data.

**Parameters**:
- `collection_id` (int): Collection ID

**Returns**: Dict with all details, or `None` if not found

**Example**:

```python
details = db_manager.get_collection_with_details(collection_id=42)

if details:
    print(f"Title: {details['title']}")
    print(f"Type: {details['content_type']}")

    if details['content_type'] == 'paper':
        paper_details = details['details']
        print(f"Authors: {', '.join(paper_details['authors'])}")
        print(f"Abstract: {paper_details['abstract'][:200]}...")
        print(f"PDF: {paper_details['pdf_path']}")

    elif details['content_type'] == 'video':
        video_details = details['details']
        print(f"Channel: {video_details['channel']}")
        print(f"Duration: {video_details['duration']} seconds")
        print(f"Views: {video_details['views']}")
```

**Return Structure**:

```python
{
    # Main collection fields
    'id': int,
    'content_type': str,
    'title': str,
    # ... other collection fields

    # Type-specific details
    'details': {
        # For papers:
        'arxiv_id': str,
        'authors': List[str],      # Parsed from JSON
        'abstract': str,
        'categories': List[str],   # Parsed from JSON
        # ...

        # For videos:
        'video_id': str,
        'channel': str,
        'duration': int,
        # ...

        # For podcasts:
        'episode_id': str,
        'podcast_name': str,
        'audio_url': str,
        # ...
    }
}
```

---

#### `search_collections(query: str, limit: int = 50) -> List[Dict]`

Searches collections by title or source.

**Parameters**:
- `query` (str): Search query
- `limit` (int, optional): Maximum results. Default: 50

**Returns**: List of matching collections

**Example**:

```python
# Search by title
results = db_manager.search_collections("transformer")

# Search by source
arxiv_results = db_manager.search_collections("arxiv")

for item in results:
    print(f"{item['title']} ({item['content_type']})")
```

**SQL Query**:
```sql
SELECT * FROM collections
WHERE title LIKE ? OR source LIKE ?
ORDER BY collection_date DESC
LIMIT ?
```

**Search Behavior**:
- Case-insensitive (SQLite LIKE is case-insensitive by default)
- Partial matching (uses `%query%` pattern)
- Searches both `title` and `source` fields

---

## Integration Examples

### Complete Collection Workflow

```python
from multi_modal_rag.data_collectors import AcademicPaperCollector
from multi_modal_rag.database import CollectionDatabaseManager
from multi_modal_rag.indexing import OpenSearchManager

# Initialize
paper_collector = AcademicPaperCollector()
db_manager = CollectionDatabaseManager()
opensearch_manager = OpenSearchManager()

# Collect papers
query = "neural machine translation"
papers = paper_collector.collect_arxiv_papers(query, max_results=20)

# Track in database and index
for paper in papers:
    # 1. Add to database
    collection_id = db_manager.add_collection(
        content_type='paper',
        title=paper['title'],
        source='arxiv',
        url=paper['pdf_url'],
        metadata={'query': query, 'categories': paper['categories']}
    )

    db_manager.add_paper(collection_id, paper)

    # 2. Index in OpenSearch
    doc = {
        'content_type': 'paper',
        'title': paper['title'],
        'abstract': paper['abstract'],
        'authors': paper['authors'],
        # ... other fields
    }
    opensearch_manager.index_document('research_assistant', doc)

    # 3. Mark as indexed
    db_manager.mark_as_indexed(collection_id)

# 4. Log statistics
db_manager.log_collection_stats(
    content_type='paper',
    query=query,
    results_count=len(papers),
    source_api='arxiv'
)

# 5. View statistics
stats = db_manager.get_statistics()
print(f"Total collections: {sum(stats['by_type'].values())}")
print(f"Indexed: {stats['indexed']}")
```

### Analytics Dashboard

```python
# Get comprehensive statistics
stats = db_manager.get_statistics()

print("=== Collection Statistics ===")
print(f"\nBy Type:")
for content_type, count in stats['by_type'].items():
    print(f"  {content_type}: {count}")

print(f"\nIndexing Status:")
print(f"  Indexed: {stats['indexed']}")
print(f"  Not Indexed: {stats['not_indexed']}")
total = stats['indexed'] + stats['not_indexed']
if total > 0:
    print(f"  Percentage Indexed: {stats['indexed']/total*100:.1f}%")

print(f"\nRecent Activity:")
print(f"  Last 7 days: {stats['recent_7_days']} new items")

print(f"\nCollection History:")
for entry in stats['collection_history']:
    print(f"  {entry['type']} from {entry['source']}: {entry['total']} total")

# Get recent collections
recent = db_manager.get_all_collections(limit=10)
print("\n=== Recent Collections ===")
for item in recent:
    indexed_status = "✅" if item['indexed'] else "❌"
    print(f"{indexed_status} {item['title'][:50]}... ({item['content_type']})")
```

---

## Performance Considerations

### Database Size

**Typical Sizes**:
- 1,000 collections: ~2-5 MB
- 10,000 collections: ~20-50 MB
- 100,000 collections: ~200-500 MB

**Optimization**: SQLite handles these sizes efficiently on modern hardware.

### Query Performance

**Fast Queries** (with indexing):
- `get_all_collections()`: ~10-50ms (1000 records)
- `get_collections_by_type()`: ~5-20ms (filtered)
- `get_collection_with_details()`: ~2-10ms (single record)

**Slower Queries** (without indexing):
- `search_collections()`: ~50-200ms (LIKE query, 10K records)

**Optimization Tips**:

1. **Add Indexes**:
   ```python
   cursor.execute("""
       CREATE INDEX IF NOT EXISTS idx_content_type
       ON collections(content_type)
   """)

   cursor.execute("""
       CREATE INDEX IF NOT EXISTS idx_indexed
       ON collections(indexed)
   """)
   ```

2. **Limit Results**:
   ```python
   # Good: Limit to what you need
   collections = db_manager.get_all_collections(limit=100)

   # Bad: Loading thousands unnecessarily
   collections = db_manager.get_all_collections(limit=100000)
   ```

3. **Use Pagination**:
   ```python
   page_size = 50
   for page in range(total_pages):
       offset = page * page_size
       items = db_manager.get_all_collections(limit=page_size, offset=offset)
       process_items(items)
   ```

---

## Error Handling

### Transaction Rollback

All write operations use transactions with automatic rollback:

```python
def add_collection(self, ...):
    conn = sqlite3.connect(self.db_path)
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO collections ...")
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        logger.error(f"Error adding collection: {e}")
        conn.rollback()  # Rollback on error
        raise
    finally:
        conn.close()
```

### Handling Database Errors

```python
try:
    collection_id = db_manager.add_collection(...)
except sqlite3.IntegrityError as e:
    print(f"Duplicate entry: {e}")
except sqlite3.OperationalError as e:
    print(f"Database locked or unavailable: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

---

## Logging

All database operations are logged:

```python
from multi_modal_rag.logging_config import get_logger

logger = get_logger(__name__)
```

**Log Examples**:

```
INFO - CollectionDatabaseManager initialized with database at data/collections.db
INFO - Database schema initialized successfully
DEBUG - Added collection item: 42 - Attention Is All You Need
DEBUG - Added paper data for collection_id: 42
INFO - Successfully marked collection 42 as indexed
```

---

## Backup and Export

### Database Backup

```python
import shutil
from datetime import datetime

# Create backup
backup_path = f"data/backups/collections_{datetime.now():%Y%m%d_%H%M%S}.db"
shutil.copy2("data/collections.db", backup_path)
print(f"Backup created: {backup_path}")
```

### Export to JSON

```python
import json

# Export all collections
collections = db_manager.get_all_collections(limit=10000)

with open("collections_export.json", "w") as f:
    json.dump(collections, f, indent=2)

print(f"Exported {len(collections)} collections")
```

### Export to CSV

```python
import csv

collections = db_manager.get_all_collections(limit=10000)

with open("collections_export.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=['id', 'title', 'content_type', 'source', 'indexed'])
    writer.writeheader()
    for item in collections:
        writer.writerow({
            'id': item['id'],
            'title': item['title'],
            'content_type': item['content_type'],
            'source': item['source'],
            'indexed': item['indexed']
        })
```

---

## Dependencies

```python
import sqlite3
import json
from datetime import datetime
import os
```

**Installation**: Part of Python standard library (no external dependencies)

---

## Troubleshooting

### Issue: Database is locked

**Error**: `sqlite3.OperationalError: database is locked`

**Causes**:
- Another process has database open
- Long-running transaction
- Disk I/O issues

**Solutions**:
1. Ensure connections are closed:
   ```python
   conn.close()  # Always in finally block
   ```

2. Increase timeout:
   ```python
   conn = sqlite3.connect(db_path, timeout=30.0)
   ```

3. Use WAL mode (Write-Ahead Logging):
   ```python
   conn.execute("PRAGMA journal_mode=WAL")
   ```

### Issue: Corrupted database

**Symptoms**: `sqlite3.DatabaseError: database disk image is malformed`

**Recovery**:
```bash
# Attempt to recover
sqlite3 collections.db ".dump" | sqlite3 recovered.db
```

### Issue: Metadata JSON parse error

**Error**: `json.decoder.JSONDecodeError`

**Cause**: Invalid JSON in metadata field

**Solution**: Add error handling:
```python
try:
    metadata = json.loads(result['metadata'])
except json.JSONDecodeError:
    metadata = {}  # Fallback to empty dict
```

---

## Future Enhancements

### Planned Features

1. **Full-Text Search**: SQLite FTS5 for advanced text search
2. **Database Migrations**: Version tracking and schema updates
3. **Relationship Tracking**: Link related papers, citations
4. **Usage Analytics**: Track query patterns, popular content
5. **Archiving**: Move old collections to archive tables

### Extension Points

```python
# Add full-text search
def create_fts_index(self):
    """Create FTS5 virtual table for search"""
    pass

# Add relationship tracking
def add_citation_link(self, source_id: int, cited_id: int):
    """Track paper citations"""
    pass

# Add analytics
def get_popular_content(self, days: int = 30) -> List[Dict]:
    """Get most accessed content"""
    pass
```
