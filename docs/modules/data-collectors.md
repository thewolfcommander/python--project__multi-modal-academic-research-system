# Data Collectors Module

## Overview

The Data Collectors module provides a unified interface for collecting academic content from multiple free sources. It includes three main collectors for papers, videos, and podcasts, each implementing rate limiting and error handling to ensure respectful API usage.

## Module Architecture

```
multi_modal_rag/data_collectors/
├── paper_collector.py      # ArXiv, PubMed Central, Semantic Scholar
├── youtube_collector.py    # YouTube educational content
└── podcast_collector.py    # RSS podcast feeds
```

---

## AcademicPaperCollector

**File**: `multi_modal_rag/data_collectors/paper_collector.py`

### Class Overview

Collects free academic papers from multiple sources including ArXiv, PubMed Central, and Semantic Scholar.

### Initialization

```python
from multi_modal_rag.data_collectors import AcademicPaperCollector

collector = AcademicPaperCollector(save_dir="data/papers")
```

**Parameters**:
- `save_dir` (str, optional): Directory to save downloaded PDFs. Default: `"data/papers"`

### Methods

#### `collect_arxiv_papers(query: str, max_results: int = 100) -> List[Dict]`

Collects papers from ArXiv, a free preprint repository.

**Parameters**:
- `query` (str): Search query (e.g., "machine learning", "quantum computing")
- `max_results` (int, optional): Maximum number of papers to collect. Default: 100

**Returns**: List of dictionaries with paper metadata:

```python
{
    'title': str,              # Paper title
    'abstract': str,           # Paper abstract
    'authors': List[str],      # List of author names
    'pdf_url': str,           # Direct PDF URL
    'arxiv_id': str,          # ArXiv identifier
    'published': str,         # ISO format publication date
    'categories': List[str],  # ArXiv categories
    'local_path': str         # Path to downloaded PDF
}
```

**Example**:

```python
collector = AcademicPaperCollector()
papers = collector.collect_arxiv_papers("deep learning", max_results=50)

for paper in papers:
    print(f"Title: {paper['title']}")
    print(f"Authors: {', '.join(paper['authors'])}")
    print(f"PDF saved to: {paper['local_path']}")
```

**Rate Limiting**: Includes 1-second delay between downloads to respect ArXiv API guidelines.

---

#### `collect_pubmed_central(query: str, max_results: int = 50) -> List[Dict]`

Collects from PubMed Central Open Access Subset (biomedical papers).

**Parameters**:
- `query` (str): Search query
- `max_results` (int, optional): Maximum results. Default: 50

**Returns**: List of dictionaries:

```python
{
    'pmc_id': str,           # PubMed Central ID
    'source': str,           # Always 'pubmed_central'
    'pdf_url': str           # PDF download URL
}
```

**Example**:

```python
papers = collector.collect_pubmed_central("COVID-19 treatment", max_results=30)
```

**Rate Limiting**: 0.5-second delay between requests.

**Note**: This method only returns metadata and PDF URLs. Papers must be downloaded separately.

---

#### `collect_semantic_scholar(query: str, max_results: int = 50) -> List[Dict]`

Collects from Semantic Scholar's free API, filtering for open-access PDFs.

**Parameters**:
- `query` (str): Search query
- `max_results` (int, optional): Maximum results. Default: 50

**Returns**: List of dictionaries:

```python
{
    'title': str,
    'abstract': str,
    'authors': List[Dict],  # Author objects with name, authorId
    'year': int,
    'pdf_url': str,        # Open access PDF URL
    'source': str          # Always 'semantic_scholar'
}
```

**Example**:

```python
papers = collector.collect_semantic_scholar("transformer models", max_results=25)

# Filter for recent papers
recent_papers = [p for p in papers if p.get('year', 0) >= 2023]
```

---

## YouTubeLectureCollector

**File**: `multi_modal_rag/data_collectors/youtube_collector.py`

### Class Overview

Collects educational YouTube videos with transcripts using `yt-dlp` and `youtube-transcript-api`.

### Initialization

```python
from multi_modal_rag.data_collectors import YouTubeLectureCollector

collector = YouTubeLectureCollector(save_dir="data/videos")
```

