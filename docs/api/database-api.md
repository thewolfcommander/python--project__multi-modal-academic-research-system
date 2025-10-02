# Database API Reference

## Overview

The `CollectionDatabaseManager` class provides a Python API for interacting with the SQLite database that stores all collected research content. This is the primary interface for database operations in the Multi-Modal Academic Research System.

**Module**: `multi_modal_rag.database`
**Class**: `CollectionDatabaseManager`
**File**: `multi_modal_rag/database/db_manager.py`

## Importing

```python
from multi_modal_rag.database import CollectionDatabaseManager
```

---

## Class: CollectionDatabaseManager

### Constructor

#### `__init__(db_path: str = "data/collections.db")`

Initialize the database manager and create database schema if it doesn't exist.

**Parameters**:
- `db_path` (str, optional): Path to the SQLite database file. Defaults to `"data/collections.db"`

**Returns**: `CollectionDatabaseManager` instance

**Side Effects**:
- Creates database directory if it doesn't exist
- Initializes all database tables if they don't exist
- Logs initialization message

**Example**:

```python
from multi_modal_rag.database import CollectionDatabaseManager

# Use default database path
db = CollectionDatabaseManager()

# Use custom database path
db = CollectionDatabaseManager(db_path="custom/path/research.db")
```

**Raises**:
- `OSError`: If unable to create database directory
- `sqlite3.Error`: If database initialization fails

---

## Collection Management Methods

### `add_collection()`

#### `add_collection(content_type: str, title: str, source: str, url: str, metadata: Dict, indexed: bool = False) -> int`

Add a new collection item to the database.

**Parameters**:
- `content_type` (str): Type of content - must be `'paper'`, `'video'`, or `'podcast'`
- `title` (str): Title of the content
- `source` (str): Source platform (e.g., `'arxiv'`, `'youtube'`, `'podcast_rss'`)
- `url` (str): Original URL of the content
- `metadata` (Dict): Additional metadata as a dictionary (will be JSON-encoded)
- `indexed` (bool, optional): Whether content is indexed in OpenSearch. Defaults to `False`

**Returns**: `int` - The auto-generated collection ID

**Raises**:
- `Exception`: If database insertion fails (propagates after rollback)

**Example**:

```python
db = CollectionDatabaseManager()

# Add a paper
collection_id = db.add_collection(
    content_type='paper',
    title='Attention Is All You Need',
    source='arxiv',
    url='https://arxiv.org/abs/1706.03762',
    metadata={
        'keywords': ['transformers', 'attention'],
        'language': 'en'
    },
    indexed=False
)

print(f"Created collection with ID: {collection_id}")
```

**Notes**:
- The `metadata` dictionary is automatically JSON-encoded for storage
- `collection_date` is automatically set to current timestamp
- `status` is automatically set to `'collected'`

---

### `get_all_collections()`

#### `get_all_collections(limit: int = 100, offset: int = 0) -> List[Dict]`

Retrieve all collections with pagination support.

**Parameters**:
- `limit` (int, optional): Maximum number of results to return. Defaults to `100`
- `offset` (int, optional): Number of records to skip (for pagination). Defaults to `0`

**Returns**: `List[Dict]` - List of collection dictionaries, ordered by `collection_date` DESC

**Example**:

```python
# Get first 100 collections
collections = db.get_all_collections()

# Get next 100 collections (pagination)
collections_page2 = db.get_all_collections(limit=100, offset=100)

# Get only 10 collections
recent_collections = db.get_all_collections(limit=10)

for collection in collections:
    print(f"{collection['id']}: {collection['title']}")
    print(f"  Type: {collection['content_type']}")
    print(f"  Source: {collection['source']}")
    print(f"  Metadata: {collection['metadata']}")  # Already parsed from JSON
```

**Return Format**:

```python
[
    {
        'id': 1,
        'content_type': 'paper',
        'title': 'Attention Is All You Need',
        'source': 'arxiv',
        'url': 'https://arxiv.org/abs/1706.03762',
        'collection_date': '2025-10-01 10:30:00',
        'metadata': {'keywords': ['transformers']},  # Parsed from JSON
        'status': 'collected',
        'indexed': 1
    },
    ...
]
```

