# Type-Specific Tables Reference

## Overview

The Multi-Modal Academic Research System uses type-specific tables to store detailed information that is unique to each content type. Each type-specific table has a foreign key relationship with the main `collections` table.

## Table Relationships

```
collections (parent)
    ├── papers (child)
    ├── videos (child)
    └── podcasts (child)
```

Each collection record (in `collections` table) has exactly **zero or one** corresponding record in one of these type-specific tables, depending on its `content_type` field.

---

## Papers Table

### Overview

Stores detailed metadata for academic papers collected from sources like ArXiv, PubMed Central, and Semantic Scholar.

### Table Definition

```sql
CREATE TABLE IF NOT EXISTS papers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    collection_id INTEGER,
    arxiv_id TEXT,
    pmc_id TEXT,
    abstract TEXT,
    authors TEXT,
    published_date TEXT,
    categories TEXT,
    pdf_path TEXT,
    FOREIGN KEY (collection_id) REFERENCES collections(id)
)
```

### Fields

#### id
- **Type**: `INTEGER`
- **Constraints**: `PRIMARY KEY AUTOINCREMENT`
- **Description**: Unique identifier for the paper record
- **Example**: `1`

#### collection_id
- **Type**: `INTEGER`
- **Constraints**: `FOREIGN KEY → collections(id)`
- **Description**: References the parent collection record
- **Usage**: Join key to get full collection details
- **Example**: `42`

#### arxiv_id
- **Type**: `TEXT`
- **Constraints**: None (nullable)
- **Description**: ArXiv identifier if paper is from ArXiv
- **Format**: Typically `YYMM.NNNNN` or `archive/YYMMNNN`
- **Example**: `'1706.03762'`, `'2103.14030'`

#### pmc_id
- **Type**: `TEXT`
- **Constraints**: None (nullable)
- **Description**: PubMed Central identifier if paper is from PMC
- **Format**: `PMC` followed by numbers
- **Example**: `'PMC1234567'`

#### abstract
- **Type**: `TEXT`
- **Constraints**: None (nullable)
- **Description**: Full text of the paper's abstract
- **Usage**: Searchable, used for initial indexing and display
- **Example**: `'We propose a new architecture for neural machine translation...'`

#### authors
- **Type**: `TEXT` (JSON array)
- **Constraints**: None (nullable)
- **Description**: JSON-encoded array of author names
- **Format**: Stored as JSON string, parsed to list by database manager
- **Example**: `'["Ashish Vaswani", "Noam Shazeer", "Niki Parmar"]'`

#### published_date
- **Type**: `TEXT`
- **Constraints**: None (nullable)
- **Description**: Publication date of the paper
- **Format**: Flexible text format (ISO 8601 recommended: `YYYY-MM-DD`)
- **Examples**: `'2017-06-12'`, `'2021-03-15'`

#### categories
- **Type**: `TEXT` (JSON array)
- **Constraints**: None (nullable)
- **Description**: JSON-encoded array of research categories/tags
- **Format**: Stored as JSON string, parsed to list by database manager
- **Examples**: `'["cs.CL", "cs.AI", "cs.LG"]'`

#### pdf_path
- **Type**: `TEXT`
- **Constraints**: None (nullable)
- **Description**: Local filesystem path to the downloaded PDF file
- **Format**: Absolute or relative path
- **Example**: `'data/papers/1706.03762.pdf'`

### Example Data

```json
{
  "id": 1,
  "collection_id": 42,
  "arxiv_id": "1706.03762",
  "pmc_id": null,
  "abstract": "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks...",
  "authors": "[\"Ashish Vaswani\", \"Noam Shazeer\", \"Niki Parmar\", \"Jakob Uszkoreit\", \"Llion Jones\", \"Aidan N. Gomez\", \"Lukasz Kaiser\", \"Illia Polosukhin\"]",
  "published_date": "2017-06-12",
  "categories": "[\"cs.CL\", \"cs.AI\", \"cs.LG\"]",
  "pdf_path": "data/papers/arxiv_1706.03762.pdf"
}
```

### Common Queries

