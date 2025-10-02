# Collections Table Reference

## Overview

The `collections` table is the core table in the Multi-Modal Academic Research System database. It serves as the central registry for all collected research content, regardless of type (papers, videos, or podcasts).

## Table Definition

```sql
CREATE TABLE IF NOT EXISTS collections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content_type TEXT NOT NULL,
    title TEXT NOT NULL,
    source TEXT,
    url TEXT,
    collection_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT,
    status TEXT DEFAULT 'collected',
    indexed BOOLEAN DEFAULT 0
)
```

## Field Specifications

### id
- **Type**: `INTEGER`
- **Constraints**: `PRIMARY KEY AUTOINCREMENT`
- **Description**: Auto-incrementing unique identifier for each collection item
- **Usage**: Used as foreign key in type-specific tables (papers, videos, podcasts)
- **Example**: `1`, `2`, `3`, ...

### content_type
- **Type**: `TEXT`
- **Constraints**: `NOT NULL`
- **Description**: Identifies the type of content
- **Valid Values**:
  - `'paper'` - Academic papers (ArXiv, PubMed, etc.)
  - `'video'` - YouTube videos
  - `'podcast'` - Podcast episodes
- **Usage**: Determines which type-specific table contains additional data
- **Example**: `'paper'`

### title
- **Type**: `TEXT`
- **Constraints**: `NOT NULL`
- **Description**: The title of the research content
- **Usage**: Primary display name, searchable field
- **Example**: `'Attention Is All You Need'`

### source
- **Type**: `TEXT`
- **Constraints**: None (nullable)
- **Description**: The platform or API from which content was collected
- **Common Values**:
  - `'arxiv'` - ArXiv repository
  - `'pubmed'` - PubMed Central
  - `'semantic_scholar'` - Semantic Scholar API
  - `'youtube'` - YouTube platform
  - `'podcast_rss'` - Podcast RSS feed
- **Example**: `'arxiv'`

### url
- **Type**: `TEXT`
- **Constraints**: None (nullable)
- **Description**: Original URL of the content
- **Usage**: Link back to source, can be used for re-fetching or citation
- **Examples**:
  - `'https://arxiv.org/abs/1706.03762'`
  - `'https://www.youtube.com/watch?v=dQw4w9WgXcQ'`
  - `'https://podcast.example.com/episode/123'`

### collection_date
- **Type**: `TIMESTAMP`
- **Constraints**: `DEFAULT CURRENT_TIMESTAMP`
- **Description**: Timestamp when the item was collected
- **Format**: `YYYY-MM-DD HH:MM:SS`
- **Usage**: Sorting, filtering recent collections, analytics
- **Example**: `'2025-10-02 14:30:45'`

### metadata
- **Type**: `TEXT`
- **Constraints**: None (nullable)
- **Description**: JSON-encoded dictionary containing arbitrary metadata
- **Usage**: Flexible storage for additional information not captured in structured fields
- **Structure**: JSON string, automatically parsed to dict by database manager
- **Example**:
```json
{
  "collector_version": "1.0.0",
  "keywords": ["machine learning", "transformers"],
  "language": "en",
  "download_time_ms": 1234
}
```

### status
- **Type**: `TEXT`
- **Constraints**: `DEFAULT 'collected'`
- **Description**: Processing status of the collection item
- **Common Values**:
  - `'collected'` - Successfully collected, not yet processed
  - `'processing'` - Currently being processed
  - `'processed'` - Processing complete
  - `'failed'` - Processing failed
  - `'indexed'` - Successfully indexed (though `indexed` field is preferred)
- **Usage**: Track processing workflow, identify items needing attention
- **Example**: `'collected'`

### indexed
- **Type**: `BOOLEAN` (stored as INTEGER)
- **Constraints**: `DEFAULT 0`
- **Description**: Whether the item has been indexed in OpenSearch
- **Valid Values**:
  - `0` - Not indexed (False)
  - `1` - Indexed (True)
- **Usage**: Track which items are searchable in the RAG system
- **Example**: `1`

## Relationships

### One-to-One with Type-Specific Tables

Each collection has exactly **zero or one** corresponding entry in a type-specific table:

- If `content_type = 'paper'` → One record in `papers` table
- If `content_type = 'video'` → One record in `videos` table
- If `content_type = 'podcast'` → One record in `podcasts` table

**Foreign Key**: `papers.collection_id`, `videos.collection_id`, `podcasts.collection_id` all reference `collections.id`

### Relationship Diagram

```
collections (1) ←→ (0..1) papers
collections (1) ←→ (0..1) videos
collections (1) ←→ (0..1) podcasts
```

## Common Query Patterns

### Insert New Collection

```sql
INSERT INTO collections (content_type, title, source, url, metadata, indexed)
VALUES ('paper', 'Attention Is All You Need', 'arxiv',
        'https://arxiv.org/abs/1706.03762',
        '{"keywords": ["transformers", "attention"]}',
        0);
```

### Get All Collections

```sql
SELECT * FROM collections
ORDER BY collection_date DESC
LIMIT 100;
```

### Filter by Content Type

```sql
SELECT * FROM collections
WHERE content_type = 'paper'
ORDER BY collection_date DESC;
```

### Get Unindexed Items

```sql
SELECT id, title, content_type
FROM collections
WHERE indexed = 0
ORDER BY collection_date ASC;
```