**Notes**:
- The `metadata` field is automatically parsed from JSON to a Python dictionary
- Results are ordered by `collection_date` in descending order (newest first)

---

### `get_collections_by_type()`

#### `get_collections_by_type(content_type: str, limit: int = 100) -> List[Dict]`

Retrieve collections filtered by content type.

**Parameters**:
- `content_type` (str): Type to filter by - must be `'paper'`, `'video'`, or `'podcast'`
- `limit` (int, optional): Maximum number of results. Defaults to `100`

**Returns**: `List[Dict]` - List of matching collection dictionaries, ordered by `collection_date` DESC

**Example**:

```python
# Get all papers
papers = db.get_collections_by_type('paper', limit=50)

# Get all videos
videos = db.get_collections_by_type('video')

# Get all podcasts
podcasts = db.get_collections_by_type('podcast', limit=20)

print(f"Found {len(papers)} papers")
for paper in papers:
    print(f"  - {paper['title']}")
```

**Return Format**: Same as `get_all_collections()`

---

### `get_collection_with_details()`

#### `get_collection_with_details(collection_id: int) -> Optional[Dict]`

Retrieve full collection details including type-specific data from related tables.

**Parameters**:
- `collection_id` (int): The unique ID of the collection

**Returns**:
- `Dict` - Collection dictionary with additional `'details'` key containing type-specific data
- `None` - If collection doesn't exist

**Example**:

```python
# Get paper with details
collection = db.get_collection_with_details(1)

if collection:
    print(f"Title: {collection['title']}")
    print(f"Type: {collection['content_type']}")

    # Type-specific details
    if collection['content_type'] == 'paper':
        details = collection['details']
        print(f"Authors: {', '.join(details['authors'])}")
        print(f"ArXiv ID: {details['arxiv_id']}")
        print(f"Abstract: {details['abstract'][:100]}...")
        print(f"PDF Path: {details['pdf_path']}")

    elif collection['content_type'] == 'video':
        details = collection['details']
        print(f"Channel: {details['channel']}")
        print(f"Video ID: {details['video_id']}")
        print(f"Duration: {details['duration']} seconds")
        print(f"Views: {details['views']}")

    elif collection['content_type'] == 'podcast':
        details = collection['details']
        print(f"Podcast: {details['podcast_name']}")
        print(f"Episode ID: {details['episode_id']}")
        print(f"Duration: {details['duration']} seconds")
else:
    print("Collection not found")
```

**Return Format for Paper**:

```python
{
    'id': 1,
    'content_type': 'paper',
    'title': 'Attention Is All You Need',
    'source': 'arxiv',
    'url': 'https://arxiv.org/abs/1706.03762',
    'collection_date': '2025-10-01 10:30:00',
    'metadata': {},
    'status': 'collected',
    'indexed': 1,
    'details': {
        'id': 1,
        'collection_id': 1,
        'arxiv_id': '1706.03762',
        'pmc_id': None,
        'abstract': 'The dominant sequence transduction models...',
        'authors': ['Ashish Vaswani', 'Noam Shazeer'],  # Parsed from JSON
        'published_date': '2017-06-12',
        'categories': ['cs.CL', 'cs.AI'],  # Parsed from JSON
        'pdf_path': 'data/papers/arxiv_1706.03762.pdf'
    }
}
```

**Notes**:
- For papers, `authors` and `categories` in details are automatically parsed from JSON
- If collection exists but has no type-specific record, `'details'` key will not be present

---

### `search_collections()`

#### `search_collections(query: str, limit: int = 50) -> List[Dict]`

Search collections by title or source using substring matching.

**Parameters**:
- `query` (str): Search query string
- `limit` (int, optional): Maximum number of results. Defaults to `50`

**Returns**: `List[Dict]` - List of matching collection dictionaries, ordered by `collection_date` DESC

**Example**:

```python
# Search for "transformer"
results = db.search_collections('transformer', limit=20)

# Search for "arxiv" (searches in source field too)
arxiv_papers = db.search_collections('arxiv')

# Search for "neural network"
nn_results = db.search_collections('neural network')

print(f"Found {len(results)} results")
for result in results:
    print(f"  {result['content_type']}: {result['title']}")
```