```sql
-- Get all papers with collection details
SELECT c.*, p.*
FROM collections c
JOIN papers p ON c.id = p.collection_id
ORDER BY p.published_date DESC;

-- Find papers by author
SELECT c.title, p.authors, p.published_date
FROM collections c
JOIN papers p ON c.id = p.collection_id
WHERE p.authors LIKE '%Vaswani%';

-- Get papers from ArXiv only
SELECT c.title, p.arxiv_id, p.pdf_path
FROM collections c
JOIN papers p ON c.id = p.collection_id
WHERE p.arxiv_id IS NOT NULL;

-- Papers by category
SELECT c.title, p.categories
FROM collections c
JOIN papers p ON c.id = p.collection_id
WHERE p.categories LIKE '%cs.AI%';
```

---

## Videos Table

### Overview

Stores metadata for educational videos collected from YouTube.

### Table Definition

```sql
CREATE TABLE IF NOT EXISTS videos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    collection_id INTEGER,
    video_id TEXT,
    channel TEXT,
    duration INTEGER,
    views INTEGER,
    thumbnail_url TEXT,
    transcript_available BOOLEAN DEFAULT 0,
    FOREIGN KEY (collection_id) REFERENCES collections(id)
)
```

### Fields

#### id
- **Type**: `INTEGER`
- **Constraints**: `PRIMARY KEY AUTOINCREMENT`
- **Description**: Unique identifier for the video record
- **Example**: `1`

#### collection_id
- **Type**: `INTEGER`
- **Constraints**: `FOREIGN KEY → collections(id)`
- **Description**: References the parent collection record
- **Example**: `43`

#### video_id
- **Type**: `TEXT`
- **Constraints**: None (nullable)
- **Description**: YouTube video ID
- **Format**: 11-character alphanumeric string
- **Example**: `'dQw4w9WgXcQ'`
- **Usage**: Construct YouTube URL: `https://www.youtube.com/watch?v={video_id}`

#### channel
- **Type**: `TEXT`
- **Constraints**: None (nullable)
- **Description**: YouTube channel name
- **Example**: `'3Blue1Brown'`, `'Two Minute Papers'`

#### duration
- **Type**: `INTEGER`
- **Constraints**: None (nullable)
- **Description**: Video duration in seconds
- **Example**: `1800` (30 minutes), `600` (10 minutes)
- **Display**: Convert to `HH:MM:SS` format in UI

#### views
- **Type**: `INTEGER`
- **Constraints**: None (nullable)
- **Description**: Video view count at time of collection
- **Example**: `1000000`
- **Note**: This is a snapshot; actual views may have changed

#### thumbnail_url
- **Type**: `TEXT`
- **Constraints**: None (nullable)
- **Description**: URL to video thumbnail image
- **Example**: `'https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg'`
- **Common Formats**:
  - `default.jpg` - 120x90
  - `mqdefault.jpg` - 320x180
  - `hqdefault.jpg` - 480x360
  - `maxresdefault.jpg` - 1280x720

#### transcript_available
- **Type**: `BOOLEAN` (stored as INTEGER)
- **Constraints**: `DEFAULT 0`
- **Description**: Whether a transcript was successfully retrieved
- **Values**:
  - `0` - No transcript available
  - `1` - Transcript successfully retrieved
- **Example**: `1`

### Example Data

```json
{
  "id": 1,
  "collection_id": 43,
  "video_id": "aircAruvnKk",
  "channel": "3Blue1Brown",
  "duration": 1194,
  "views": 5234891,
  "thumbnail_url": "https://i.ytimg.com/vi/aircAruvnKk/maxresdefault.jpg",
  "transcript_available": 1
}
```

### Common Queries

```sql
-- Get all videos with transcripts
SELECT c.title, v.channel, v.duration, v.video_id
FROM collections c
JOIN videos v ON c.id = v.collection_id
WHERE v.transcript_available = 1;

-- Videos by channel
SELECT c.title, v.video_id, v.views
FROM collections c
JOIN videos v ON c.id = v.collection_id
WHERE v.channel = '3Blue1Brown'
ORDER BY v.views DESC;

-- Long videos (>30 minutes)
SELECT c.title, v.duration/60 as duration_minutes
FROM collections c
JOIN videos v ON c.id = v.collection_id
WHERE v.duration > 1800
ORDER BY v.duration DESC;

-- Most viewed videos
SELECT c.title, v.channel, v.views
FROM collections c
JOIN videos v ON c.id = v.collection_id
ORDER BY v.views DESC
LIMIT 10;
```

