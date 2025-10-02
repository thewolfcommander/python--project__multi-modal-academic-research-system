# UI Module

## Overview

The UI module provides a Gradio-based web interface for the Multi-Modal Research Assistant. It offers tabs for research queries, data collection, citation management, settings configuration, and data visualization.

## Module Architecture

```
multi_modal_rag/ui/
└── gradio_app.py    # Gradio application interface
```

---

## ResearchAssistantUI

**File**: `multi_modal_rag/ui/gradio_app.py`

### Class Overview

Creates a comprehensive Gradio interface with multiple tabs for different functionalities. Integrates with all system components including orchestrator, citation tracker, data collectors, and database manager.

### Initialization

```python
from multi_modal_rag.ui import ResearchAssistantUI

ui = ResearchAssistantUI(
    orchestrator=orchestrator,
    citation_tracker=citation_tracker,
    data_collectors=data_collectors,
    opensearch_manager=opensearch_manager,
    db_manager=db_manager
)
```

**Parameters**:
- `orchestrator` (ResearchOrchestrator): Query processing orchestrator
- `citation_tracker` (CitationTracker): Citation management system
- `data_collectors` (Dict): Dictionary of data collectors
  - `'paper_collector'`: AcademicPaperCollector
  - `'video_collector'`: YouTubeLectureCollector
  - `'podcast_collector'`: PodcastCollector
- `opensearch_manager` (OpenSearchManager, optional): OpenSearch client
- `db_manager` (CollectionDatabaseManager, optional): Database manager

**Example Setup**:

```python
from multi_modal_rag.orchestration import ResearchOrchestrator, CitationTracker
from multi_modal_rag.data_collectors import (
    AcademicPaperCollector,
    YouTubeLectureCollector,
    PodcastCollector
)
from multi_modal_rag.indexing import OpenSearchManager
from multi_modal_rag.database import CollectionDatabaseManager
from multi_modal_rag.ui import ResearchAssistantUI

# Initialize components
orchestrator = ResearchOrchestrator(gemini_api_key, opensearch)
citation_tracker = CitationTracker()
data_collectors = {
    'paper_collector': AcademicPaperCollector(),
    'video_collector': YouTubeLectureCollector(),
    'podcast_collector': PodcastCollector()
}
opensearch = OpenSearchManager()
db_manager = CollectionDatabaseManager()

# Create UI
ui = ResearchAssistantUI(
    orchestrator=orchestrator,
    citation_tracker=citation_tracker,
    data_collectors=data_collectors,
    opensearch_manager=opensearch,
    db_manager=db_manager
)

# Launch
app = ui.create_interface()
app.launch(share=True)
```

---

## Interface Structure

### Main Application

```python
def create_interface(self) -> gr.Blocks:
    """Creates Gradio interface with all tabs"""
```

**Returns**: Configured Gradio Blocks application

**Launch Options**:

```python
app = ui.create_interface()

# Local only
app.launch(server_name="127.0.0.1", server_port=7860)

# Public share link
app.launch(share=True)

# Custom settings
app.launch(
    server_name="0.0.0.0",
    server_port=7860,
    share=True,
    debug=True,
    auth=("username", "password")  # Basic auth
)
```

---

## Tabs Overview

### 1. Research Tab

**Purpose**: Query the research system and view results with citations.

**Components**:

```python
# Input
query_input = gr.Textbox(
    label="Research Query",
    placeholder="Enter your research question...",
    lines=2
)

search_filters = gr.CheckboxGroup(
    ["Papers", "Videos", "Podcasts"],
    value=["Papers", "Videos", "Podcasts"],
    label="Content Types"
)

search_btn = gr.Button("🔍 Search", variant="primary")
clear_btn = gr.Button("Clear")

# Output
answer_output = gr.Markdown(label="Answer")
citations_output = gr.JSON(label="Citations")
related_queries = gr.Markdown(label="Related Queries")
```

**Event Handler**:

```python
search_btn.click(
    fn=self.handle_search,
    inputs=[query_input, search_filters],
    outputs=[answer_output, citations_output, related_queries]
)
```

