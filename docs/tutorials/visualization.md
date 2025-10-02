# Tutorial: Visualization Dashboard

This tutorial shows you how to use the FastAPI visualization dashboard to explore and analyze your collected research data. You'll learn how to start the dashboard, interpret statistics, filter and search data, export visualizations, and create custom views.

## Table of Contents

1. [Starting the Dashboard](#starting-the-dashboard)
2. [Understanding Statistics](#understanding-statistics)
3. [Filtering and Searching](#filtering-and-searching)
4. [Exporting Data](#exporting-data)
5. [Custom Visualizations](#custom-visualizations)
6. [Using the API](#using-the-api)
7. [Advanced Features](#advanced-features)

## Starting the Dashboard

### Prerequisites

Ensure your environment is set up:

```bash
# Activate virtual environment
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Verify FastAPI and Uvicorn are installed
pip install fastapi uvicorn
```

### Method 1: Using the Start Script

The easiest way to start the dashboard:

```bash
python start_api_server.py
```

You should see output like:
```
Starting FastAPI Visualization Server...
Dashboard will be available at: http://localhost:8000/viz
API endpoints at: http://localhost:8000/api/
API docs at: http://localhost:8000/docs
Press CTRL+C to stop the server

INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### Method 2: Using Uvicorn Directly

For more control:

```bash
uvicorn multi_modal_rag.api.api_server:app --host 0.0.0.0 --port 8000 --reload
```

Options:
- `--host 0.0.0.0`: Makes server accessible from network
- `--port 8000`: Specify port (default 8000)
- `--reload`: Auto-reload on code changes (development)

### Method 3: Custom Port

Run on a different port:

```bash
python -c "import uvicorn; uvicorn.run('multi_modal_rag.api.api_server:app', host='0.0.0.0', port=8080)"
```

### Accessing the Dashboard

Once started, open your browser:

1. **Visualization Dashboard:** http://localhost:8000/viz
2. **API Documentation:** http://localhost:8000/docs
3. **API Root:** http://localhost:8000/

### Running Alongside Gradio UI

You can run both interfaces simultaneously:

**Terminal 1 - Gradio UI:**
```bash
python main.py
# Runs on port 7860
```

**Terminal 2 - FastAPI Dashboard:**
```bash
python start_api_server.py
# Runs on port 8000
```

## Understanding Statistics

### Viewing Statistics in Gradio UI

The Gradio UI provides basic statistics:

1. Open Gradio interface at http://localhost:7860
2. Go to **"Data Visualization"** tab
3. Click **"Refresh Statistics"**

### Understanding the Statistics Display

**Quick Stats Section:**
```
Overview
- Total Collections: 45
- Indexed: 42 (93.3%)
- Recent (7 days): 12

By Type
- Papers: 30
- Videos: 10
- Podcasts: 5
```

**JSON Statistics:**
```json
{
  "total_collections": 45,
  "by_type": {
    "paper": 30,
    "video": 10,
    "podcast": 5
  },
  "indexed": 42,
  "not_indexed": 3,
  "recent_7_days": 12,
  "recent_30_days": 35,
  "by_source": {
    "arxiv": 25,
    "youtube": 10,
    "semantic_scholar": 5,
    "rss": 5
  }
}
```

### Using the API for Statistics

Get statistics programmatically:

```python
import requests

# Get statistics
response = requests.get('http://localhost:8000/api/statistics')
stats = response.json()

print(f"Total collections: {stats['total_collections']}")
print(f"Indexed: {stats['indexed']}")
print(f"By type: {stats['by_type']}")
```

### Creating Visual Reports

Generate visual statistics report:

```python
import requests
import matplotlib.pyplot as plt

# Fetch statistics
response = requests.get('http://localhost:8000/api/statistics')
stats = response.json()

# Create pie chart of content types
by_type = stats['by_type']

plt.figure(figsize=(10, 5))

# Pie chart for content types
plt.subplot(1, 2, 1)
plt.pie(
    by_type.values(),
    labels=by_type.keys(),
    autopct='%1.1f%%',
    startangle=90
)
plt.title('Collections by Content Type')

# Bar chart for sources
by_source = stats['by_source']
plt.subplot(1, 2, 2)
plt.bar(by_source.keys(), by_source.values())
plt.title('Collections by Source')
plt.xlabel('Source')
plt.ylabel('Count')
plt.xticks(rotation=45)

plt.tight_layout()
plt.savefig('collection_statistics.png')
plt.show()

print("Statistics visualization saved to collection_statistics.png")
```

### Time-Based Statistics

Analyze collection trends over time:

```python
import requests
from datetime import datetime, timedelta
from collections import defaultdict
import matplotlib.pyplot as plt

# Fetch all collections
response = requests.get('http://localhost:8000/api/collections?limit=1000')
collections = response.json()['collections']

# Group by date
by_date = defaultdict(int)

for item in collections:
    date = item['collection_date'].split('T')[0]  # Extract date part
    by_date[date] += 1

# Sort by date
dates = sorted(by_date.keys())
counts = [by_date[d] for d in dates]

# Plot timeline
plt.figure(figsize=(12, 6))
plt.plot(dates, counts, marker='o')
plt.title('Collection Activity Over Time')
plt.xlabel('Date')
plt.ylabel('Number of Collections')
plt.xticks(rotation=45)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('collection_timeline.png')
plt.show()

print("Timeline saved to collection_timeline.png")
```

## Filtering and Searching

### Using the Gradio Interface

**Filter by Content Type:**

1. Go to **"Data Visualization"** tab
2. Select content type: All, Papers, Videos, or Podcasts
3. Adjust the limit slider (10-100 items)
4. Click **"Load Collections"**

**Results displayed in table:**
```
ID | Type   | Title                           | Source  | Indexed | Date
1  | paper  | Attention is All You Need      | arxiv   | Yes     | 2024-01-15
2  | video  | Deep Learning Fundamentals     | youtube | Yes     | 2024-01-16
```

### Using the API for Filtering

**Filter by content type:**

```python
import requests

# Get only papers
response = requests.get('http://localhost:8000/api/collections?content_type=paper&limit=50')
papers = response.json()

print(f"Found {papers['count']} papers")
for paper in papers['collections'][:5]:
    print(f"  - {paper['title']}")
```

**Filter with pagination:**

```python
# Get first 20 items
response = requests.get('http://localhost:8000/api/collections?limit=20&offset=0')
page1 = response.json()

# Get next 20 items
response = requests.get('http://localhost:8000/api/collections?limit=20&offset=20')
page2 = response.json()

print(f"Page 1: {len(page1['collections'])} items")
print(f"Page 2: {len(page2['collections'])} items")
```

### Search Functionality

**Search by title or source:**

```python
import requests

# Search for "machine learning"
response = requests.get(
    'http://localhost:8000/api/search',
    params={'q': 'machine learning', 'limit': 20}
)

results = response.json()

print(f"Query: {results['query']}")
print(f"Found {results['count']} results")

for item in results['results']:
    print(f"\n{item['title']}")
    print(f"  Type: {item['content_type']}")
    print(f"  Source: {item['source']}")
```

### Advanced Filtering Script

Create a comprehensive filtering script:

```python
import requests
from datetime import datetime, timedelta

def advanced_filter(
    content_type=None,
    indexed_only=True,
    recent_days=None,
    search_term=None,
    limit=100
):
    """Advanced filtering of collections"""

    # Fetch all collections
    params = {'limit': limit}
    if content_type:
        params['content_type'] = content_type

    response = requests.get('http://localhost:8000/api/collections', params=params)
    collections = response.json()['collections']

    # Apply filters
    filtered = collections

    # Filter by indexed status
    if indexed_only:
        filtered = [c for c in filtered if c['indexed']]

    # Filter by recency
    if recent_days:
        cutoff = datetime.now() - timedelta(days=recent_days)
        filtered = [
            c for c in filtered
            if datetime.fromisoformat(c['collection_date'].replace('Z', '+00:00')) > cutoff
        ]

    # Filter by search term
    if search_term:
        search_lower = search_term.lower()
        filtered = [
            c for c in filtered
            if search_lower in c['title'].lower() or
               search_lower in (c['source'] or '').lower()
        ]

    return filtered

# Example usage
results = advanced_filter(
    content_type='paper',
    indexed_only=True,
    recent_days=30,
    search_term='neural network',
    limit=200
)

print(f"Found {len(results)} matching collections")
for item in results[:10]:
    print(f"  - {item['title']} ({item['collection_date'][:10]})")
```

### Combining Multiple Filters

```python
import requests

def complex_search(
    keywords,
    content_types=['paper', 'video', 'podcast'],
    min_date='2023-01-01',
    sources=None
):
    """Complex search with multiple criteria"""

    all_results = []

    for content_type in content_types:
        response = requests.get(
            'http://localhost:8000/api/collections',
            params={'content_type': content_type, 'limit': 500}
        )

        items = response.json()['collections']

        for item in items:
            # Check date
            if item['collection_date'] < min_date:
                continue

            # Check source
            if sources and item['source'] not in sources:
                continue

            # Check keywords
            text = f"{item['title']} {item.get('source', '')}".lower()
            if any(kw.lower() in text for kw in keywords):
                all_results.append(item)

    # Remove duplicates
    seen = set()
    unique_results = []

    for item in all_results:
        if item['id'] not in seen:
            seen.add(item['id'])
            unique_results.append(item)

    return unique_results

# Search for machine learning papers from arxiv in 2023+
results = complex_search(
    keywords=['machine learning', 'deep learning'],
    content_types=['paper'],
    min_date='2023-01-01',
    sources=['arxiv']
)

print(f"Found {len(results)} matching items")
```

## Exporting Data

### Export Collection Data

**Export as JSON:**

```python
import requests
import json

# Fetch all collections
response = requests.get('http://localhost:8000/api/collections?limit=1000')
data = response.json()

# Save to file
with open('all_collections.json', 'w') as f:
    json.dump(data, f, indent=2)

print(f"Exported {data['count']} collections to all_collections.json")
```

**Export as CSV:**

```python
import requests
import csv

# Fetch collections
response = requests.get('http://localhost:8000/api/collections?limit=1000')
collections = response.json()['collections']

# Write to CSV
with open('collections.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)

    # Header
    writer.writerow(['ID', 'Type', 'Title', 'Source', 'Indexed', 'Date', 'URL'])

    # Data
    for item in collections:
        writer.writerow([
            item['id'],
            item['content_type'],
            item['title'],
            item['source'] or 'N/A',
            'Yes' if item['indexed'] else 'No',
            item['collection_date'].split('T')[0],
            item.get('url', 'N/A')
        ])

print(f"Exported {len(collections)} collections to collections.csv")
```

**Export filtered data:**

```python
import requests
import pandas as pd

# Get papers only
response = requests.get('http://localhost:8000/api/collections?content_type=paper&limit=500')
papers = response.json()['collections']

# Create DataFrame
df = pd.DataFrame(papers)

# Export to Excel
df.to_excel('papers_collection.xlsx', index=False)

# Export to CSV
df.to_csv('papers_collection.csv', index=False)

print(f"Exported {len(papers)} papers to Excel and CSV")
```

### Export Statistics Summary

```python
import requests
import json

# Fetch statistics
response = requests.get('http://localhost:8000/api/statistics')
stats = response.json()

# Create summary report
report = {
    'generated_at': datetime.now().isoformat(),
    'statistics': stats,
    'summary': {
        'total_items': stats['total_collections'],
        'completion_rate': f"{(stats['indexed'] / stats['total_collections'] * 100):.1f}%",
        'recent_activity_7d': stats['recent_7_days'],
        'recent_activity_30d': stats['recent_30_days']
    }
}

# Save report
with open('statistics_report.json', 'w') as f:
    json.dump(report, f, indent=2)

print("Statistics report saved to statistics_report.json")
```

## Custom Visualizations

### Creating Interactive Charts

Using Plotly for interactive visualizations:

```python
import requests
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Fetch statistics
response = requests.get('http://localhost:8000/api/statistics')
stats = response.json()

# Create subplots
fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=(
        'Content Type Distribution',
        'Source Distribution',
        'Indexing Status',
        'Recent Activity'
    ),
    specs=[
        [{'type': 'pie'}, {'type': 'bar'}],
        [{'type': 'pie'}, {'type': 'bar'}]
    ]
)

# Content type pie chart
by_type = stats['by_type']
fig.add_trace(
    go.Pie(labels=list(by_type.keys()), values=list(by_type.values())),
    row=1, col=1
)

# Source bar chart
by_source = stats['by_source']
fig.add_trace(
    go.Bar(x=list(by_source.keys()), y=list(by_source.values())),
    row=1, col=2
)

# Indexing status pie chart
indexing = {
    'Indexed': stats['indexed'],
    'Not Indexed': stats['not_indexed']
}
fig.add_trace(
    go.Pie(labels=list(indexing.keys()), values=list(indexing.values())),
    row=2, col=1
)

# Recent activity bar chart
recent = {
    '7 days': stats['recent_7_days'],
    '30 days': stats['recent_30_days']
}
fig.add_trace(
    go.Bar(x=list(recent.keys()), y=list(recent.values())),
    row=2, col=2
)

# Update layout
fig.update_layout(
    height=800,
    showlegend=True,
    title_text="Research Collection Dashboard"
)

# Save to HTML
fig.write_html('dashboard.html')
print("Interactive dashboard saved to dashboard.html")

# Show in browser
fig.show()
```

### Time Series Visualization

```python
import requests
import plotly.express as px
from datetime import datetime
import pandas as pd

# Fetch all collections
response = requests.get('http://localhost:8000/api/collections?limit=1000')
collections = response.json()['collections']

# Convert to DataFrame
df = pd.DataFrame(collections)

# Parse dates
df['date'] = pd.to_datetime(df['collection_date']).dt.date

# Count by date and type
daily_counts = df.groupby(['date', 'content_type']).size().reset_index(name='count')

# Create time series plot
fig = px.line(
    daily_counts,
    x='date',
    y='count',
    color='content_type',
    title='Collection Activity Over Time',
    labels={'count': 'Number of Collections', 'date': 'Date', 'content_type': 'Type'}
)

fig.update_layout(
    xaxis_title='Date',
    yaxis_title='Collections',
    hovermode='x unified'
)

fig.write_html('timeline.html')
fig.show()

print("Timeline visualization saved to timeline.html")
```

### Heatmap of Collection Activity

```python
import requests
import plotly.express as px
import pandas as pd

# Fetch collections
response = requests.get('http://localhost:8000/api/collections?limit=1000')
collections = response.json()['collections']

# Convert to DataFrame
df = pd.DataFrame(collections)
df['datetime'] = pd.to_datetime(df['collection_date'])
df['date'] = df['datetime'].dt.date
df['weekday'] = df['datetime'].dt.day_name()
df['hour'] = df['datetime'].dt.hour

# Count by day of week and hour
heatmap_data = df.groupby(['weekday', 'hour']).size().reset_index(name='count')

# Pivot for heatmap
heatmap_pivot = heatmap_data.pivot(index='weekday', columns='hour', values='count').fillna(0)

# Order days of week
day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
heatmap_pivot = heatmap_pivot.reindex(day_order)

# Create heatmap
fig = px.imshow(
    heatmap_pivot,
    labels=dict(x='Hour of Day', y='Day of Week', color='Collections'),
    title='Collection Activity Heatmap',
    aspect='auto',
    color_continuous_scale='Blues'
)

fig.write_html('activity_heatmap.html')
fig.show()

print("Activity heatmap saved to activity_heatmap.html")
```

### Network Graph of Related Topics

```python
import requests
import networkx as nx
import plotly.graph_objects as go
from collections import Counter

# Fetch collections with metadata
response = requests.get('http://localhost:8000/api/collections?limit=500')
collections = response.json()['collections']

# Extract topics/categories from metadata
G = nx.Graph()

for item in collections:
    metadata = item.get('metadata', {})

    # Add categories if available
    if isinstance(metadata, dict):
        categories = metadata.get('categories', [])
        if categories:
            for i, cat1 in enumerate(categories):
                G.add_node(cat1)
                for cat2 in categories[i+1:]:
                    if G.has_edge(cat1, cat2):
                        G[cat1][cat2]['weight'] += 1
                    else:
                        G.add_edge(cat1, cat2, weight=1)

# Create positions
pos = nx.spring_layout(G, k=0.5, iterations=50)

# Create edges
edge_trace = []
for edge in G.edges():
    x0, y0 = pos[edge[0]]
    x1, y1 = pos[edge[1]]
    weight = G[edge[0]][edge[1]]['weight']

    edge_trace.append(
        go.Scatter(
            x=[x0, x1, None],
            y=[y0, y1, None],
            mode='lines',
            line=dict(width=weight*0.5, color='#888'),
            hoverinfo='none'
        )
    )

# Create nodes
node_x = []
node_y = []
node_text = []

for node in G.nodes():
    x, y = pos[node]
    node_x.append(x)
    node_y.append(y)
    node_text.append(f"{node}<br>Connections: {G.degree(node)}")

node_trace = go.Scatter(
    x=node_x,
    y=node_y,
    mode='markers+text',
    text=list(G.nodes()),
    textposition='top center',
    hovertext=node_text,
    marker=dict(
        size=[G.degree(n)*5 for n in G.nodes()],
        color=[G.degree(n) for n in G.nodes()],
        colorscale='Viridis',
        showscale=True,
        colorbar=dict(title='Connections')
    )
)

# Create figure
fig = go.Figure(data=edge_trace + [node_trace])
fig.update_layout(
    title='Topic Network Graph',
    showlegend=False,
    hovermode='closest',
    margin=dict(b=0, l=0, r=0, t=40),
    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
)

fig.write_html('topic_network.html')
fig.show()

print("Topic network graph saved to topic_network.html")
```

## Using the API

### API Endpoints

The FastAPI server provides several endpoints:

**Root:**
```
GET /
```
Returns available endpoints.

**Collections:**
```
GET /api/collections?content_type={type}&limit={n}&offset={n}
```
Get collections with optional filtering.

**Collection Details:**
```
GET /api/collections/{id}
```
Get detailed information about a specific collection.

**Statistics:**
```
GET /api/statistics
```
Get database statistics.

**Search:**
```
GET /api/search?q={query}&limit={n}
```
Search collections by title or source.

**Health Check:**
```
GET /health
```
Check if API is running.

### Python API Client

Create a reusable API client:

```python
import requests
from typing import Optional, List, Dict

class ResearchAPIClient:
    """Client for Research Data API"""

    def __init__(self, base_url='http://localhost:8000'):
        self.base_url = base_url

    def get_collections(
        self,
        content_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Dict:
        """Get collections with optional filtering"""
        params = {'limit': limit, 'offset': offset}
        if content_type:
            params['content_type'] = content_type

        response = requests.get(f'{self.base_url}/api/collections', params=params)
        response.raise_for_status()
        return response.json()

    def get_collection(self, collection_id: int) -> Dict:
        """Get specific collection"""
        response = requests.get(f'{self.base_url}/api/collections/{collection_id}')
        response.raise_for_status()
        return response.json()

    def get_statistics(self) -> Dict:
        """Get statistics"""
        response = requests.get(f'{self.base_url}/api/statistics')
        response.raise_for_status()
        return response.json()

    def search(self, query: str, limit: int = 50) -> Dict:
        """Search collections"""
        params = {'q': query, 'limit': limit}
        response = requests.get(f'{self.base_url}/api/search', params=params)
        response.raise_for_status()
        return response.json()

    def health_check(self) -> bool:
        """Check if API is healthy"""
        try:
            response = requests.get(f'{self.base_url}/health')
            return response.status_code == 200
        except:
            return False

# Usage
client = ResearchAPIClient()

# Check health
if not client.health_check():
    print("API is not running!")
    exit(1)

# Get statistics
stats = client.get_statistics()
print(f"Total collections: {stats['total_collections']}")

# Search
results = client.search('machine learning')
print(f"Found {results['count']} results")

# Get all papers
papers = client.get_collections(content_type='paper', limit=100)
print(f"Retrieved {len(papers['collections'])} papers")
```

## Advanced Features

### Real-Time Monitoring

Monitor collection activity in real-time:

```python
import requests
import time
from datetime import datetime

def monitor_collections(interval=10):
    """Monitor collection activity"""

    client = ResearchAPIClient()
    last_count = 0

    print("Monitoring collection activity (Ctrl+C to stop)...")
    print("="*60)

    try:
        while True:
            stats = client.get_statistics()
            current_count = stats['total_collections']

            if current_count != last_count:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                new_items = current_count - last_count

                print(f"[{timestamp}] New collections: {new_items}")
                print(f"  Total: {current_count}")
                print(f"  Papers: {stats['by_type'].get('paper', 0)}")
                print(f"  Videos: {stats['by_type'].get('video', 0)}")
                print(f"  Podcasts: {stats['by_type'].get('podcast', 0)}")
                print("-"*60)

                last_count = current_count

            time.sleep(interval)

    except KeyboardInterrupt:
        print("\nMonitoring stopped")

# Run monitor
monitor_collections(interval=30)
```

### Automated Report Generation

Generate regular reports:

```python
import requests
from datetime import datetime
import json

def generate_daily_report():
    """Generate daily collection report"""

    client = ResearchAPIClient()

    # Get statistics
    stats = client.get_statistics()

    # Get recent collections
    collections = client.get_collections(limit=1000)

    # Filter today's collections
    today = datetime.now().date().isoformat()
    today_collections = [
        c for c in collections['collections']
        if c['collection_date'].startswith(today)
    ]

    # Create report
    report = {
        'date': today,
        'generated_at': datetime.now().isoformat(),
        'overall_stats': stats,
        'today': {
            'total': len(today_collections),
            'by_type': {}
        },
        'recent_items': today_collections[:20]
    }

    # Count by type
    for item in today_collections:
        content_type = item['content_type']
        report['today']['by_type'][content_type] = \
            report['today']['by_type'].get(content_type, 0) + 1

    # Save report
    filename = f'daily_report_{today}.json'
    with open(filename, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"Daily report saved to {filename}")
    print(f"Collections today: {report['today']['total']}")

# Run daily report
generate_daily_report()
```

## Next Steps

- Learn about [Custom Searches](custom-searches.md) to query your data
- Explore [Exporting Citations](export-citations.md) for research writing
- Check [Extending the System](extending.md) to add custom visualizations
- Review [Collecting Papers](collect-papers.md) to expand your database