---

## Podcasts Table

### Overview

Stores metadata for podcast episodes collected from RSS feeds.

### Table Definition

```sql
CREATE TABLE IF NOT EXISTS podcasts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    collection_id INTEGER,
    episode_id TEXT,
    podcast_name TEXT,
    audio_url TEXT,
    duration INTEGER,
    FOREIGN KEY (collection_id) REFERENCES collections(id)
)
```

### Fields

#### id
- **Type**: `INTEGER`
- **Constraints**: `PRIMARY KEY AUTOINCREMENT`
- **Description**: Unique identifier for the podcast record
- **Example**: `1`

#### collection_id
- **Type**: `INTEGER`
- **Constraints**: `FOREIGN KEY → collections(id)`
- **Description**: References the parent collection record
- **Example**: `44`

#### episode_id
- **Type**: `TEXT`
- **Constraints**: None (nullable)
- **Description**: Unique identifier for the podcast episode
- **Format**: Varies by podcast platform (GUID from RSS feed)
- **Example**: `'ep-123-ai-safety'`, `'https://podcast.example.com/episode/456'`

#### podcast_name
- **Type**: `TEXT`
- **Constraints**: None (nullable)
- **Description**: Name of the podcast show
- **Example**: `'The AI Podcast'`, `'Lex Fridman Podcast'`

#### audio_url
- **Type**: `TEXT`
- **Constraints**: None (nullable)
- **Description**: Direct URL to the audio file (MP3, M4A, etc.)
- **Example**: `'https://podcast.example.com/audio/episode-123.mp3'`
- **Usage**: For downloading or streaming the episode

#### duration
- **Type**: `INTEGER`
- **Constraints**: None (nullable)
- **Description**: Episode duration in seconds
- **Example**: `3600` (1 hour), `5400` (1.5 hours)
- **Display**: Convert to `HH:MM:SS` format in UI

### Example Data

```json
{
  "id": 1,
  "collection_id": 44,
  "episode_id": "ep-312-yann-lecun",
  "podcast_name": "Lex Fridman Podcast",
  "audio_url": "https://lexfridman.com/audio/312-yann-lecun.mp3",
  "duration": 7200
}
```

### Common Queries

```sql
-- Get all podcasts with collection details
SELECT c.title, p.podcast_name, p.duration, p.audio_url
FROM collections c
JOIN podcasts p ON c.id = p.collection_id
ORDER BY c.collection_date DESC;

-- Episodes by podcast name
SELECT c.title, p.episode_id, p.duration
FROM collections c
JOIN podcasts p ON c.id = p.collection_id
WHERE p.podcast_name = 'Lex Fridman Podcast'
ORDER BY c.collection_date DESC;

-- Long episodes (>2 hours)
SELECT c.title, p.podcast_name, p.duration/3600.0 as duration_hours
FROM collections c
JOIN podcasts p ON c.id = p.collection_id
WHERE p.duration > 7200
ORDER BY p.duration DESC;

-- Total podcast duration by show
SELECT p.podcast_name,
       COUNT(*) as episode_count,
       SUM(p.duration)/3600.0 as total_hours
FROM collections c
JOIN podcasts p ON c.id = p.collection_id
GROUP BY p.podcast_name
ORDER BY total_hours DESC;
```

---

## Python Database Manager Usage

### Adding Type-Specific Records