**Parameters**:
- `save_dir` (str, optional): Directory for video metadata. Default: `"data/videos"`

**Dependencies**: Requires `yt-dlp` to be installed:
```bash
pip install yt-dlp
```

### Methods

#### `get_educational_channels() -> List[str]`

Returns a curated list of educational YouTube channels.

**Returns**: List of channel URLs:

```python
[
    "https://www.youtube.com/@mitocw",         # MIT OpenCourseWare
    "https://www.youtube.com/@stanford",       # Stanford
    "https://www.youtube.com/@GoogleDeepMind", # DeepMind
    "https://www.youtube.com/@OpenAI",         # OpenAI
    "https://www.youtube.com/@khanacademy",    # Khan Academy
    "https://www.youtube.com/@3blue1brown",    # 3Blue1Brown
    "https://www.youtube.com/@TwoMinutePapers", # Two Minute Papers
    "https://www.youtube.com/@YannicKilcher",  # Yannic Kilcher
    "https://www.youtube.com/@CSdojo",         # CS Dojo
]
```

---

#### `collect_video_metadata(video_url: str) -> Dict`

Collects complete metadata and transcript for a single YouTube video.

**Parameters**:
- `video_url` (str): Full YouTube video URL

**Returns**: Dictionary with video data:

```python
{
    'video_id': str,          # YouTube video ID
    'title': str,             # Video title
    'description': str,       # Video description
    'author': str,            # Channel name/uploader
    'length': int,            # Duration in seconds
    'views': int,             # View count
    'url': str,               # Original URL
    'transcript': str,        # Full transcript text
    'thumbnail_url': str,     # Thumbnail image URL
    'publish_date': str       # Upload date (YYYYMMDD format)
}
```

**Example**:

```python
collector = YouTubeLectureCollector()
video_url = "https://www.youtube.com/watch?v=aircAruvnKk"
metadata = collector.collect_video_metadata(video_url)

print(f"Title: {metadata['title']}")
print(f"Channel: {metadata['author']}")
print(f"Duration: {metadata['length']} seconds")
print(f"Transcript length: {len(metadata['transcript'])} characters")
```

**Error Handling**:
- Returns `None` if `yt-dlp` is not installed
- Returns metadata with `"Transcript not available"` if transcript extraction fails
- Logs warnings for missing transcripts

---

#### `extract_video_id(url: str) -> str`

Extracts video ID from various YouTube URL formats.

**Parameters**:
- `url` (str): YouTube URL in any format

**Returns**: Video ID string or `None` if not found

**Supported Formats**:
```python
# Standard watch URL
"https://www.youtube.com/watch?v=VIDEO_ID"

# Shortened URL
"https://youtu.be/VIDEO_ID"

# Embed URL
"https://www.youtube.com/embed/VIDEO_ID"
```

---

#### `search_youtube_lectures(query: str, max_results: int = 50) -> List[Dict]`

Searches YouTube for educational videos and collects their metadata.

**Parameters**:
- `query` (str): Search query (automatically appended with "lecture tutorial course")
- `max_results` (int, optional): Maximum videos to collect. Default: 50

**Returns**: List of video metadata dictionaries (same structure as `collect_video_metadata`)

**Example**:

```python
collector = YouTubeLectureCollector()
videos = collector.search_youtube_lectures("quantum computing", max_results=20)

for video in videos:
    if video['transcript'] != "Transcript not available":
        print(f"✓ {video['title']} - Has transcript")
    else:
        print(f"✗ {video['title']} - No transcript")
```

**Search Enhancement**: Query is automatically enhanced with " lecture tutorial course" to focus on educational content.

**Error Handling**:
- Returns empty list if `yt-dlp` not installed
- Logs detailed progress and errors
- Skips videos that fail metadata collection

---

## PodcastCollector

**File**: `multi_modal_rag/data_collectors/podcast_collector.py`

### Class Overview

Collects podcast episodes from RSS feeds with optional audio transcription using Whisper.

### Initialization

```python
from multi_modal_rag.data_collectors import PodcastCollector

collector = PodcastCollector(save_dir="data/podcasts")
```

**Parameters**:
- `save_dir` (str, optional): Directory for audio files and transcripts. Default: `"data/podcasts"`