**Search Behavior**:
- Case-insensitive substring matching
- Searches both `title` AND `source` fields
- Uses SQL `LIKE '%query%'` pattern
- Returns results ordered by newest first

**Return Format**: Same as `get_all_collections()`

---

## Type-Specific Methods

### `add_paper()`

#### `add_paper(collection_id: int, paper_data: Dict)`

Add paper-specific data to the papers table.

**Parameters**:
- `collection_id` (int): ID of the parent collection record
- `paper_data` (Dict): Dictionary containing paper details

**Paper Data Fields**:
- `arxiv_id` (str, optional): ArXiv identifier
- `pmc_id` (str, optional): PubMed Central identifier
- `abstract` (str, optional): Paper abstract
- `authors` (List[str], optional): List of author names
- `published` (str, optional): Publication date
- `categories` (List[str], optional): List of category tags
- `local_path` (str, optional): Path to downloaded PDF

**Returns**: `None`

**Raises**:
- `Exception`: If database insertion fails (propagates after rollback)

**Example**:

```python
# First, create the collection
collection_id = db.add_collection(
    content_type='paper',
    title='Attention Is All You Need',
    source='arxiv',
    url='https://arxiv.org/abs/1706.03762',
    metadata={}
)

# Then add paper-specific details
db.add_paper(collection_id, {
    'arxiv_id': '1706.03762',
    'pmc_id': None,
    'abstract': 'The dominant sequence transduction models are based on complex recurrent or convolutional neural networks...',
    'authors': ['Ashish Vaswani', 'Noam Shazeer', 'Niki Parmar', 'Jakob Uszkoreit'],
    'published': '2017-06-12',
    'categories': ['cs.CL', 'cs.AI', 'cs.LG'],
    'local_path': 'data/papers/arxiv_1706.03762.pdf'
})
```

**Notes**:
- `authors` and `categories` lists are automatically JSON-encoded for storage
- All fields are optional (nullable in database)

---

### `add_video()`

#### `add_video(collection_id: int, video_data: Dict)`

Add video-specific data to the videos table.

**Parameters**:
- `collection_id` (int): ID of the parent collection record
- `video_data` (Dict): Dictionary containing video details

**Video Data Fields**:
- `video_id` (str, optional): YouTube video ID
- `author` (str, optional): Channel name (mapped to `channel` field)
- `length` (int, optional): Duration in seconds (mapped to `duration` field)
- `views` (int, optional): View count
- `thumbnail_url` (str, optional): Thumbnail image URL
- `transcript` (str/bool, optional): Transcript text or boolean indicating availability

**Returns**: `None`

**Raises**:
- `Exception`: If database insertion fails (propagates after rollback)

**Example**:

```python
# Create collection
collection_id = db.add_collection(
    content_type='video',
    title='Neural Networks Explained',
    source='youtube',
    url='https://youtube.com/watch?v=abc123',
    metadata={}
)

# Add video details
db.add_video(collection_id, {
    'video_id': 'abc123',
    'author': '3Blue1Brown',
    'length': 1194,
    'views': 5234891,
    'thumbnail_url': 'https://i.ytimg.com/vi/abc123/maxresdefault.jpg',
    'transcript': 'Hello and welcome to this video about neural networks...'
})
```

**Notes**:
- `author` is mapped to the `channel` database field
- `length` is mapped to the `duration` database field
- `transcript_available` is set based on whether `transcript` field is truthy
- All fields are optional (nullable in database)

---

### `add_podcast()`

#### `add_podcast(collection_id: int, podcast_data: Dict)`

Add podcast-specific data to the podcasts table.

**Parameters**:
- `collection_id` (int): ID of the parent collection record
- `podcast_data` (Dict): Dictionary containing podcast details

**Podcast Data Fields**:
- `episode_id` (str, optional): Unique episode identifier
- `podcast_name` (str, optional): Name of the podcast show
- `audio_url` (str, optional): Direct URL to audio file
- `duration` (int, optional): Episode duration in seconds

**Returns**: `None`