**Example Usage**:
1. Enter query: "How do transformers work?"
2. Select content types (papers, videos, podcasts)
3. Click "🔍 Search"
4. View formatted answer with citations
5. Explore related queries

---

### 2. Data Collection Tab

**Purpose**: Collect new content from various sources and index it.

**Components**:

```python
# Input
collection_type = gr.Radio(
    ["ArXiv Papers", "YouTube Lectures", "Podcasts"],
    label="Data Source"
)

collection_query = gr.Textbox(
    label="Search Query",
    placeholder="e.g., machine learning, quantum computing"
)

max_results = gr.Slider(
    minimum=5,
    maximum=100,
    value=20,
    step=5,
    label="Maximum Results"
)

collect_btn = gr.Button("📥 Collect Data", variant="primary")

# Output
collection_status = gr.Textbox(
    label="Collection Status",
    lines=10
)

collection_results = gr.JSON(label="Collection Results")
```

**Event Handler**:

```python
collect_btn.click(
    fn=self.handle_data_collection,
    inputs=[collection_type, collection_query, max_results],
    outputs=[collection_status, collection_results]
)
```

**Workflow**:
1. **Select Source**: Choose ArXiv Papers, YouTube Lectures, or Podcasts
2. **Enter Query**: Specify search terms
3. **Set Limit**: Choose max number of results (5-100)
4. **Collect**: Click "📥 Collect Data"
5. **Monitor**: Watch real-time status updates
6. **Auto-Index**: Data automatically indexed in OpenSearch
7. **Database Tracking**: Items tracked in SQLite database

**Status Updates Example**:

```
Collecting papers from ArXiv...
✅ Collected 20 papers

📊 Indexing data into OpenSearch...
✅ Indexed 20 items into OpenSearch

✅ Collection and indexing complete!
```

---

### 3. Citation Manager Tab

**Purpose**: View citation statistics and export bibliographies.

**Components**:

```python
# Report
citation_report = gr.JSON(label="Citation Report")
refresh_report_btn = gr.Button("🔄 Refresh Report")

# Export
export_format = gr.Radio(
    ["BibTeX", "APA", "JSON"],
    value="BibTeX",
    label="Export Format"
)

export_btn = gr.Button("📤 Export Citations")

exported_citations = gr.Textbox(
    label="Exported Citations",
    lines=15
)
```

**Event Handlers**:

```python
refresh_report_btn.click(
    fn=self.get_citation_report,
    outputs=citation_report
)

export_btn.click(
    fn=self.export_citations,
    inputs=export_format,
    outputs=exported_citations
)
```

**Citation Report Structure**:

```json
{
    "total_papers": 25,
    "total_videos": 12,
    "total_podcasts": 5,
    "most_cited": [
        {
            "id": "a1b2c3d4",
            "type": "papers",
            "title": "Attention Is All You Need",
            "use_count": 15
        },
        ...
    ],
    "recent_citations": [
        {
            "citation_id": "a1b2c3d4",
            "content_type": "paper",
            "query": "How do transformers work?",
            "timestamp": "2024-10-02T14:30:00"
        },
        ...
    ]
}
```

---

### 4. Settings Tab

**Purpose**: Configure OpenSearch connection and manage indices.

**Components**:

```python
# OpenSearch Settings
opensearch_host = gr.Textbox(
    label="Host",
    value="localhost"
)

opensearch_port = gr.Number(
    label="Port",
    value=9200
)

# API Keys
gemini_key = gr.Textbox(
    label="Gemini API Key",
    type="password",
    placeholder="Enter your Gemini API key"
)

save_settings_btn = gr.Button("💾 Save Settings")

# Index Management
index_name = gr.Textbox(
    label="Index Name",
    value="research_assistant"
)

create_index_btn = gr.Button("Create Index")
reindex_btn = gr.Button("Reindex All Data")

index_status = gr.Textbox(
    label="Status",
    lines=5
)
```

**Event Handlers**:

```python
reindex_btn.click(
    fn=self.handle_reindex,
    inputs=[index_name],
    outputs=[index_status]
)
```

**Reindex Functionality**:
- Reindexes all previously collected data
- Useful after OpenSearch restart or schema changes
- Shows progress and completion status

---

### 5. Data Visualization Tab

**Purpose**: View collection statistics and data tables.

**Components**:

```python
# Statistics
stats_display = gr.JSON(label="Statistics")
refresh_stats_btn = gr.Button("🔄 Refresh Statistics")
quick_stats = gr.Markdown("")

# Filters
content_type_filter = gr.Radio(
    ["All", "Papers", "Videos", "Podcasts"],
    value="All",
    label="Filter by Type"
)

limit_slider = gr.Slider(
    minimum=10,
    maximum=100,
    value=20,
    step=10,
    label="Number of Items"
)

refresh_collections_btn = gr.Button("📊 Load Collections")

# Data Table
collections_table = gr.Dataframe(
    headers=["ID", "Type", "Title", "Source", "Indexed", "Date"],
    label="Collection Data",
    wrap=True
)
```

**Event Handlers**:

```python
refresh_stats_btn.click(
    fn=self.get_database_statistics,
    outputs=[stats_display, quick_stats]
)

refresh_collections_btn.click(
    fn=self.get_collection_data,
    inputs=[content_type_filter, limit_slider],
    outputs=collections_table
)
```

**Quick Stats Display**:

```markdown
### Overview
- **Total Collections**: 255
- **Indexed**: 200 (78.4%)
- **Recent (7 days)**: 45

### By Type
- **Papers**: 150
- **Videos**: 75
- **Podcasts**: 30
```

**External Dashboard Link**:

```markdown
For advanced visualization with charts and filtering, visit the FastAPI dashboard:

**[Open Visualization Dashboard](http://localhost:8000/viz)**

To start the FastAPI server, run:
```bash
python -m uvicorn multi_modal_rag.api.api_server:app --host 0.0.0.0 --port 8000
```
```

---

## Event Handler Methods

### `handle_search(query: str, content_types: List[str]) -> Tuple`

Handles research query processing.

**Parameters**:
- `query` (str): User's research question
- `content_types` (List[str]): Selected content types (not currently used for filtering)

**Returns**: Tuple of (answer_markdown, citations_json, related_queries_markdown)

**Implementation**:

```python
def handle_search(self, query: str, content_types: List[str]) -> Tuple:
    # Process query
    result = self.orchestrator.process_query(query, "research_assistant")

    # Format answer with markdown
    answer_md = f"""
    ## Answer

    {result['answer']}

    ---

    **Sources Used:** {len(result['source_documents'])}
    """

    # Format related queries
    related_md = "### Related Research Questions\n\n"
    for i, q in enumerate(result['related_queries'], 1):
        related_md += f"{i}. {q}\n"

    return answer_md, result['citations'], related_md
```

---

### `handle_data_collection(source_type: str, query: str, max_results: int) -> Tuple`

Handles data collection and automatic indexing.

**Parameters**:
- `source_type` (str): "ArXiv Papers", "YouTube Lectures", or "Podcasts"
- `query` (str): Search query
- `max_results` (int): Maximum items to collect

**Returns**: Tuple of (status_updates_text, results_json)

**Workflow**:

1. **Collection**: Collect from selected source
2. **Database Tracking**: Save to SQLite database
3. **Indexing**: Index in OpenSearch
4. **Mark Indexed**: Update database status
5. **Log Statistics**: Record collection stats

**Example Status Output**:

```
Collecting papers from ArXiv...
✅ Collected 20 papers

📊 Indexing data into OpenSearch...
✅ Indexed 20 items into OpenSearch

✅ Collection and indexing complete!
```

**Results JSON**:

```json
{
    "papers_collected": 20,
    "items_indexed": 20
}
```

---

### `_index_data(items: List, source_type: str) -> int`

Helper method to index collected data into OpenSearch.

**Parameters**:
- `items` (List): Collected items (papers, videos, or podcasts)
- `source_type` (str): Type identifier