### Methods

#### `get_educational_podcasts() -> Dict[str, str]`

Returns curated educational podcast RSS feeds.

**Returns**: Dictionary mapping podcast names to RSS URLs:

```python
{
    "Lex Fridman Podcast": "https://lexfridman.com/feed/podcast/",
    "Machine Learning Street Talk": "https://anchor.fm/s/1e4a0eac/podcast/rss",
    "Data Skeptic": "https://dataskeptic.com/feed.rss",
    "The TWIML AI Podcast": "https://twimlai.com/feed/",
    "Learning Machines 101": "http://www.learningmachines101.com/rss",
    "Talking Machines": "http://www.thetalkingmachines.com/rss",
    "AI in Business": "https://feeds.soundcloud.com/.../sounds.rss",
    "Eye on AI": "https://www.eye-on.ai/podcast-rss.xml"
}
```

**Example**:

```python
collector = PodcastCollector()
feeds = collector.get_educational_podcasts()

for name, rss_url in feeds.items():
    print(f"Podcast: {name}")
    print(f"Feed: {rss_url}")
```

---

#### `collect_podcast_episodes(rss_url: str, max_episodes: int = 10) -> List[Dict]`

Collects episodes from a podcast RSS feed.

**Parameters**:
- `rss_url` (str): RSS feed URL
- `max_episodes` (int, optional): Maximum episodes to collect. Default: 10

**Returns**: List of episode dictionaries:

```python
{
    'title': str,          # Episode title
    'description': str,    # Episode description/summary
    'published': str,      # Publication date
    'link': str,          # Episode web page URL
    'audio_url': str,     # Direct audio file URL (MP3/M4A)
    'transcript': None    # Initially None, populated by transcribe_audio()
}
```

**Example**:

```python
collector = PodcastCollector()
rss_url = "https://lexfridman.com/feed/podcast/"
episodes = collector.collect_podcast_episodes(rss_url, max_episodes=5)

for ep in episodes:
    print(f"Title: {ep['title']}")
    print(f"Published: {ep['published']}")
    print(f"Audio URL: {ep['audio_url']}")
```

**Error Handling**:
- Returns empty list if RSS feed fails to parse
- Logs warnings for malformed feeds
- Attempts to find audio URL in multiple RSS locations (links, enclosures)

---

#### `transcribe_audio(audio_url: str, episode_id: str) -> str`

Downloads and transcribes podcast audio using OpenAI's Whisper model.

**Parameters**:
- `audio_url` (str): Direct URL to audio file
- `episode_id` (str): Unique identifier for the episode (used for filename)

**Returns**: Transcript text as a string, or `None` on error

**Example**:

```python
collector = PodcastCollector()

# Collect episodes
episodes = collector.collect_podcast_episodes(
    "https://lexfridman.com/feed/podcast/",
    max_episodes=1
)

# Transcribe first episode
if episodes and episodes[0]['audio_url']:
    transcript = collector.transcribe_audio(
        episodes[0]['audio_url'],
        episode_id="lex_001"
    )
    print(f"Transcript: {transcript[:500]}...")
```

**Whisper Model**:
- Uses `base` model by default (good balance of speed and accuracy)
- Model is loaded once and cached for subsequent transcriptions
- First load may take time to download model weights

**Performance**:
- Downloads audio file to disk before transcription
- Transcription can take several minutes for long episodes
- Logs download progress and transcription status

**Error Handling**:
- Returns `None` if download fails (network error, invalid URL)
- Returns `None` if Whisper transcription fails
- Logs detailed error messages

---

## Integration Example

Here's how to use all collectors together:

```python
from multi_modal_rag.data_collectors import (
    AcademicPaperCollector,
    YouTubeLectureCollector,
    PodcastCollector
)

# Initialize all collectors
paper_collector = AcademicPaperCollector()
video_collector = YouTubeLectureCollector()
podcast_collector = PodcastCollector()

# Collect content on a topic
topic = "neural networks"

# 1. Collect papers
papers = paper_collector.collect_arxiv_papers(topic, max_results=10)
print(f"Collected {len(papers)} papers")

# 2. Collect videos
videos = video_collector.search_youtube_lectures(topic, max_results=5)
print(f"Collected {len(videos)} videos")

# 3. Collect podcasts
podcasts = []
for name, rss_url in podcast_collector.get_educational_podcasts().items():
    episodes = podcast_collector.collect_podcast_episodes(rss_url, max_episodes=2)
    podcasts.extend(episodes)
print(f"Collected {len(podcasts)} podcast episodes")

# All content is now ready for processing and indexing
all_content = {
    'papers': papers,
    'videos': videos,
    'podcasts': podcasts
}
```

