# Building Custom Data Collectors

Comprehensive guide to building custom data collectors for the Multi-Modal Academic Research System.

## Table of Contents

- [Overview](#overview)
- [Collector Architecture](#collector-architecture)
- [Building Your First Collector](#building-your-first-collector)
- [Advanced Collector Patterns](#advanced-collector-patterns)
- [Data Source Examples](#data-source-examples)
- [Error Handling](#error-handling)
- [Testing Collectors](#testing-collectors)
- [Best Practices](#best-practices)

---

## Overview

### What is a Data Collector?

A data collector is a module that:
1. Connects to an external data source (API, website, file system)
2. Retrieves content based on search criteria
3. Transforms data into a standard format
4. Returns structured data for indexing

### When to Build a Custom Collector

Build a custom collector when you want to:
- Add a new data source (e.g., Google Scholar, JSTOR)
- Collect specific content types (e.g., datasets, code repositories)
- Integrate proprietary data sources
- Customize existing collectors

---

## Collector Architecture

### Standard Data Format

All collectors should return data in this format:

```python
{
    'id': 'unique_identifier',
    'content_type': 'paper|video|podcast|custom',
    'title': 'Content title',
    'abstract': 'Brief summary or description',
    'content': 'Full text content',
    'authors': ['Author 1', 'Author 2'],
    'publication_date': '2024-01-15',
    'source_url': 'https://source.url',
    'metadata': {
        # Additional source-specific metadata
        'journal': 'Journal name',
        'doi': '10.1234/example',
        'citations': 42
    }
}
```

### Collector Interface

```python
from typing import List, Dict, Optional
from abc import ABC, abstractmethod

class BaseCollector(ABC):
    """Base class for all data collectors."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize collector."""
        self.api_key = api_key

    @abstractmethod
    def collect(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Collect data from source.

        Args:
            query: Search query
            max_results: Maximum number of results to return

        Returns:
            List of documents in standard format
        """
        pass

    @abstractmethod
    def validate_result(self, result: Dict) -> bool:
        """
        Validate that result has required fields.

        Args:
            result: Document to validate

        Returns:
            True if valid, False otherwise
        """
        pass

    def format_date(self, date_string: str) -> str:
        """
        Convert date to standard format (YYYY-MM-DD).

        Args:
            date_string: Date in various formats

        Returns:
            Standardized date string
        """
        from dateutil import parser
        try:
            date_obj = parser.parse(date_string)
            return date_obj.strftime('%Y-%m-%d')
        except:
            return '1970-01-01'  # Default date

    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text.

        Args:
            text: Raw text

        Returns:
            Cleaned text
        """
        import re

        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove special characters
        text = text.strip()

        return text
```

---

## Building Your First Collector

### Example: Google Scholar Collector

```python
from scholarly import scholarly
from typing import List, Dict
import time

class GoogleScholarCollector(BaseCollector):
    """Collector for Google Scholar papers."""

    def __init__(self):
        """Initialize collector."""
        super().__init__()

    def collect(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Collect papers from Google Scholar.

        Args:
            query: Search query
            max_results: Maximum number of results

        Returns:
            List of papers in standard format
        """
        results = []

        try:
            # Search Google Scholar
            search_query = scholarly.search_pubs(query)

            # Collect results
            for i, result in enumerate(search_query):
                if i >= max_results:
                    break

                # Fill in details
                try:
                    paper = scholarly.fill(result)
                    formatted = self._format_paper(paper)

                    if self.validate_result(formatted):
                        results.append(formatted)

                except Exception as e:
                    print(f"Error processing paper: {e}")
                    continue

                # Rate limiting
                time.sleep(1)

        except Exception as e:
            print(f"Error searching Google Scholar: {e}")

        return results

    def _format_paper(self, paper: Dict) -> Dict:
        """
        Convert Scholar paper to standard format.

        Args:
            paper: Paper from scholarly

        Returns:
            Formatted paper
        """
        # Extract data
        title = paper.get('bib', {}).get('title', '')
        abstract = paper.get('bib', {}).get('abstract', '')
        authors = paper.get('bib', {}).get('author', [])
        year = paper.get('bib', {}).get('pub_year', '1970')
        url = paper.get('pub_url', '')
        citations = paper.get('num_citations', 0)

        # Generate ID
        paper_id = f"scholar_{hash(title)}"

        # Format date
        date = self.format_date(f"{year}-01-01")

        return {
            'id': paper_id,
            'content_type': 'paper',
            'title': self.clean_text(title),
            'abstract': self.clean_text(abstract),
            'content': abstract,  # Scholar doesn't provide full text
            'authors': authors if isinstance(authors, list) else [authors],
            'publication_date': date,
            'source_url': url,
            'metadata': {
                'source': 'Google Scholar',
                'citations': citations,
                'year': year
            }
        }

    def validate_result(self, result: Dict) -> bool:
        """Validate result has required fields."""
        required = ['id', 'title', 'content_type']

        for field in required:
            if field not in result or not result[field]:
                return False

        return True

# Usage
collector = GoogleScholarCollector()
papers = collector.collect("deep learning", max_results=5)

for paper in papers:
    print(f"Title: {paper['title']}")
    print(f"Authors: {', '.join(paper['authors'])}")
    print(f"Date: {paper['publication_date']}")
    print(f"Citations: {paper['metadata']['citations']}")
    print("-" * 60)
```

---

## Advanced Collector Patterns

### 1. Authenticated Collector

For APIs requiring authentication:

```python
import requests
from typing import Optional

class AuthenticatedCollector(BaseCollector):
    """Collector for authenticated API."""

    def __init__(self, api_key: str, base_url: str):
        """
        Initialize collector.

        Args:
            api_key: API key for authentication
            base_url: Base API URL
        """
        super().__init__(api_key)
        self.base_url = base_url
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """Create authenticated session."""
        session = requests.Session()
        session.headers.update({
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'ResearchAssistant/1.0'
        })
        return session

    def collect(self, query: str, max_results: int = 10) -> List[Dict]:
        """Collect data from authenticated API."""
        try:
            response = self.session.get(
                f"{self.base_url}/search",
                params={
                    'query': query,
                    'limit': max_results
                },
                timeout=30
            )

            response.raise_for_status()
            data = response.json()

            return [self._format_result(item) for item in data['results']]

        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            return []

    def _format_result(self, item: Dict) -> Dict:
        """Format API result to standard format."""
        # Implementation specific to API
        pass

    def validate_result(self, result: Dict) -> bool:
        """Validate result."""
        return all(k in result for k in ['id', 'title', 'content_type'])
```

### 2. Paginated Collector

For APIs with pagination:

```python
class PaginatedCollector(BaseCollector):
    """Collector that handles pagination."""

    def collect(self, query: str, max_results: int = 100) -> List[Dict]:
        """Collect with pagination."""
        all_results = []
        page = 1
        per_page = 20

        while len(all_results) < max_results:
            try:
                page_results = self._fetch_page(query, page, per_page)

                if not page_results:
                    break

                all_results.extend(page_results)
                page += 1

                # Rate limiting
                time.sleep(1)

            except Exception as e:
                print(f"Error fetching page {page}: {e}")
                break

        return all_results[:max_results]

    def _fetch_page(
        self,
        query: str,
        page: int,
        per_page: int
    ) -> List[Dict]:
        """Fetch single page of results."""
        response = requests.get(
            f"{self.api_url}/search",
            params={
                'q': query,
                'page': page,
                'per_page': per_page
            }
        )

        response.raise_for_status()
        data = response.json()

        return [self._format_result(item) for item in data['items']]

    def _format_result(self, item: Dict) -> Dict:
        """Format result."""
        pass

    def validate_result(self, result: Dict) -> bool:
        """Validate result."""
        return True
```

### 3. Async Collector

For concurrent collection:

```python
import asyncio
import aiohttp
from typing import List, Dict

class AsyncCollector(BaseCollector):
    """Async collector for concurrent requests."""

    async def collect_async(
        self,
        queries: List[str],
        max_results_per_query: int = 10
    ) -> List[Dict]:
        """
        Collect from multiple queries concurrently.

        Args:
            queries: List of search queries
            max_results_per_query: Max results per query

        Returns:
            Combined results from all queries
        """
        async with aiohttp.ClientSession() as session:
            tasks = [
                self._fetch_query(session, query, max_results_per_query)
                for query in queries
            ]

            results = await asyncio.gather(*tasks)

        # Flatten results
        all_results = []
        for query_results in results:
            all_results.extend(query_results)

        return all_results

    async def _fetch_query(
        self,
        session: aiohttp.ClientSession,
        query: str,
        max_results: int
    ) -> List[Dict]:
        """Fetch results for single query."""
        try:
            async with session.get(
                f"{self.api_url}/search",
                params={'q': query, 'limit': max_results}
            ) as response:
                data = await response.json()

                return [
                    self._format_result(item)
                    for item in data['results']
                ]

        except Exception as e:
            print(f"Error fetching query '{query}': {e}")
            return []

    def collect(self, query: str, max_results: int = 10) -> List[Dict]:
        """Sync interface for async collection."""
        return asyncio.run(
            self.collect_async([query], max_results)
        )

    def _format_result(self, item: Dict) -> Dict:
        """Format result."""
        pass

    def validate_result(self, result: Dict) -> bool:
        """Validate result."""
        return True

# Usage
collector = AsyncCollector(api_key="...")
results = asyncio.run(
    collector.collect_async(
        ["machine learning", "deep learning", "neural networks"],
        max_results_per_query=20
    )
)
```

### 4. Cached Collector

With built-in caching:

```python
import pickle
import os
from datetime import datetime, timedelta

class CachedCollector(BaseCollector):
    """Collector with result caching."""

    def __init__(self, cache_dir: str = 'cache', cache_ttl: int = 86400):
        """
        Initialize collector.

        Args:
            cache_dir: Directory for cache files
            cache_ttl: Cache time-to-live in seconds
        """
        super().__init__()
        self.cache_dir = cache_dir
        self.cache_ttl = cache_ttl
        os.makedirs(cache_dir, exist_ok=True)

    def collect(self, query: str, max_results: int = 10) -> List[Dict]:
        """Collect with caching."""
        # Check cache
        cached = self._get_cached(query, max_results)
        if cached is not None:
            print(f"Using cached results for: {query}")
            return cached

        # Fetch fresh data
        results = self._collect_fresh(query, max_results)

        # Cache results
        self._cache_results(query, max_results, results)

        return results

    def _get_cache_path(self, query: str, max_results: int) -> str:
        """Get cache file path."""
        import hashlib
        key = f"{query}_{max_results}"
        hash_key = hashlib.md5(key.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{hash_key}.pkl")

    def _get_cached(self, query: str, max_results: int) -> Optional[List[Dict]]:
        """Get cached results if available and not expired."""
        cache_path = self._get_cache_path(query, max_results)

        if not os.path.exists(cache_path):
            return None

        # Check if expired
        file_time = datetime.fromtimestamp(os.path.getmtime(cache_path))
        if datetime.now() - file_time > timedelta(seconds=self.cache_ttl):
            os.remove(cache_path)
            return None

        # Load cache
        try:
            with open(cache_path, 'rb') as f:
                return pickle.load(f)
        except:
            return None

    def _cache_results(
        self,
        query: str,
        max_results: int,
        results: List[Dict]
    ):
        """Cache results."""
        cache_path = self._get_cache_path(query, max_results)

        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(results, f)
        except Exception as e:
            print(f"Error caching results: {e}")

    def _collect_fresh(self, query: str, max_results: int) -> List[Dict]:
        """Collect fresh data (implement in subclass)."""
        raise NotImplementedError

    def validate_result(self, result: Dict) -> bool:
        """Validate result."""
        return True
```

---

## Data Source Examples

### 1. GitHub Repository Collector

```python
import requests

class GitHubCollector(BaseCollector):
    """Collect code repositories from GitHub."""

    def __init__(self, api_token: str):
        """Initialize with GitHub API token."""
        super().__init__(api_token)
        self.api_url = "https://api.github.com"
        self.headers = {
            'Authorization': f'token {api_token}',
            'Accept': 'application/vnd.github.v3+json'
        }

    def collect(self, query: str, max_results: int = 10) -> List[Dict]:
        """Search GitHub repositories."""
        try:
            response = requests.get(
                f"{self.api_url}/search/repositories",
                headers=self.headers,
                params={
                    'q': query,
                    'sort': 'stars',
                    'order': 'desc',
                    'per_page': max_results
                }
            )

            response.raise_for_status()
            data = response.json()

            return [
                self._format_repository(repo)
                for repo in data['items']
            ]

        except Exception as e:
            print(f"GitHub API error: {e}")
            return []

    def _format_repository(self, repo: Dict) -> Dict:
        """Format repository to standard format."""
        return {
            'id': f"github_{repo['id']}",
            'content_type': 'code',
            'title': repo['full_name'],
            'abstract': repo.get('description', ''),
            'content': self._get_readme(repo),
            'authors': [repo['owner']['login']],
            'publication_date': self.format_date(repo['created_at']),
            'source_url': repo['html_url'],
            'metadata': {
                'source': 'GitHub',
                'stars': repo['stargazers_count'],
                'forks': repo['forks_count'],
                'language': repo['language'],
                'topics': repo.get('topics', [])
            }
        }

    def _get_readme(self, repo: Dict) -> str:
        """Fetch repository README."""
        try:
            response = requests.get(
                f"{self.api_url}/repos/{repo['full_name']}/readme",
                headers=self.headers
            )

            if response.status_code == 200:
                import base64
                content = base64.b64decode(
                    response.json()['content']
                ).decode('utf-8')
                return content
            else:
                return repo.get('description', '')

        except:
            return repo.get('description', '')

    def validate_result(self, result: Dict) -> bool:
        """Validate result."""
        return result.get('title') and result.get('content_type') == 'code'
```

### 2. RSS Feed Collector

```python
import feedparser

class RSSCollector(BaseCollector):
    """Collect articles from RSS feeds."""

    def __init__(self, feed_urls: List[str]):
        """
        Initialize with RSS feed URLs.

        Args:
            feed_urls: List of RSS feed URLs
        """
        super().__init__()
        self.feed_urls = feed_urls

    def collect(self, query: str = "", max_results: int = 10) -> List[Dict]:
        """
        Collect articles from RSS feeds.

        Args:
            query: Optional filter query
            max_results: Maximum total results

        Returns:
            List of articles
        """
        all_articles = []

        for feed_url in self.feed_urls:
            try:
                feed = feedparser.parse(feed_url)

                for entry in feed.entries:
                    # Filter by query if provided
                    if query and query.lower() not in entry.title.lower():
                        continue

                    article = self._format_entry(entry, feed_url)
                    if self.validate_result(article):
                        all_articles.append(article)

                    if len(all_articles) >= max_results:
                        break

            except Exception as e:
                print(f"Error parsing feed {feed_url}: {e}")
                continue

            if len(all_articles) >= max_results:
                break

        return all_articles[:max_results]

    def _format_entry(self, entry, feed_url: str) -> Dict:
        """Format RSS entry to standard format."""
        return {
            'id': f"rss_{hash(entry.link)}",
            'content_type': 'article',
            'title': entry.title,
            'abstract': entry.get('summary', '')[:500],
            'content': entry.get('summary', ''),
            'authors': [entry.get('author', 'Unknown')],
            'publication_date': self.format_date(
                entry.get('published', '1970-01-01')
            ),
            'source_url': entry.link,
            'metadata': {
                'source': 'RSS',
                'feed_url': feed_url,
                'tags': [tag.term for tag in entry.get('tags', [])]
            }
        }

    def validate_result(self, result: Dict) -> bool:
        """Validate result."""
        return bool(result.get('title') and result.get('source_url'))
```

### 3. Web Scraper Collector

```python
from bs4 import BeautifulSoup
import requests

class WebScraperCollector(BaseCollector):
    """Scrape content from websites."""

    def __init__(self, target_urls: List[str]):
        """
        Initialize with target URLs.

        Args:
            target_urls: List of URLs to scrape
        """
        super().__init__()
        self.target_urls = target_urls

    def collect(self, query: str = "", max_results: int = 10) -> List[Dict]:
        """Scrape content from target URLs."""
        results = []

        for url in self.target_urls:
            if len(results) >= max_results:
                break

            try:
                content = self._scrape_url(url)

                # Filter by query if provided
                if query and query.lower() not in content['content'].lower():
                    continue

                if self.validate_result(content):
                    results.append(content)

            except Exception as e:
                print(f"Error scraping {url}: {e}")
                continue

        return results

    def _scrape_url(self, url: str) -> Dict:
        """Scrape single URL."""
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract content
        title = soup.find('h1').get_text() if soup.find('h1') else url
        paragraphs = soup.find_all('p')
        content = '\n\n'.join([p.get_text() for p in paragraphs])

        return {
            'id': f"web_{hash(url)}",
            'content_type': 'article',
            'title': self.clean_text(title),
            'abstract': content[:500],
            'content': content,
            'authors': ['Unknown'],
            'publication_date': '1970-01-01',
            'source_url': url,
            'metadata': {
                'source': 'Web Scraping',
                'scraped_at': datetime.now().isoformat()
            }
        }

    def validate_result(self, result: Dict) -> bool:
        """Validate result."""
        return bool(result.get('content') and len(result['content']) > 100)
```

---

## Error Handling

### Robust Error Handling Pattern

```python
class RobustCollector(BaseCollector):
    """Collector with comprehensive error handling."""

    def collect(self, query: str, max_results: int = 10) -> List[Dict]:
        """Collect with error handling."""
        results = []
        errors = []

        try:
            raw_results = self._fetch_data(query, max_results)

            for item in raw_results:
                try:
                    formatted = self._format_result(item)

                    if self.validate_result(formatted):
                        results.append(formatted)
                    else:
                        errors.append({
                            'item': item,
                            'error': 'Validation failed'
                        })

                except Exception as e:
                    errors.append({
                        'item': item,
                        'error': str(e)
                    })

        except Exception as e:
            print(f"Fatal error in collect: {e}")
            return []

        # Log errors
        if errors:
            self._log_errors(errors)

        return results

    def _log_errors(self, errors: List[Dict]):
        """Log collection errors."""
        import logging

        logging.basicConfig(filename='collector_errors.log')
        for error in errors:
            logging.error(f"Collection error: {error}")

    def _fetch_data(self, query: str, max_results: int):
        """Fetch data (implement in subclass)."""
        raise NotImplementedError

    def _format_result(self, item: Dict) -> Dict:
        """Format result (implement in subclass)."""
        raise NotImplementedError

    def validate_result(self, result: Dict) -> bool:
        """Validate result."""
        return True
```

---

## Testing Collectors

### Unit Tests

```python
import unittest

class TestCollector(unittest.TestCase):
    """Test suite for collectors."""

    def setUp(self):
        """Set up test collector."""
        self.collector = MyCollector(api_key="test_key")

    def test_collect_returns_list(self):
        """Test collect returns list."""
        results = self.collector.collect("test query", max_results=5)
        self.assertIsInstance(results, list)

    def test_collect_respects_max_results(self):
        """Test max_results parameter."""
        results = self.collector.collect("test query", max_results=5)
        self.assertLessEqual(len(results), 5)

    def test_result_format(self):
        """Test result has required fields."""
        results = self.collector.collect("test query", max_results=1)

        if results:
            result = results[0]
            required_fields = ['id', 'title', 'content_type', 'content']

            for field in required_fields:
                self.assertIn(field, result)

    def test_validation(self):
        """Test result validation."""
        valid_result = {
            'id': '123',
            'title': 'Test',
            'content_type': 'paper',
            'content': 'Content'
        }

        invalid_result = {
            'id': '123'
            # Missing required fields
        }

        self.assertTrue(self.collector.validate_result(valid_result))
        self.assertFalse(self.collector.validate_result(invalid_result))

    def test_error_handling(self):
        """Test error handling."""
        # Should not raise exception
        try:
            results = self.collector.collect("", max_results=-1)
            self.assertIsInstance(results, list)
        except Exception as e:
            self.fail(f"Collector raised exception: {e}")

if __name__ == '__main__':
    unittest.main()
```

---

## Best Practices

### 1. Rate Limiting

```python
import time
from functools import wraps

def rate_limit(calls_per_second=1):
    """Rate limiting decorator."""
    min_interval = 1.0 / calls_per_second
    last_called = [0.0]

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            wait_time = min_interval - elapsed

            if wait_time > 0:
                time.sleep(wait_time)

            result = func(*args, **kwargs)
            last_called[0] = time.time()
            return result

        return wrapper
    return decorator

# Usage
class RateLimitedCollector(BaseCollector):
    @rate_limit(calls_per_second=2)
    def _fetch_page(self, query: str):
        """Fetch page with rate limiting."""
        pass
```

### 2. Retry Logic

```python
from functools import wraps
import time

def retry(max_attempts=3, delay=1, backoff=2):
    """Retry decorator with exponential backoff."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            current_delay = delay

            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    if attempts >= max_attempts:
                        raise

                    print(f"Attempt {attempts} failed: {e}")
                    print(f"Retrying in {current_delay}s...")
                    time.sleep(current_delay)
                    current_delay *= backoff

        return wrapper
    return decorator

# Usage
@retry(max_attempts=3, delay=1, backoff=2)
def fetch_data(url):
    """Fetch data with retry."""
    response = requests.get(url)
    response.raise_for_status()
    return response.json()
```

### 3. Logging

```python
import logging

class LoggedCollector(BaseCollector):
    """Collector with comprehensive logging."""

    def __init__(self):
        super().__init__()
        self._setup_logging()

    def _setup_logging(self):
        """Set up logging."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('collector.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(self.__class__.__name__)

    def collect(self, query: str, max_results: int = 10) -> List[Dict]:
        """Collect with logging."""
        self.logger.info(f"Starting collection: query='{query}', max={max_results}")

        try:
            results = self._collect_impl(query, max_results)
            self.logger.info(f"Collected {len(results)} results")
            return results

        except Exception as e:
            self.logger.error(f"Collection failed: {e}", exc_info=True)
            return []
```

### 4. Configuration

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class CollectorConfig:
    """Configuration for collector."""
    api_key: Optional[str] = None
    base_url: str = ""
    timeout: int = 30
    max_retries: int = 3
    rate_limit: float = 1.0  # Requests per second
    cache_enabled: bool = True
    cache_ttl: int = 3600

class ConfigurableCollector(BaseCollector):
    """Collector with configuration."""

    def __init__(self, config: CollectorConfig):
        """Initialize with configuration."""
        super().__init__(config.api_key)
        self.config = config

    def collect(self, query: str, max_results: int = 10) -> List[Dict]:
        """Collect using configuration."""
        # Use config values
        pass

# Usage
config = CollectorConfig(
    api_key="your_key",
    base_url="https://api.example.com",
    timeout=60,
    max_retries=5
)

collector = ConfigurableCollector(config)
```

---

## Integration with System

### Register Collector

```python
# In main.py
from multi_modal_rag.data_collectors.custom_collector import CustomCollector

# Register collector
data_collectors = {
    'arxiv': arxiv_collector,
    'youtube': youtube_collector,
    'custom': CustomCollector()  # Add your collector
}

# Use in UI (gradio_app.py)
collector_choice = gr.Dropdown(
    choices=['arxiv', 'youtube', 'custom'],
    label="Data Source"
)
```

---

## Additional Resources

- [requests Documentation](https://docs.python-requests.org/)
- [BeautifulSoup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [aiohttp Documentation](https://docs.aiohttp.org/)
- [API Best Practices](https://restfulapi.net/)

## Summary

**Key Points**:
1. Follow standard data format
2. Implement error handling
3. Add rate limiting
4. Include logging
5. Write tests
6. Document your collector
7. Consider caching

**Quick Start Checklist**:
- [ ] Create collector class inheriting from BaseCollector
- [ ] Implement collect() method
- [ ] Implement validate_result() method
- [ ] Add error handling
- [ ] Test with sample queries
- [ ] Document usage
- [ ] Register in main.py