**Returns**: Number of items successfully indexed

**Document Formatting**:
- Converts collector output to OpenSearch document format
- Handles different content types appropriately
- Uses `_format_document()` helper

---

### `_format_document(item: dict, source_type: str) -> dict`

Formats collected item into OpenSearch document.

**Parameters**:
- `item` (dict): Raw collector output
- `source_type` (str): "YouTube Lectures", "ArXiv Papers", or "Podcasts"

**Returns**: OpenSearch-compatible document

**Paper Format**:

```python
{
    'content_type': 'paper',
    'title': item.get('title', 'Unknown'),
    'abstract': item.get('abstract', ''),
    'content': item.get('content', ''),
    'authors': item.get('authors', []),
    'url': item.get('url', ''),
    'publication_date': item.get('published', None),
    'metadata': {
        'arxiv_id': item.get('id', ''),
        'categories': item.get('categories', [])
    }
}
```

**Video Format**:

```python
{
    'content_type': 'video',
    'title': item.get('title', 'Unknown'),
    'content': item.get('description', ''),
    'transcript': item.get('transcript', ''),
    'authors': [item.get('author', 'Unknown')],
    'url': item.get('url', ''),
    'publication_date': item.get('publish_date', None),
    'metadata': {
        'video_id': item.get('video_id', ''),
        'length': item.get('length', 0),
        'views': item.get('views', 0),
        'thumbnail_url': item.get('thumbnail_url', '')
    }
}
```

---

### `handle_reindex(index_name: str) -> str`

Reindexes all previously collected data.

**Parameters**:
- `index_name` (str): Target index name

**Returns**: Status message

**Example**:

```python
# Reindex all data
status = ui.handle_reindex("research_assistant")
print(status)
# "✅ Successfully reindexed 200 items to 'research_assistant'"
```

---

### `get_citation_report() -> Dict`

Retrieves citation usage report.

**Returns**: Citation tracker report dictionary

---

### `export_citations(format: str) -> str`

Exports citations in specified format.

**Parameters**:
- `format` (str): "BibTeX", "APA", or "JSON"

**Returns**: Formatted bibliography string

---

### `get_database_statistics() -> Tuple`

Retrieves database statistics for visualization.

**Returns**: Tuple of (stats_json, quick_stats_markdown)

**Stats JSON**:

```json
{
    "by_type": {
        "paper": 150,
        "video": 75,
        "podcast": 30
    },
    "indexed": 200,
    "not_indexed": 55,
    "recent_7_days": 45,
    "collection_history": [...]
}
```

---

### `get_collection_data(content_type_filter: str, limit: int) -> List`

Retrieves collection data for table display.

**Parameters**:
- `content_type_filter` (str): "All", "Papers", "Videos", or "Podcasts"
- `limit` (int): Maximum rows

**Returns**: List of lists for Gradio Dataframe

**Example Output**:

```python
[
    [1, "paper", "Attention Is All You Need", "arxiv", "Yes", "2024-10-02"],
    [2, "video", "Neural Networks Explained", "youtube", "Yes", "2024-10-02"],
    ...
]
```

---

## UI Customization

### Theme Customization

```python
import gradio as gr

app = gr.Blocks(
    title="Multi-Modal Research Assistant",
    theme=gr.themes.Soft()  # or Base(), Monochrome(), Glass()
)
```

**Available Themes**:
- `gr.themes.Base()`: Default theme
- `gr.themes.Soft()`: Softer colors
- `gr.themes.Monochrome()`: Black and white
- `gr.themes.Glass()`: Glassmorphism effect

**Custom Theme**:

```python
theme = gr.themes.Base(
    primary_hue="blue",
    secondary_hue="gray",
    neutral_hue="slate",
    font=("Helvetica", "sans-serif")
)

app = gr.Blocks(theme=theme)
```

---

### Adding Custom Tabs