---

## Rate Limiting and Best Practices

### ArXiv
- **Rate Limit**: 1 second between requests (implemented)
- **Best Practice**: Use specific queries to reduce result set
- **API Docs**: https://info.arxiv.org/help/api/index.html

### PubMed Central
- **Rate Limit**: 0.5 seconds between requests (implemented)
- **Best Practice**: Include "open access" filter in queries
- **API Docs**: https://www.ncbi.nlm.nih.gov/books/NBK25497/

### Semantic Scholar
- **Rate Limit**: None implemented (API is rate-limited server-side)
- **Best Practice**: Filter for `openAccessPdf` to ensure free content
- **API Docs**: https://api.semanticscholar.org/

### YouTube
- **Dependencies**: Requires `yt-dlp` installation
- **Rate Limit**: None implemented (yt-dlp handles this)
- **Best Practice**: Check for transcript availability before processing

### Podcasts
- **Dependencies**: Requires `whisper` and `pydub` for transcription
- **Rate Limit**: None needed for RSS feeds
- **Best Practice**: Transcribe selectively due to processing time

---

## Error Handling

All collectors implement robust error handling:

1. **Network Errors**: Gracefully handle connection failures
2. **API Errors**: Log and skip problematic items
3. **File Errors**: Create directories if they don't exist
4. **Data Validation**: Handle missing or malformed fields

**Common Error Patterns**:

```python
try:
    papers = collector.collect_arxiv_papers("query", max_results=100)
except Exception as e:
    print(f"Collection failed: {e}")
    papers = []  # Fallback to empty list
```

---

## Logging

All collectors use the centralized logging system:

```python
from multi_modal_rag.logging_config import get_logger

logger = get_logger(__name__)
```

**Log Levels**:
- `INFO`: Collection start/end, counts, success messages
- `DEBUG`: Detailed processing steps, API calls
- `WARNING`: Missing data, failed transcripts, malformed content
- `ERROR`: Critical failures, exceptions

**Example Log Output**:

```
INFO - YouTubeLectureCollector initialized with save_dir: data/videos
INFO - Starting YouTube search for query: 'quantum computing' with max_results: 20
DEBUG - Using yt-dlp search query: 'ytsearch20:quantum computing lecture tutorial course'
INFO - yt-dlp returned 20 results
DEBUG - Processing video 1/20: https://www.youtube.com/watch?v=...
INFO - Successfully collected metadata for: Quantum Computing Introduction by MIT
INFO - Successfully collected 20 videos
```

---

## Troubleshooting

### Issue: yt-dlp not found

**Solution**:
```bash
pip install yt-dlp
```

### Issue: YouTube transcript not available

**Cause**: Video doesn't have captions/subtitles

**Solution**: Collectors handle this gracefully by setting `transcript: "Transcript not available"`

### Issue: Whisper model download fails

**Cause**: Network issues or insufficient disk space

**Solution**:
```python
# Pre-download Whisper model
import whisper
model = whisper.load_model("base")  # Downloads ~140MB
```

### Issue: ArXiv download timeout

**Cause**: Large PDFs or slow network

**Solution**: Increase timeout in arxiv library (modify source or retry)

### Issue: RSS feed parsing fails

**Cause**: Malformed XML or network errors

**Solution**: Collectors log warnings and continue; check RSS feed validity

---

## Module Dependencies

```python
# paper_collector.py
import arxiv
import requests
from scholarly import scholarly

# youtube_collector.py
import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi

# podcast_collector.py
import feedparser
import requests
import whisper
from pydub import AudioSegment
```

Install all dependencies:
```bash
pip install arxiv requests scholarly yt-dlp youtube-transcript-api feedparser openai-whisper pydub
```
