# Database Schema Documentation

## Overview

The Multi-Modal Academic Research System uses SQLite as its database backend to track all collected research content. The database is located at `data/collections.db` by default and consists of 5 main tables that work together to store papers, videos, podcasts, and collection statistics.

## Database Manager

**Class**: `CollectionDatabaseManager`
**Location**: `multi_modal_rag/database/db_manager.py`
**Default Path**: `data/collections.db`

## Entity Relationship Diagram

```
┌─────────────────────────┐
│     collections         │
│─────────────────────────│
│ id (PK)                 │
│ content_type            │
│ title                   │
│ source                  │
│ url                     │
│ collection_date         │
│ metadata                │
│ status                  │
│ indexed                 │
└───────────┬─────────────┘
            │
            │ 1:1 (content_type dependent)
            │
     ┌──────┴──────┬──────────────┬──────────────┐
     │             │              │              │
     ▼             ▼              ▼              ▼
┌─────────┐  ┌──────────┐  ┌───────────┐  ┌──────────────────┐
│ papers  │  │  videos  │  │ podcasts  │  │ collection_stats │
│─────────│  │──────────│  │───────────│  │──────────────────│
│ id (PK) │  │ id (PK)  │  │ id (PK)   │  │ id (PK)          │
│ coll_id │  │ coll_id  │  │ coll_id   │  │ content_type     │
│ (FK)    │  │ (FK)     │  │ (FK)      │  │ query            │
│ ...     │  │ ...      │  │ ...       │  │ results_count    │
└─────────┘  └──────────┘  └───────────┘  │ collection_date  │
                                           │ source_api       │
                                           └──────────────────┘
```

## Tables

### 1. collections (Main Table)

The primary table that stores all collected research content regardless of type.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique identifier for each collection item |
| `content_type` | TEXT | NOT NULL | Type of content: 'paper', 'video', or 'podcast' |
| `title` | TEXT | NOT NULL | Title of the research content |
| `source` | TEXT | - | Source platform (e.g., 'arxiv', 'youtube', 'podcast_rss') |
| `url` | TEXT | - | Original URL of the content |
| `collection_date` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | When the item was collected |
| `metadata` | TEXT | - | JSON-encoded additional metadata |
| `status` | TEXT | DEFAULT 'collected' | Processing status |
| `indexed` | BOOLEAN | DEFAULT 0 | Whether item is indexed in OpenSearch (0=false, 1=true) |

**Indexes**:
- Primary key on `id`
- Implicit index on `content_type` (for filtering)
- Implicit index on `collection_date` (for ordering)

### 2. papers

Stores paper-specific data with a foreign key reference to `collections`.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique identifier |
| `collection_id` | INTEGER | FOREIGN KEY → collections(id) | Reference to parent collection |
| `arxiv_id` | TEXT | - | ArXiv identifier (if from ArXiv) |
| `pmc_id` | TEXT | - | PubMed Central identifier (if from PMC) |
| `abstract` | TEXT | - | Paper abstract text |
| `authors` | TEXT | - | JSON array of author names |
| `published_date` | TEXT | - | Publication date |
| `categories` | TEXT | - | JSON array of research categories/tags |
| `pdf_path` | TEXT | - | Local filesystem path to downloaded PDF |

**Relationships**:
- `collection_id` FOREIGN KEY references `collections(id)`

### 3. videos

Stores YouTube video-specific data.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique identifier |
| `collection_id` | INTEGER | FOREIGN KEY → collections(id) | Reference to parent collection |
| `video_id` | TEXT | - | YouTube video ID |
| `channel` | TEXT | - | YouTube channel name |
| `duration` | INTEGER | - | Video duration in seconds |
| `views` | INTEGER | - | View count |
| `thumbnail_url` | TEXT | - | URL to video thumbnail |
| `transcript_available` | BOOLEAN | DEFAULT 0 | Whether transcript was successfully retrieved |

**Relationships**:
- `collection_id` FOREIGN KEY references `collections(id)`

### 4. podcasts

Stores podcast episode-specific data.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique identifier |
| `collection_id` | INTEGER | FOREIGN KEY → collections(id) | Reference to parent collection |
| `episode_id` | TEXT | - | Unique episode identifier |
| `podcast_name` | TEXT | - | Name of the podcast show |
| `audio_url` | TEXT | - | Direct URL to audio file |
| `duration` | INTEGER | - | Episode duration in seconds |

**Relationships**:
- `collection_id` FOREIGN KEY references `collections(id)`

### 5. collection_stats

Tracks statistics about collection operations for analytics.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique identifier |
| `content_type` | TEXT | - | Type of content collected |
| `query` | TEXT | - | Search query used |
| `results_count` | INTEGER | - | Number of results returned |
| `collection_date` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | When the collection occurred |
| `source_api` | TEXT | - | Which API was used (e.g., 'arxiv', 'youtube_api') |

**Note**: This table is independent and does not reference `collections`.

## Data Types and Storage

### JSON Fields

Several fields store JSON-encoded data for flexibility:

- `collections.metadata`: Arbitrary metadata dictionary
- `papers.authors`: Array of author names, e.g., `["John Doe", "Jane Smith"]`
- `papers.categories`: Array of category tags, e.g., `["cs.AI", "cs.LG"]`