```python
def create_interface(self):
    with gr.Blocks() as app:
        # ... existing tabs ...

        # Custom tab
        with gr.TabItem("Analytics"):
            with gr.Row():
                date_range = gr.DateTimePicker(label="Start Date")
                plot_btn = gr.Button("Generate Plot")

            plot_output = gr.Plot(label="Analytics")

            plot_btn.click(
                fn=self.generate_analytics_plot,
                inputs=[date_range],
                outputs=[plot_output]
            )

    return app

def generate_analytics_plot(self, start_date):
    import matplotlib.pyplot as plt
    import pandas as pd

    # Generate plot
    fig, ax = plt.subplots()
    # ... plotting logic ...
    return fig
```

---

## Launch Configurations

### Local Development

```python
app.launch(
    server_name="127.0.0.1",
    server_port=7860,
    debug=True,
    show_error=True
)
```

### Public Deployment

```python
app.launch(
    server_name="0.0.0.0",
    server_port=7860,
    share=True,  # Creates public link
    auth=("admin", "password"),  # Basic authentication
    ssl_keyfile="key.pem",
    ssl_certfile="cert.pem"
)
```

### Production Deployment

```python
import os

app.launch(
    server_name="0.0.0.0",
    server_port=int(os.getenv("PORT", 7860)),
    share=False,
    auth=(os.getenv("USERNAME"), os.getenv("PASSWORD")),
    show_api=False,  # Hide API docs
    favicon_path="favicon.ico"
)
```

---

## Integration with Main Application

**File**: `main.py`

```python
from multi_modal_rag.orchestration import ResearchOrchestrator, CitationTracker
from multi_modal_rag.data_collectors import (
    AcademicPaperCollector,
    YouTubeLectureCollector,
    PodcastCollector
)
from multi_modal_rag.indexing import OpenSearchManager
from multi_modal_rag.database import CollectionDatabaseManager
from multi_modal_rag.ui import ResearchAssistantUI

def main():
    # Load config
    gemini_api_key = os.getenv("GEMINI_API_KEY")

    # Initialize components
    opensearch = OpenSearchManager()
    orchestrator = ResearchOrchestrator(gemini_api_key, opensearch)
    citation_tracker = CitationTracker()

    data_collectors = {
        'paper_collector': AcademicPaperCollector(),
        'video_collector': YouTubeLectureCollector(),
        'podcast_collector': PodcastCollector()
    }

    db_manager = CollectionDatabaseManager()

    # Create and launch UI
    ui = ResearchAssistantUI(
        orchestrator=orchestrator,
        citation_tracker=citation_tracker,
        data_collectors=data_collectors,
        opensearch_manager=opensearch,
        db_manager=db_manager
    )

    app = ui.create_interface()
    app.launch(share=True)

if __name__ == "__main__":
    main()
```

---

## User Workflows

### Workflow 1: Research Query

1. Navigate to **Research** tab
2. Enter query: "Explain attention mechanisms in transformers"
3. Select content types (Papers, Videos, Podcasts)
4. Click "🔍 Search"
5. Read formatted answer with citations
6. Click related queries for deeper exploration
7. View citations in **Citation Manager**

### Workflow 2: Collect New Content

1. Navigate to **Data Collection** tab
2. Select source: "ArXiv Papers"
3. Enter query: "quantum machine learning"
4. Set max results: 20
5. Click "📥 Collect Data"
6. Monitor real-time status
7. Data automatically indexed and ready for queries

### Workflow 3: Export Bibliography

1. Navigate to **Citation Manager** tab
2. Click "🔄 Refresh Report" to update
3. Review most cited sources
4. Select export format: "BibTeX"
5. Click "📤 Export Citations"
6. Copy exported text
7. Paste into LaTeX document or reference manager

### Workflow 4: View Analytics

1. Navigate to **Data Visualization** tab
2. Click "🔄 Refresh Statistics"
3. Review quick stats (total collections, indexed percentage)
4. Select filter: "Papers"
5. Adjust limit: 50
6. Click "📊 Load Collections"
7. Browse table of collected papers
8. Open external dashboard for advanced charts

---

## Error Handling in UI

### Collection Errors

