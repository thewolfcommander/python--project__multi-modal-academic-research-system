# Tutorial: Extending the System

This tutorial teaches you how to extend and customize the Multi-Modal Academic Research System. You'll learn how to add new data collectors, create custom processors, modify the UI, add search filters, and contribute back to the project.

## Table of Contents

1. [System Architecture Overview](#system-architecture-overview)
2. [Adding New Data Collectors](#adding-new-data-collectors)
3. [Creating Custom Processors](#creating-custom-processors)
4. [Modifying the UI](#modifying-the-ui)
5. [Adding New Search Filters](#adding-new-search-filters)
6. [Contributing Back to the Project](#contributing-back-to-the-project)

## System Architecture Overview

### Component Structure

```
multi_modal_rag/
├── data_collectors/      # Collect content from sources
├── data_processors/      # Process and extract information
├── indexing/            # OpenSearch indexing and search
├── orchestration/       # Query orchestration and citations
├── ui/                  # Gradio and web interfaces
├── api/                 # FastAPI endpoints
└── database/            # SQLite database management
```

### Data Flow

1. **Collection** - Data collectors fetch content
2. **Processing** - Processors extract text, metadata, and insights
3. **Indexing** - Content is indexed in OpenSearch
4. **Retrieval** - Hybrid search retrieves relevant documents
5. **Generation** - LLM generates answers with citations

### Key Design Principles

- **Modularity:** Each component is independent
- **Extensibility:** Easy to add new sources and processors
- **Consistency:** Standard interfaces for collectors and processors
- **Robustness:** Comprehensive error handling and logging

## Adding New Data Collectors

### Data Collector Interface

All data collectors should follow this pattern:

```python
from typing import List, Dict
import os

class BaseCollector:
    """Base class for data collectors"""

    def __init__(self, save_dir: str = "data/custom"):
        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)

    def collect(self, query: str, max_results: int = 50) -> List[Dict]:
        """
        Collect data from source

        Args:
            query: Search query
            max_results: Maximum number of results

        Returns:
            List of dictionaries with standardized fields:
            - title: str
            - content: str (or abstract, description)
            - authors: List[str]
            - url: str
            - published: str (ISO format date)
            - metadata: Dict (source-specific data)
        """
        raise NotImplementedError
```

### Example: Adding a Blog Post Collector

Create a new file: `multi_modal_rag/data_collectors/blog_collector.py`

```python
import requests
from typing import List, Dict
import feedparser
import time
from datetime import datetime

class BlogCollector:
    """Collect blog posts from RSS feeds"""

    def __init__(self, save_dir: str = "data/blogs"):
        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)

    def collect_from_feed(self, feed_url: str, max_results: int = 20) -> List[Dict]:
        """Collect posts from a single RSS feed"""

        posts = []

        try:
            # Parse RSS feed
            feed = feedparser.parse(feed_url)

            for entry in feed.entries[:max_results]:
                post_data = {
                    'title': entry.get('title', 'Untitled'),
                    'content': entry.get('summary', ''),
                    'authors': [entry.get('author', 'Unknown')],
                    'url': entry.get('link', ''),
                    'published': entry.get('published', datetime.now().isoformat()),
                    'metadata': {
                        'feed_url': feed_url,
                        'feed_title': feed.feed.get('title', ''),
                        'tags': [tag.term for tag in entry.get('tags', [])]
                    }
                }

                posts.append(post_data)

            time.sleep(1)  # Be respectful

        except Exception as e:
            print(f"Error collecting from {feed_url}: {e}")

        return posts

    def collect_from_multiple_feeds(
        self,
        feed_urls: List[str],
        max_per_feed: int = 10
    ) -> List[Dict]:
        """Collect from multiple RSS feeds"""

        all_posts = []

        for feed_url in feed_urls:
            posts = self.collect_from_feed(feed_url, max_per_feed)
            all_posts.extend(posts)

        return all_posts

    def get_ml_blogs(self) -> Dict[str, str]:
        """Curated list of machine learning blogs"""
        return {
            'Google AI Blog': 'https://ai.googleblog.com/feeds/posts/default',
            'OpenAI Blog': 'https://openai.com/blog/rss.xml',
            'DeepMind Blog': 'https://deepmind.com/blog/feed/basic',
            'Meta AI': 'https://ai.facebook.com/blog/rss/',
            'Distill': 'https://distill.pub/rss.xml'
        }

    def collect_ml_blogs(self, max_per_blog: int = 5) -> List[Dict]:
        """Collect posts from ML blogs"""

        blogs = self.get_ml_blogs()
        return self.collect_from_multiple_feeds(
            list(blogs.values()),
            max_per_blog
        )
```

### Example: Adding a GitHub Repository Collector

```python
import requests
from typing import List, Dict
import base64
import time

class GitHubCollector:
    """Collect content from GitHub repositories"""

    def __init__(self, github_token: str = None):
        self.token = github_token
        self.headers = {}
        if github_token:
            self.headers['Authorization'] = f'token {github_token}'

    def search_repositories(
        self,
        query: str,
        max_results: int = 30
    ) -> List[Dict]:
        """Search GitHub repositories"""

        repos = []
        url = 'https://api.github.com/search/repositories'

        params = {
            'q': query,
            'sort': 'stars',
            'order': 'desc',
            'per_page': min(max_results, 100)
        }

        try:
            response = requests.get(url, params=params, headers=self.headers)
            response.raise_for_status()
            data = response.json()

            for item in data.get('items', [])[:max_results]:
                # Get README content
                readme_content = self._get_readme(
                    item['owner']['login'],
                    item['name']
                )

                repo_data = {
                    'title': f"{item['full_name']}: {item['description'] or 'No description'}",
                    'content': readme_content,
                    'authors': [item['owner']['login']],
                    'url': item['html_url'],
                    'published': item.get('created_at', ''),
                    'metadata': {
                        'stars': item['stargazers_count'],
                        'forks': item['forks_count'],
                        'language': item.get('language', 'Unknown'),
                        'topics': item.get('topics', []),
                        'updated_at': item.get('updated_at', '')
                    }
                }

                repos.append(repo_data)

                time.sleep(1)  # Rate limiting

        except Exception as e:
            print(f"Error searching repositories: {e}")

        return repos

    def _get_readme(self, owner: str, repo: str) -> str:
        """Get README content from repository"""

        url = f'https://api.github.com/repos/{owner}/{repo}/readme'

        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()

            # Decode base64 content
            content = base64.b64decode(data['content']).decode('utf-8')
            return content

        except Exception as e:
            return f"README not available: {e}"
```

### Registering Your Collector

Add your collector to `main.py`:

```python
from multi_modal_rag.data_collectors.blog_collector import BlogCollector
from multi_modal_rag.data_collectors.github_collector import GitHubCollector

# In main() function
blog_collector = BlogCollector()
github_collector = GitHubCollector(github_token=os.getenv('GITHUB_TOKEN'))

data_collectors = {
    'paper_collector': paper_collector,
    'video_collector': video_collector,
    'podcast_collector': podcast_collector,
    'blog_collector': blog_collector,          # Add new collector
    'github_collector': github_collector       # Add new collector
}
```

Update the UI in `gradio_app.py`:

```python
# In create_interface() method
collection_type = gr.Radio(
    ["ArXiv Papers", "YouTube Lectures", "Podcasts", "Blog Posts", "GitHub Repos"],
    label="Data Source"
)
```

Add handling in `handle_data_collection()`:

```python
elif source_type == "Blog Posts":
    status_updates.append("Collecting blog posts...")
    posts = self.data_collectors['blog_collector'].collect_ml_blogs(max_results=max_results)
    collected_items = posts
    results['posts_collected'] = len(posts)
    status_updates.append(f"Collected {len(posts)} blog posts")

elif source_type == "GitHub Repos":
    status_updates.append("Searching GitHub repositories...")
    repos = self.data_collectors['github_collector'].search_repositories(query, max_results)
    collected_items = repos
    results['repos_collected'] = len(repos)
    status_updates.append(f"Collected {len(repos)} repositories")
```

## Creating Custom Processors

### Processor Interface

Processors transform raw content into searchable documents:

```python
from typing import Dict, List
import os

class BaseProcessor:
    """Base class for data processors"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key

    def process(self, raw_data: Dict) -> Dict:
        """
        Process raw data into structured format

        Args:
            raw_data: Raw data from collector

        Returns:
            Processed document with fields:
            - title: str
            - content: str
            - key_concepts: List[str]
            - summary: str
            - metadata: Dict
        """
        raise NotImplementedError
```

### Example: Blog Post Processor

Create `multi_modal_rag/data_processors/blog_processor.py`:

```python
import google.generativeai as genai
from typing import Dict, List
import re

class BlogProcessor:
    """Process blog posts with LLM analysis"""

    def __init__(self, gemini_api_key: str):
        self.api_key = gemini_api_key
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel('gemini-pro')

    def process(self, blog_post: Dict) -> Dict:
        """Process a blog post"""

        # Extract text content
        content = blog_post.get('content', '')

        # Remove HTML tags
        content_clean = re.sub(r'<[^>]+>', '', content)

        # Use LLM to extract key concepts and summary
        prompt = f"""
        Analyze this blog post and extract:
        1. Key concepts (5-10 main topics/technologies discussed)
        2. A concise 2-3 sentence summary

        Blog post:
        {content_clean[:2000]}

        Return in this format:
        KEY CONCEPTS: concept1, concept2, concept3, ...
        SUMMARY: summary text here
        """

        try:
            response = self.model.generate_content(prompt)
            analysis = response.text

            # Parse response
            key_concepts = []
            summary = ""

            if "KEY CONCEPTS:" in analysis:
                concepts_line = analysis.split("KEY CONCEPTS:")[1].split("SUMMARY:")[0]
                key_concepts = [c.strip() for c in concepts_line.split(",")]

            if "SUMMARY:" in analysis:
                summary = analysis.split("SUMMARY:")[1].strip()

        except Exception as e:
            print(f"Error in LLM analysis: {e}")
            key_concepts = []
            summary = content_clean[:200]

        # Create processed document
        processed = {
            'title': blog_post['title'],
            'content': content_clean,
            'authors': blog_post.get('authors', []),
            'url': blog_post.get('url', ''),
            'publication_date': blog_post.get('published', ''),
            'key_concepts': key_concepts,
            'summary': summary,
            'metadata': {
                'source': 'blog',
                'feed_url': blog_post.get('metadata', {}).get('feed_url', ''),
                'tags': blog_post.get('metadata', {}).get('tags', [])
            }
        }

        return processed

    def batch_process(self, blog_posts: List[Dict]) -> List[Dict]:
        """Process multiple blog posts"""

        processed = []

        for post in blog_posts:
            try:
                processed_post = self.process(post)
                processed.append(processed_post)
            except Exception as e:
                print(f"Error processing post '{post.get('title', 'Unknown')}': {e}")

        return processed
```

### Example: Code Repository Processor

```python
import google.generativeai as genai
from typing import Dict, List

class RepositoryProcessor:
    """Process GitHub repositories"""

    def __init__(self, gemini_api_key: str):
        self.api_key = gemini_api_key
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel('gemini-pro')

    def process(self, repo: Dict) -> Dict:
        """Process a repository"""

        readme = repo.get('content', '')
        metadata = repo.get('metadata', {})

        # Analyze README with LLM
        prompt = f"""
        Analyze this GitHub repository README and extract:
        1. Main purpose/functionality
        2. Key technologies used
        3. Use cases
        4. Target audience

        Repository: {repo['title']}
        Language: {metadata.get('language', 'Unknown')}
        Stars: {metadata.get('stars', 0)}

        README:
        {readme[:3000]}

        Provide a structured analysis.
        """

        try:
            response = self.model.generate_content(prompt)
            analysis = response.text

            # Extract key concepts from topics and language
            key_concepts = metadata.get('topics', [])
            if metadata.get('language'):
                key_concepts.append(metadata['language'])

        except Exception as e:
            print(f"Error analyzing repository: {e}")
            analysis = readme[:500]
            key_concepts = metadata.get('topics', [])

        processed = {
            'title': repo['title'],
            'content': readme,
            'authors': repo.get('authors', []),
            'url': repo.get('url', ''),
            'publication_date': repo.get('published', ''),
            'key_concepts': key_concepts,
            'summary': analysis,
            'metadata': {
                'source': 'github',
                'stars': metadata.get('stars', 0),
                'forks': metadata.get('forks', 0),
                'language': metadata.get('language', ''),
                'topics': metadata.get('topics', [])
            }
        }

        return processed
```

## Modifying the UI

### Adding New Tabs to Gradio

Edit `multi_modal_rag/ui/gradio_app.py`:

```python
# In create_interface() method

with gr.Tabs():
    # ... existing tabs ...

    # Add new Analytics tab
    with gr.TabItem("Analytics"):
        with gr.Row():
            with gr.Column():
                gr.Markdown("### Collection Analytics")

                date_range = gr.Radio(
                    ["Last 7 days", "Last 30 days", "All time"],
                    value="Last 30 days",
                    label="Time Range"
                )

                metric_type = gr.Radio(
                    ["Collection Volume", "Source Distribution", "Popular Topics"],
                    value="Collection Volume",
                    label="Metric"
                )

                generate_chart_btn = gr.Button("Generate Chart")

            with gr.Column():
                chart_output = gr.Plot(label="Visualization")
                metrics_table = gr.Dataframe(label="Detailed Metrics")

        # Event handler
        generate_chart_btn.click(
            fn=self.generate_analytics,
            inputs=[date_range, metric_type],
            outputs=[chart_output, metrics_table]
        )
```

Add the analytics method:

```python
def generate_analytics(self, date_range: str, metric_type: str):
    """Generate analytics visualizations"""
    import plotly.graph_objects as go
    import pandas as pd
    from datetime import datetime, timedelta

    # Determine date filter
    if date_range == "Last 7 days":
        days = 7
    elif date_range == "Last 30 days":
        days = 30
    else:
        days = None

    # Get collections from database
    if days:
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        collections = [
            c for c in self.db_manager.get_all_collections(limit=1000)
            if c['collection_date'] >= cutoff
        ]
    else:
        collections = self.db_manager.get_all_collections(limit=1000)

    # Generate visualization based on metric type
    if metric_type == "Collection Volume":
        # Group by date
        df = pd.DataFrame(collections)
        df['date'] = pd.to_datetime(df['collection_date']).dt.date
        daily_counts = df.groupby('date').size()

        fig = go.Figure(data=[
            go.Bar(x=daily_counts.index, y=daily_counts.values)
        ])
        fig.update_layout(title="Daily Collection Volume")

        metrics = daily_counts.reset_index()
        metrics.columns = ['Date', 'Count']

    elif metric_type == "Source Distribution":
        # Group by source
        df = pd.DataFrame(collections)
        source_counts = df['source'].value_counts()

        fig = go.Figure(data=[
            go.Pie(labels=source_counts.index, values=source_counts.values)
        ])
        fig.update_layout(title="Distribution by Source")

        metrics = source_counts.reset_index()
        metrics.columns = ['Source', 'Count']

    else:  # Popular Topics
        # Extract topics from metadata
        topics = {}
        for c in collections:
            metadata = c.get('metadata', {})
            if isinstance(metadata, dict):
                for topic in metadata.get('topics', []):
                    topics[topic] = topics.get(topic, 0) + 1

        top_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)[:20]

        fig = go.Figure(data=[
            go.Bar(x=[t[0] for t in top_topics], y=[t[1] for t in top_topics])
        ])
        fig.update_layout(title="Top 20 Topics")

        metrics = pd.DataFrame(top_topics, columns=['Topic', 'Count'])

    return fig, metrics
```

### Customizing the UI Appearance

Add custom CSS:

```python
# In create_interface() method

with gr.Blocks(
    title="Multi-Modal Research Assistant",
    theme=gr.themes.Base(),
    css="""
    .gradio-container {
        max-width: 1200px !important;
    }
    .tab-nav button {
        font-size: 16px;
        font-weight: bold;
    }
    .citation-box {
        background-color: #f0f0f0;
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
    }
    """
) as app:
    # ... rest of UI code ...
```

### Adding Custom Components

Create reusable UI components:

```python
def create_search_filters(self):
    """Create reusable search filter component"""

    with gr.Group():
        gr.Markdown("### Search Filters")

        content_type = gr.CheckboxGroup(
            ["Papers", "Videos", "Podcasts", "Blogs", "Repositories"],
            value=["Papers", "Videos", "Podcasts"],
            label="Content Types"
        )

        date_range = gr.Slider(
            minimum=7,
            maximum=365,
            value=30,
            step=1,
            label="Days back"
        )

        min_citations = gr.Slider(
            minimum=0,
            maximum=100,
            value=0,
            step=1,
            label="Minimum citations"
        )

    return content_type, date_range, min_citations
```

## Adding New Search Filters

### Extending OpenSearch Queries

Edit `multi_modal_rag/indexing/opensearch_manager.py`:

```python
def advanced_search(
    self,
    index_name: str,
    query: str,
    content_types: List[str] = None,
    min_date: str = None,
    max_date: str = None,
    authors: List[str] = None,
    min_citations: int = 0,
    k: int = 10
) -> List[Dict]:
    """Advanced search with multiple filters"""

    # Build base query
    must_clauses = [
        {
            'multi_match': {
                'query': query,
                'fields': ['title^3', 'abstract^2', 'content', 'transcript'],
                'fuzziness': 'AUTO'
            }
        }
    ]

    # Build filters
    filter_clauses = []

    # Content type filter
    if content_types:
        filter_clauses.append({
            'terms': {'content_type': content_types}
        })

    # Date range filter
    if min_date or max_date:
        date_filter = {'range': {'publication_date': {}}}
        if min_date:
            date_filter['range']['publication_date']['gte'] = min_date
        if max_date:
            date_filter['range']['publication_date']['lte'] = max_date
        filter_clauses.append(date_filter)

    # Author filter
    if authors:
        filter_clauses.append({
            'terms': {'authors': authors}
        })

    # Citation count filter (if you track this)
    if min_citations > 0:
        filter_clauses.append({
            'range': {'metadata.citation_count': {'gte': min_citations}}
        })

    # Construct full query
    search_query = {
        'size': k,
        'query': {
            'bool': {
                'must': must_clauses,
                'filter': filter_clauses
            }
        }
    }

    response = self.client.search(index=index_name, body=search_query)

    results = []
    for hit in response['hits']['hits']:
        results.append({
            'score': hit['_score'],
            'source': hit['_source']
        })

    return results
```

### Adding Faceted Search

```python
def faceted_search(
    self,
    index_name: str,
    query: str,
    k: int = 10
) -> Dict:
    """Search with facets for filtering"""

    search_query = {
        'size': k,
        'query': {
            'multi_match': {
                'query': query,
                'fields': ['title', 'abstract', 'content']
            }
        },
        'aggs': {
            'content_types': {
                'terms': {'field': 'content_type', 'size': 10}
            },
            'authors': {
                'terms': {'field': 'authors', 'size': 20}
            },
            'publication_years': {
                'date_histogram': {
                    'field': 'publication_date',
                    'calendar_interval': 'year'
                }
            },
            'topics': {
                'terms': {'field': 'key_concepts', 'size': 30}
            }
        }
    }

    response = self.client.search(index=index_name, body=search_query)

    return {
        'results': [
            {'score': hit['_score'], 'source': hit['_source']}
            for hit in response['hits']['hits']
        ],
        'facets': response['aggregations']
    }
```

## Contributing Back to the Project

### Setting Up for Development

1. **Fork the repository**
2. **Clone your fork:**
   ```bash
   git clone https://github.com/your-username/multi-modal-academic-research-system.git
   cd multi-modal-academic-research-system
   ```

3. **Create a development branch:**
   ```bash
   git checkout -b feature/new-collector
   ```

4. **Install development dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install pytest black flake8 mypy
   ```

### Code Quality Standards

**Format code with Black:**
```bash
black multi_modal_rag/
```

**Lint with flake8:**
```bash
flake8 multi_modal_rag/ --max-line-length=100
```

**Type checking with mypy:**
```bash
mypy multi_modal_rag/
```

### Writing Tests

Create tests in `tests/` directory:

```python
# tests/test_blog_collector.py
import pytest
from multi_modal_rag.data_collectors.blog_collector import BlogCollector

def test_blog_collector_initialization():
    """Test blog collector initializes correctly"""
    collector = BlogCollector()
    assert collector.save_dir == "data/blogs"

def test_collect_from_feed():
    """Test collecting from a single feed"""
    collector = BlogCollector()

    # Use a known test feed
    posts = collector.collect_from_feed(
        'https://ai.googleblog.com/feeds/posts/default',
        max_results=5
    )

    assert len(posts) > 0
    assert 'title' in posts[0]
    assert 'content' in posts[0]
    assert 'url' in posts[0]

def test_ml_blogs():
    """Test ML blog list"""
    collector = BlogCollector()
    blogs = collector.get_ml_blogs()

    assert isinstance(blogs, dict)
    assert len(blogs) > 0
```

Run tests:
```bash
pytest tests/
```

### Documentation

Add docstrings to your code:

```python
def collect_from_feed(self, feed_url: str, max_results: int = 20) -> List[Dict]:
    """
    Collect blog posts from an RSS feed.

    Args:
        feed_url (str): URL of the RSS feed
        max_results (int): Maximum number of posts to collect

    Returns:
        List[Dict]: List of blog post dictionaries with keys:
            - title: Post title
            - content: Post content/summary
            - authors: List of authors
            - url: Post URL
            - published: Publication date (ISO format)
            - metadata: Additional metadata

    Raises:
        ValueError: If feed_url is invalid
        ConnectionError: If feed cannot be accessed

    Example:
        >>> collector = BlogCollector()
        >>> posts = collector.collect_from_feed(
        ...     'https://example.com/feed.xml',
        ...     max_results=10
        ... )
        >>> len(posts)
        10
    """
    # Implementation
```

### Submitting a Pull Request

1. **Commit your changes:**
   ```bash
   git add .
   git commit -m "Add blog post collector with RSS feed support"
   ```

2. **Push to your fork:**
   ```bash
   git push origin feature/new-collector
   ```

3. **Create Pull Request:**
   - Go to the original repository
   - Click "New Pull Request"
   - Select your branch
   - Describe your changes

4. **PR Description Template:**
   ```markdown
   ## Description
   Adds a new blog post collector that can fetch posts from RSS feeds.

   ## Changes
   - Added `BlogCollector` class in `data_collectors/blog_collector.py`
   - Added `BlogProcessor` class in `data_processors/blog_processor.py`
   - Updated `main.py` to register the new collector
   - Added tests in `tests/test_blog_collector.py`

   ## Testing
   - [ ] Tested with multiple RSS feeds
   - [ ] Added unit tests
   - [ ] Verified integration with existing system
   - [ ] Checked code formatting (black, flake8)

   ## Documentation
   - [ ] Added docstrings
   - [ ] Updated README if necessary
   - [ ] Added usage examples
   ```

### Best Practices for Contributors

1. **Keep changes focused:** One feature per PR
2. **Write tests:** Maintain test coverage
3. **Document thoroughly:** Clear docstrings and comments
4. **Follow existing patterns:** Match the codebase style
5. **Test integration:** Ensure new code works with existing features
6. **Be responsive:** Address review feedback promptly

## Next Steps

- Review [Collecting Papers](collect-papers.md) for data collection basics
- Explore [Custom Searches](custom-searches.md) for advanced queries
- Check [Exporting Citations](export-citations.md) for citation management
- Learn [Visualization Dashboard](visualization.md) for data analysis

## Additional Resources

- **OpenSearch Documentation:** https://opensearch.org/docs/
- **Gradio Documentation:** https://gradio.app/docs/
- **FastAPI Documentation:** https://fastapi.tiangolo.com/
- **LangChain Documentation:** https://python.langchain.com/
- **Google Gemini API:** https://ai.google.dev/docs