**Raises**:
- `Exception`: If database insertion fails (propagates after rollback)

**Example**:

```python
# Create collection
collection_id = db.add_collection(
    content_type='podcast',
    title='AI Safety Discussion - Episode 42',
    source='podcast_rss',
    url='https://podcast.ai/ep42',
    metadata={'language': 'en'}
)

# Add podcast details
db.add_podcast(collection_id, {
    'episode_id': 'ep-42',
    'podcast_name': 'AI Alignment Podcast',
    'audio_url': 'https://podcast.ai/audio/ep42.mp3',
    'duration': 3600
})
```

**Notes**:
- All fields are optional (nullable in database)

---

## Status Management Methods

### `mark_as_indexed()`

#### `mark_as_indexed(collection_id: int)`

Mark a collection item as indexed in OpenSearch.

**Parameters**:
- `collection_id` (int): The unique ID of the collection

**Returns**: `None`

**Raises**:
- `Exception`: If database update fails (propagates after rollback)

**Example**:

```python
# After successfully indexing in OpenSearch
collection_id = 42
db.mark_as_indexed(collection_id)

print(f"Collection {collection_id} marked as indexed")
```

**SQL Operation**:
```sql
UPDATE collections SET indexed = 1 WHERE id = ?
```

---

## Statistics Methods

### `get_statistics()`

#### `get_statistics() -> Dict`

Retrieve comprehensive database statistics.

**Parameters**: None

**Returns**: `Dict` containing various statistics

**Return Format**:

```python
{
    'by_type': {
        'paper': 1523,
        'video': 342,
        'podcast': 87
    },
    'indexed': 1845,
    'not_indexed': 107,
    'recent_7_days': 23,
    'collection_history': [
        {
            'type': 'paper',
            'source': 'arxiv',
            'total': 1200
        },
        {
            'type': 'paper',
            'source': 'pubmed',
            'total': 323
        },
        {
            'type': 'video',
            'source': 'youtube',
            'total': 342
        }
    ]
}
```

**Return Fields**:
- `by_type` (Dict[str, int]): Count of collections by content type
- `indexed` (int): Number of indexed collections
- `not_indexed` (int): Number of not-yet-indexed collections
- `recent_7_days` (int): Collections added in the last 7 days
- `collection_history` (List[Dict]): Aggregated collection stats by type and source

**Example**:

```python
stats = db.get_statistics()

print("Database Statistics:")
print(f"  Total Papers: {stats['by_type'].get('paper', 0)}")
print(f"  Total Videos: {stats['by_type'].get('video', 0)}")
print(f"  Total Podcasts: {stats['by_type'].get('podcast', 0)}")
print(f"  Indexed: {stats['indexed']}")
print(f"  Pending Indexing: {stats['not_indexed']}")
print(f"  Added Last 7 Days: {stats['recent_7_days']}")

print("\nCollection History:")
for item in stats['collection_history']:
    print(f"  {item['type']} from {item['source']}: {item['total']} items")
```

---

### `log_collection_stats()`

#### `log_collection_stats(content_type: str, query: str, results_count: int, source_api: str)`

Log statistics about a collection operation.

**Parameters**:
- `content_type` (str): Type of content collected
- `query` (str): Search query used
- `results_count` (int): Number of results returned by the API
- `source_api` (str): API source (e.g., `'arxiv'`, `'youtube_api'`)

**Returns**: `None`

**Raises**:
- `Exception`: If database insertion fails (propagates after rollback)

**Example**:

```python
# After collecting papers from ArXiv
db.log_collection_stats(
    content_type='paper',
    query='machine learning',
    results_count=25,
    source_api='arxiv'
)

# After collecting videos
db.log_collection_stats(
    content_type='video',
    query='neural networks',
    results_count=10,
    source_api='youtube_api'
)
```

**Usage**: This helps track which queries are being used, how many results are typically returned, and which APIs are most productive.

---

## Complete Usage Example