### Search by Title

```sql
SELECT * FROM collections
WHERE title LIKE '%machine learning%'
ORDER BY collection_date DESC
LIMIT 50;
```

### Count by Type

```sql
SELECT content_type, COUNT(*) as count
FROM collections
GROUP BY content_type;
```

### Recent Collections (Last 7 Days)

```sql
SELECT * FROM collections
WHERE collection_date >= datetime('now', '-7 days')
ORDER BY collection_date DESC;
```

### Update Indexed Status

```sql
UPDATE collections
SET indexed = 1
WHERE id = ?;
```

### Delete Collection

```sql
-- First delete from type-specific table
DELETE FROM papers WHERE collection_id = ?;

-- Then delete from collections
DELETE FROM collections WHERE id = ?;
```

## Example Data

| id | content_type | title | source | url | collection_date | metadata | status | indexed |
|----|--------------|-------|--------|-----|-----------------|----------|--------|---------|
| 1 | paper | Attention Is All You Need | arxiv | https://arxiv.org/abs/1706.03762 | 2025-10-01 10:30:00 | {"keywords": ["transformers"]} | collected | 1 |
| 2 | video | Introduction to Neural Networks | youtube | https://youtube.com/watch?v=abc123 | 2025-10-01 11:00:00 | {"duration": 1800} | collected | 1 |
| 3 | podcast | AI Podcast Episode 42 | podcast_rss | https://podcast.ai/ep42 | 2025-10-02 09:15:00 | {"language": "en"} | collected | 0 |

## Indexing Recommendations

For optimal query performance on the collections table:

```sql
-- Content type filtering (frequently used)
CREATE INDEX idx_content_type ON collections(content_type);

-- Indexed status filtering (find unindexed items)
CREATE INDEX idx_indexed ON collections(indexed);

-- Collection date sorting (most common sort)
CREATE INDEX idx_collection_date ON collections(collection_date DESC);

-- Composite index for type + indexed queries
CREATE INDEX idx_type_indexed ON collections(content_type, indexed);

-- Full-text search on title (optional, requires FTS5)
CREATE VIRTUAL TABLE collections_fts USING fts5(title, content='collections', content_rowid='id');
```

## Data Validation

When inserting data, ensure:

1. **content_type** is one of: `'paper'`, `'video'`, `'podcast'`
2. **title** is not empty
3. **metadata** is valid JSON (if provided)
4. **indexed** is 0 or 1 (not NULL)
5. **url** is a valid URL format (if provided)

## Python Database Manager Usage

The `CollectionDatabaseManager` class provides methods to interact with this table:

```python
from multi_modal_rag.database import CollectionDatabaseManager

db = CollectionDatabaseManager()

# Add a new collection
collection_id = db.add_collection(
    content_type='paper',
    title='Attention Is All You Need',
    source='arxiv',
    url='https://arxiv.org/abs/1706.03762',
    metadata={'keywords': ['transformers', 'attention']},
    indexed=False
)

# Get all collections with pagination
collections = db.get_all_collections(limit=100, offset=0)

# Get collections by type
papers = db.get_collections_by_type('paper', limit=50)

# Mark as indexed
db.mark_as_indexed(collection_id)

# Search collections
results = db.search_collections('transformer', limit=50)

# Get full details (includes type-specific data)
details = db.get_collection_with_details(collection_id)
```

## Storage Considerations

### Size Estimates

Approximate storage per collection record:
- Base record: ~500 bytes
- With small metadata: ~1 KB
- With large metadata (long arrays): up to 10 KB

**Example**: 10,000 collections ≈ 10-100 MB

### Metadata JSON Best Practices

- Keep metadata JSON compact
- Don't store large text blobs (use separate fields or files)
- Use consistent key naming conventions
- Store only non-searchable auxiliary data (searchable data should go in proper fields)

Good metadata examples:
```json
{
  "collector_version": "1.0.0",
  "language": "en",
  "download_timestamp": 1696234567
}
```

Bad metadata examples (too large):
```json
{
  "full_text": "...[thousands of lines]...",
  "raw_html": "...[complete HTML dump]..."
}
```

## Migration Path

If adding new fields to the collections table:

```sql
-- Add new column (SQLite limited ALTER TABLE support)
ALTER TABLE collections ADD COLUMN new_field TEXT DEFAULT NULL;

-- For complex changes, create new table and migrate:
CREATE TABLE collections_new (...);
INSERT INTO collections_new SELECT ..., DEFAULT_VALUE FROM collections;
DROP TABLE collections;
ALTER TABLE collections_new RENAME TO collections;
```

## Troubleshooting

### Issue: Foreign Key Constraint Failed

**Cause**: Trying to delete a collection that has type-specific records

**Solution**: Delete type-specific records first
```sql
DELETE FROM papers WHERE collection_id = 123;
DELETE FROM collections WHERE id = 123;
```

### Issue: Invalid JSON in metadata

**Cause**: Manually inserted invalid JSON string

**Solution**: Validate JSON before insert
```python
import json
metadata_str = json.dumps(metadata_dict)  # Always use json.dumps()
```

### Issue: Duplicate collections

**Cause**: No UNIQUE constraint on url or title

**Solution**: Add application-level deduplication or:
```sql
CREATE UNIQUE INDEX idx_unique_url ON collections(url) WHERE url IS NOT NULL;
```