```python
from multi_modal_rag.database import CollectionDatabaseManager

db = CollectionDatabaseManager()

# 1. Add paper
collection_id = db.add_collection(
    content_type='paper',
    title='Attention Is All You Need',
    source='arxiv',
    url='https://arxiv.org/abs/1706.03762',
    metadata={}
)

db.add_paper(collection_id, {
    'arxiv_id': '1706.03762',
    'abstract': 'The dominant sequence transduction models...',
    'authors': ['Ashish Vaswani', 'Noam Shazeer'],
    'published': '2017-06-12',
    'categories': ['cs.CL', 'cs.AI'],
    'local_path': 'data/papers/1706.03762.pdf'
})

# 2. Add video
collection_id = db.add_collection(
    content_type='video',
    title='Neural Networks Explained',
    source='youtube',
    url='https://youtube.com/watch?v=abc123',
    metadata={}
)

db.add_video(collection_id, {
    'video_id': 'abc123',
    'author': '3Blue1Brown',  # Maps to 'channel' field
    'length': 1194,            # Maps to 'duration' field
    'views': 1000000,
    'thumbnail_url': 'https://i.ytimg.com/vi/abc123/maxresdefault.jpg',
    'transcript': 'Full transcript text...'  # Boolean check for transcript_available
})

# 3. Add podcast
collection_id = db.add_collection(
    content_type='podcast',
    title='AI Safety Episode',
    source='podcast_rss',
    url='https://podcast.ai/ep42',
    metadata={}
)

db.add_podcast(collection_id, {
    'episode_id': 'ep-42',
    'podcast_name': 'AI Alignment Podcast',
    'audio_url': 'https://podcast.ai/audio/ep42.mp3',
    'duration': 3600
})
```

### Retrieving Type-Specific Data

```python
# Get full collection details with type-specific data
details = db.get_collection_with_details(collection_id)

# For a paper, details will include:
# {
#   'id': 42,
#   'content_type': 'paper',
#   'title': '...',
#   'details': {
#     'id': 1,
#     'collection_id': 42,
#     'arxiv_id': '1706.03762',
#     'authors': ['Ashish Vaswani', ...],  # Parsed from JSON
#     'categories': ['cs.CL', ...],         # Parsed from JSON
#     ...
#   }
# }
```

## Indexing Recommendations

```sql
-- Papers
CREATE INDEX idx_papers_collection_id ON papers(collection_id);
CREATE INDEX idx_papers_arxiv_id ON papers(arxiv_id);
CREATE INDEX idx_papers_pmc_id ON papers(pmc_id);
CREATE INDEX idx_papers_published_date ON papers(published_date);

-- Videos
CREATE INDEX idx_videos_collection_id ON videos(collection_id);
CREATE INDEX idx_videos_video_id ON videos(video_id);
CREATE INDEX idx_videos_channel ON videos(channel);
CREATE INDEX idx_videos_transcript_available ON videos(transcript_available);

-- Podcasts
CREATE INDEX idx_podcasts_collection_id ON podcasts(collection_id);
CREATE INDEX idx_podcasts_episode_id ON podcasts(episode_id);
CREATE INDEX idx_podcasts_podcast_name ON podcasts(podcast_name);
```

## Data Validation

### Papers
- At least one of `arxiv_id` or `pmc_id` should be present
- `authors` must be valid JSON array
- `categories` must be valid JSON array
- `published_date` should be in ISO format (YYYY-MM-DD)

### Videos
- `video_id` should be 11 characters
- `duration` and `views` should be non-negative integers
- `thumbnail_url` should be valid URL
- `transcript_available` should be 0 or 1

### Podcasts
- `episode_id` should be unique within a podcast
- `audio_url` should be valid URL
- `duration` should be non-negative integer

## Troubleshooting

### Issue: JSON Parse Errors

**Cause**: Invalid JSON in `authors` or `categories` fields

**Solution**: Always use `json.dumps()` when inserting:
```python
import json
authors_json = json.dumps(['Author 1', 'Author 2'])
```

### Issue: Orphaned Type Records

**Cause**: Deleting from `collections` without deleting from type tables

**Solution**: Delete in correct order:
```python
# First delete type-specific record
cursor.execute("DELETE FROM papers WHERE collection_id = ?", (id,))
# Then delete collection
cursor.execute("DELETE FROM collections WHERE id = ?", (id,))
```

### Issue: Duplicate Video IDs

**Cause**: Same video collected multiple times

**Solution**: Check before inserting:
```sql
SELECT COUNT(*) FROM videos WHERE video_id = ?;
```

Or add UNIQUE constraint:
```sql
CREATE UNIQUE INDEX idx_unique_video_id ON videos(video_id);
```