```python
from multi_modal_rag.database import CollectionDatabaseManager

# Initialize database
db = CollectionDatabaseManager()

# === Add a Paper ===
paper_collection_id = db.add_collection(
    content_type='paper',
    title='Attention Is All You Need',
    source='arxiv',
    url='https://arxiv.org/abs/1706.03762',
    metadata={'keywords': ['transformers', 'attention']},
    indexed=False
)

db.add_paper(paper_collection_id, {
    'arxiv_id': '1706.03762',
    'abstract': 'The dominant sequence transduction models...',
    'authors': ['Ashish Vaswani', 'Noam Shazeer'],
    'published': '2017-06-12',
    'categories': ['cs.CL', 'cs.AI'],
    'local_path': 'data/papers/1706.03762.pdf'
})

# Log the collection
db.log_collection_stats('paper', 'transformers', 1, 'arxiv')

# === Add a Video ===
video_collection_id = db.add_collection(
    content_type='video',
    title='Neural Networks Explained',
    source='youtube',
    url='https://youtube.com/watch?v=abc123',
    metadata={}
)

db.add_video(video_collection_id, {
    'video_id': 'abc123',
    'author': '3Blue1Brown',
    'length': 1194,
    'views': 5000000,
    'thumbnail_url': 'https://i.ytimg.com/vi/abc123/maxresdefault.jpg',
    'transcript': 'Hello and welcome...'
})

# === Query Collections ===

# Get all papers
papers = db.get_collections_by_type('paper', limit=10)
print(f"Found {len(papers)} papers")

# Search
results = db.search_collections('transformer')
print(f"Search found {len(results)} results")

# Get full details
details = db.get_collection_with_details(paper_collection_id)
print(f"Paper title: {details['title']}")
print(f"Authors: {', '.join(details['details']['authors'])}")

# === Mark as Indexed ===
db.mark_as_indexed(paper_collection_id)

# === Get Statistics ===
stats = db.get_statistics()
print(f"Total items: {sum(stats['by_type'].values())}")
print(f"Indexed: {stats['indexed']}, Pending: {stats['not_indexed']}")
```

---

## Error Handling

All methods that modify the database use try/except blocks with rollback:

```python
try:
    # Database operation
    conn.commit()
except Exception as e:
    logger.error(f"Error: {e}")
    conn.rollback()
    raise  # Re-raise exception
finally:
    conn.close()
```

**Best Practice**:

```python
try:
    collection_id = db.add_collection(...)
    db.add_paper(collection_id, {...})
except Exception as e:
    print(f"Failed to add paper: {e}")
    # Handle error appropriately
```

---

## Thread Safety

**Important**: SQLite connections are NOT thread-safe by default. Each method creates its own connection and closes it, which is safe for multi-threaded use, but **not optimal for performance**.

For high-concurrency scenarios, consider:
1. Using connection pooling
2. Implementing a connection-per-thread pattern
3. Using a more robust database (PostgreSQL, MySQL)

---

## Performance Considerations

### Indexing

For better performance with large datasets:

```python
import sqlite3

conn = sqlite3.connect('data/collections.db')
cursor = conn.cursor()

# Add indexes
cursor.execute("CREATE INDEX IF NOT EXISTS idx_content_type ON collections(content_type)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_indexed ON collections(indexed)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_collection_date ON collections(collection_date DESC)")

conn.commit()
conn.close()
```

### Batch Operations

For inserting many items, use transactions:

```python
import sqlite3

conn = sqlite3.connect('data/collections.db')
cursor = conn.cursor()

try:
    # Disable autocommit for batch insert
    for paper_data in large_paper_list:
        cursor.execute("INSERT INTO collections ...")
        # ... more inserts

    conn.commit()  # Commit all at once
except:
    conn.rollback()
    raise
finally:
    conn.close()
```

### Query Optimization

- Use `LIMIT` to avoid loading too many records
- Add appropriate indexes on frequently queried fields
- Use `EXPLAIN QUERY PLAN` to analyze slow queries

---

## Backup and Recovery

```python
import sqlite3
import shutil
from datetime import datetime

# Simple file backup
shutil.copy('data/collections.db', f'data/backup_{datetime.now().strftime("%Y%m%d")}.db')

# SQLite backup API (online backup)
source = sqlite3.connect('data/collections.db')
dest = sqlite3.connect('data/backup.db')
source.backup(dest)
dest.close()
source.close()
```