```python
def handle_data_collection(self, ...):
    try:
        # ... collection logic ...
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        status_updates.append(error_msg)
        logger.error(f"Collection error: {e}", exc_info=True)

    return '\n'.join(status_updates), results
```

**Displayed Error**:
```
Collecting papers from ArXiv...
❌ Error: Network connection timeout
```

### Search Errors

```python
def handle_search(self, query, content_types):
    try:
        result = self.orchestrator.process_query(query, "research_assistant")
    except Exception as e:
        return (
            f"## Error\n\n{str(e)}",
            [],
            "No related queries available"
        )
```

---

## Performance Considerations

### UI Response Times

- **Search**: 4-8 seconds (Gemini generation)
- **Data Collection**: 1-5 minutes (depending on count)
- **Statistics**: 50-200ms
- **Export**: 10-50ms

### Optimization Tips

1. **Show Loading States**:
   ```python
   with gr.Column():
       search_btn = gr.Button("🔍 Search")
       loading = gr.HTML("", visible=False)

   def search_with_loading(query):
       # Show loading
       yield "Searching...", [], "", "<p>Loading...</p>"

       # Process
       result = orchestrator.process_query(query, index)

       # Hide loading
       yield answer, citations, related, ""

   search_btn.click(
       fn=search_with_loading,
       inputs=[query_input],
       outputs=[answer, citations, related, loading]
   )
   ```

2. **Limit Result Display**:
   ```python
   # Don't display huge JSON objects
   citations_output = gr.JSON(label="Citations", max_height=400)
   ```

3. **Async Operations**:
   ```python
   async def handle_search_async(query):
       result = await async_process_query(query)
       return result
   ```

---

## Dependencies

```python
import gradio as gr
from typing import List, Tuple
```

**Installation**:
```bash
pip install gradio
```

---

## Troubleshooting

### Issue: Gradio app won't launch

**Error**: `Address already in use`

**Solution**:
```python
app.launch(server_port=7861)  # Use different port
```

### Issue: Share link doesn't work

**Cause**: Firewall or network restrictions

**Solution**:
- Check firewall settings
- Try local access first
- Use ngrok as alternative:
  ```bash
  ngrok http 7860
  ```

### Issue: UI freezes during collection

**Cause**: Long-running operation blocks UI

**Solution**: Already implemented with status updates, but consider:
```python
# Use queue for real-time updates
app.queue()
app.launch()
```

### Issue: Large JSON crashes browser

**Cause**: Too much data in JSON component

**Solution**:
```python
# Limit JSON display
limited_citations = citations[:10]  # Show first 10 only
return answer, limited_citations, related
```

---

## Accessibility Features

### Keyboard Navigation

Gradio automatically supports:
- Tab navigation between fields
- Enter to submit forms
- Arrow keys for sliders

### Screen Reader Support

Use descriptive labels:
```python
query_input = gr.Textbox(
    label="Research Query",
    placeholder="Enter your research question...",
    info="Ask about papers, videos, or podcasts"  # Additional help text
)
```

### Dark Mode

```python
app = gr.Blocks(theme=gr.themes.Soft(variant="dark"))
```

---

## Future Enhancements

### Planned Features

1. **Advanced Filters**: Filter search by date, author, source
2. **Saved Queries**: Save and reuse frequent queries
3. **Export Options**: Export results as PDF, Markdown
4. **Collaboration**: Share query results with team
5. **Visualization**: Charts showing citation networks
6. **Voice Input**: Speech-to-text for queries
7. **Multi-language**: Support for non-English content

### Extension Points

```python
# Add advanced search filters
def create_advanced_search_tab(self):
    with gr.TabItem("Advanced Search"):
        # Date range
        date_from = gr.DateTime(label="From")
        date_to = gr.DateTime(label="To")

        # Author filter
        author_filter = gr.Textbox(label="Author")

        # Advanced search
        advanced_search_btn = gr.Button("Advanced Search")

# Add export options
def export_results(self, format: str):
    if format == "PDF":
        return self.generate_pdf_report()
    elif format == "Markdown":
        return self.generate_markdown_report()
```