When retrieved via the database manager, these JSON fields are automatically parsed back into Python dictionaries/lists.

### Boolean Fields

SQLite doesn't have a native BOOLEAN type. Boolean fields use INTEGER:
- `0` = False
- `1` = True

Fields using this convention:
- `collections.indexed`
- `videos.transcript_available`

### Timestamps

Timestamp fields use SQLite's `CURRENT_TIMESTAMP` which stores in format: `YYYY-MM-DD HH:MM:SS`

## Constraints and Relationships

### Foreign Keys

Foreign keys maintain referential integrity between tables:

1. `papers.collection_id` → `collections.id`
2. `videos.collection_id` → `collections.id`
3. `podcasts.collection_id` → `collections.id`

**Cascade Behavior**: SQLite foreign keys are enforced if `PRAGMA foreign_keys = ON`. By default, no CASCADE DELETE is configured, so collections should be deleted manually after removing type-specific records.

## Example Queries

### Get All Papers with Full Details

```sql
SELECT
    c.*,
    p.arxiv_id,
    p.abstract,
    p.authors,
    p.published_date,
    p.pdf_path
FROM collections c
INNER JOIN papers p ON c.id = p.collection_id
WHERE c.content_type = 'paper'
ORDER BY c.collection_date DESC;
```

### Count Collections by Type

```sql
SELECT
    content_type,
    COUNT(*) as count
FROM collections
GROUP BY content_type;
```

### Find Unindexed Items

```sql
SELECT
    id,
    content_type,
    title,
    collection_date
FROM collections
WHERE indexed = 0
ORDER BY collection_date ASC;
```

### Get Videos with Transcripts

```sql
SELECT
    c.title,
    c.url,
    v.video_id,
    v.channel,
    v.duration
FROM collections c
INNER JOIN videos v ON c.id = v.collection_id
WHERE v.transcript_available = 1;
```

### Recent Collections (Last 7 Days)

```sql
SELECT *
FROM collections
WHERE collection_date >= datetime('now', '-7 days')
ORDER BY collection_date DESC;
```

### Search by Title or Source

```sql
SELECT *
FROM collections
WHERE title LIKE '%machine learning%'
   OR source LIKE '%arxiv%'
ORDER BY collection_date DESC
LIMIT 50;
```

### Collection Statistics by API

```sql
SELECT
    content_type,
    source_api,
    SUM(results_count) as total_results,
    COUNT(*) as query_count
FROM collection_stats
GROUP BY content_type, source_api
ORDER BY total_results DESC;
```

### Papers with Authors and Categories

```sql
SELECT
    c.title,
    p.authors,
    p.categories,
    p.published_date,
    p.arxiv_id
FROM collections c
INNER JOIN papers p ON c.id = p.collection_id
WHERE c.content_type = 'paper'
  AND p.authors LIKE '%LeCun%';
```

## Indexes

### Implicit Indexes

SQLite automatically creates indexes for:
- All PRIMARY KEY columns
- All UNIQUE columns

### Recommended Additional Indexes

For better query performance, consider adding:

```sql
-- Index for content type filtering
CREATE INDEX idx_content_type ON collections(content_type);

-- Index for indexed status
CREATE INDEX idx_indexed ON collections(indexed);

-- Index for collection date sorting
CREATE INDEX idx_collection_date ON collections(collection_date DESC);

-- Index for paper ArXiv IDs
CREATE INDEX idx_arxiv_id ON papers(arxiv_id);

-- Index for video IDs
CREATE INDEX idx_video_id ON videos(video_id);

-- Composite index for type-specific lookups
CREATE INDEX idx_type_indexed ON collections(content_type, indexed);
```

## Database Initialization

The database schema is automatically created when `CollectionDatabaseManager` is instantiated:

```python
from multi_modal_rag.database import CollectionDatabaseManager

# Automatically creates database and all tables if they don't exist
db_manager = CollectionDatabaseManager(db_path="data/collections.db")
```

## Migration Considerations

The current schema does NOT include migration management. If schema changes are needed:

1. Backup the existing database: `cp data/collections.db data/collections.db.backup`
2. Update schema in `db_manager.py`
3. Manually migrate data using SQL commands or Python scripts
4. Consider adding a migration framework like Alembic for production use

## Performance Notes

- **Pagination**: Use LIMIT and OFFSET for large result sets
- **JSON Parsing**: JSON fields are parsed in Python, not at the database level
- **Full-Text Search**: For advanced search, consider SQLite FTS5 extension
- **Concurrent Access**: SQLite supports concurrent reads but serializes writes
- **Database Size**: Monitor `data/collections.db` size; SQLite handles databases up to terabytes but performance degrades with very large datasets

## Backup and Maintenance

### Backup

```bash
# Simple file copy (stop application first)
cp data/collections.db data/collections.db.backup

# SQLite backup command (online backup)
sqlite3 data/collections.db ".backup data/collections.db.backup"
```

### Vacuum (Optimize)

```sql
-- Reclaim unused space and optimize
VACUUM;
```

### Integrity Check

```sql
-- Check database integrity
PRAGMA integrity_check;
```
