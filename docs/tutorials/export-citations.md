# Tutorial: Exporting Citations

This tutorial shows you how to export citations from the Multi-Modal Academic Research System in various formats. You'll learn how to use the UI, programmatic export via Python, integrate with reference managers, and create custom citation formats.

## Table of Contents

1. [Understanding Citation Tracking](#understanding-citation-tracking)
2. [Exporting from the UI](#exporting-from-the-ui)
3. [Programmatic Export via Python](#programmatic-export-via-python)
4. [Citation Formats](#citation-formats)
5. [Integrating with Reference Managers](#integrating-with-reference-managers)
6. [Custom Citation Formats](#custom-citation-formats)
7. [Advanced Usage](#advanced-usage)

## Understanding Citation Tracking

### How Citations are Tracked

The system automatically tracks citations when you:

1. **Perform a research query** - The orchestrator identifies sources used in responses
2. **View search results** - Sources are logged with usage statistics
3. **Generate answers** - Citations are extracted and stored

### Citation Storage

Citations are stored in:
- **Location:** `data/citations.json`
- **Database:** SQLite database for additional tracking
- **Format:** JSON with metadata and usage history

### Citation Data Structure

```json
{
  "papers": {
    "abc123def456": {
      "title": "Attention is All You Need",
      "authors": ["Vaswani", "Shazeer", "Parmar"],
      "url": "https://arxiv.org/abs/1706.03762",
      "first_used": "2024-01-15T10:30:00",
      "use_count": 5,
      "queries": [
        {
          "query": "transformer architecture",
          "timestamp": "2024-01-15T10:30:00"
        }
      ]
    }
  },
  "videos": {},
  "podcasts": {},
  "usage_history": []
}
```

## Exporting from the UI

### Step 1: Access Citation Manager

1. Start the application:
   ```bash
   python main.py
   ```

2. Open the web interface at `http://localhost:7860`

3. Click on the **"Citation Manager"** tab

### Step 2: View Citation Report

1. Click **"Refresh Report"** to see your citation statistics

2. Review the report showing:
   - Total papers, videos, and podcasts cited
   - Most frequently cited sources
   - Recent citations

Example report:
```json
{
  "total_papers": 25,
  "total_videos": 8,
  "total_podcasts": 3,
  "most_cited": [
    {
      "id": "abc123",
      "type": "papers",
      "title": "Attention is All You Need",
      "use_count": 12
    }
  ],
  "recent_citations": [...]
}
```

### Step 3: Choose Export Format

Select from available formats:
- **BibTeX** - For LaTeX documents
- **APA** - For Word documents and general use
- **JSON** - For programmatic use or custom processing

### Step 4: Export Citations

1. Select your desired format using the radio buttons
2. Click **"Export Citations"**
3. Copy the output from the text box

**BibTeX Output Example:**
```bibtex
@article{abc123def456,
    title={Attention is All You Need},
    author={Vaswani and Shazeer and Parmar},
    year={2024},
    url={https://arxiv.org/abs/1706.03762}
}
```

**APA Output Example:**
```
Vaswani et al. (2024). Attention is All You Need. Retrieved from https://arxiv.org/abs/1706.03762
```

### Step 5: Use Exported Citations

**For LaTeX:**
1. Copy BibTeX output
2. Paste into your `.bib` file
3. Reference with `\cite{citation_id}`

**For Word:**
1. Copy APA output
2. Paste into your document's references section
3. Use Word's citation manager to link references

**For Custom Processing:**
1. Export as JSON
2. Process with your own scripts or tools

## Programmatic Export via Python

### Basic Export Script

Create a Python script to export citations:

```python
from multi_modal_rag.orchestration.citation_tracker import CitationTracker

# Initialize citation tracker
tracker = CitationTracker()

# Export in different formats
bibtex = tracker.export_bibliography('bibtex')
apa = tracker.export_bibliography('apa')
json_data = tracker.export_bibliography('json')

# Save to files
with open('references.bib', 'w') as f:
    f.write(bibtex)

with open('references_apa.txt', 'w') as f:
    f.write(apa)

with open('citations.json', 'w') as f:
    f.write(json_data)

print("Citations exported successfully!")
```

### Export Specific Citation Types

Export only papers, videos, or podcasts:

```python
from multi_modal_rag.orchestration.citation_tracker import CitationTracker
import json

tracker = CitationTracker()

# Export only papers
papers_only = {
    'papers': tracker.citations['papers'],
    'total': len(tracker.citations['papers'])
}

with open('papers_only.json', 'w') as f:
    json.dump(papers_only, f, indent=2)

# Export only videos
videos_only = {
    'videos': tracker.citations['videos'],
    'total': len(tracker.citations['videos'])
}

with open('videos_only.json', 'w') as f:
    json.dump(videos_only, f, indent=2)
```

### Export Most Cited Sources

```python
from multi_modal_rag.orchestration.citation_tracker import CitationTracker

tracker = CitationTracker()

# Get top 10 most cited sources
most_cited = tracker.get_most_cited(10)

# Create BibTeX for top sources only
bibtex_entries = []

for citation in most_cited:
    citation_type = citation['type']
    citation_id = citation['id']

    # Get full citation data
    if citation_type in tracker.citations:
        full_data = tracker.citations[citation_type].get(citation_id)

        if full_data:
            entry = f"""@article{{{citation_id},
    title={{{full_data['title']}}},
    author={{{' and '.join(full_data.get('authors', ['Unknown']))}}},
    year={{{full_data.get('first_used', '')[:4]}}},
    url={{{full_data.get('url', '')}}},
    note={{Cited {citation['use_count']} times}}
}}"""
            bibtex_entries.append(entry)

# Save top citations
with open('top_citations.bib', 'w') as f:
    f.write('\n\n'.join(bibtex_entries))

print(f"Exported {len(bibtex_entries)} top citations")
```

### Export by Date Range

```python
from multi_modal_rag.orchestration.citation_tracker import CitationTracker
from datetime import datetime, timedelta

tracker = CitationTracker()

# Get citations from last 30 days
thirty_days_ago = datetime.now() - timedelta(days=30)

recent_citations = []

for entry in tracker.citations['usage_history']:
    timestamp = datetime.fromisoformat(entry['timestamp'])

    if timestamp >= thirty_days_ago:
        citation_id = entry['citation_id']
        content_type = entry['content_type']

        # Get full citation
        citation_data = tracker.citations[f'{content_type}s'].get(citation_id)
        if citation_data:
            recent_citations.append({
                'id': citation_id,
                'type': content_type,
                'data': citation_data,
                'query': entry['query'],
                'timestamp': entry['timestamp']
            })

# Export recent citations
import json
with open('recent_citations.json', 'w') as f:
    json.dump(recent_citations, f, indent=2)

print(f"Exported {len(recent_citations)} recent citations")
```

## Citation Formats

### BibTeX Format

Used primarily with LaTeX documents.

**Standard Entry:**
```bibtex
@article{unique_id,
    title={Paper Title},
    author={Author1 and Author2 and Author3},
    year={2024},
    url={https://example.com/paper.pdf}
}
```

**Entry Types:**
- `@article` - Journal articles
- `@inproceedings` - Conference papers
- `@misc` - Videos, podcasts, other media

**Enhanced BibTeX Export:**

```python
def export_enhanced_bibtex(tracker):
    """Export BibTeX with more fields"""
    bibtex = []

    for cid, paper in tracker.citations['papers'].items():
        # Determine entry type based on metadata
        entry_type = 'article'
        if 'conference' in str(paper.get('metadata', {})).lower():
            entry_type = 'inproceedings'

        entry = f"""@{entry_type}{{{cid},
    title={{{paper['title']}}},
    author={{{' and '.join(paper.get('authors', ['Unknown']))}}},
    year={{{paper.get('first_used', '')[:4]}}},
    url={{{paper.get('url', '')}}},
    abstract={{{paper.get('abstract', 'N/A')}}},
    keywords={{{', '.join(paper.get('key_concepts', []))}}},
    note={{Used {paper['use_count']} times in research}}
}}"""
        bibtex.append(entry)

    return '\n\n'.join(bibtex)
```

### APA Format

Used in academic writing, especially social sciences.

**Standard Format:**
```
Author, A. A., Author, B. B., & Author, C. C. (Year). Title of article. Retrieved from URL
```

**Enhanced APA Export:**

```python
def export_enhanced_apa(tracker):
    """Export APA format with proper formatting"""
    apa = []

    for paper in tracker.citations['papers'].values():
        authors = paper.get('authors', ['Unknown'])
        year = paper.get('first_used', '')[:4] or 'n.d.'

        # Format authors (APA style)
        if len(authors) == 1:
            author_str = authors[0]
        elif len(authors) == 2:
            author_str = f"{authors[0]} & {authors[1]}"
        elif len(authors) > 2:
            author_str = f"{authors[0]} et al."
        else:
            author_str = "Unknown"

        # Get journal/conference if available
        venue = paper.get('metadata', {}).get('venue', '')
        venue_str = f" {venue}." if venue else ""

        citation = f"{author_str} ({year}). {paper['title']}.{venue_str} Retrieved from {paper.get('url', 'N/A')}"
        apa.append(citation)

    return '\n\n'.join(sorted(apa))

# Usage
tracker = CitationTracker()
apa_text = export_enhanced_apa(tracker)
print(apa_text)
```

### MLA Format

Modern Language Association format.

**Standard Format:**
```
Author(s). "Title." Website/Source, Date, URL.
```

**MLA Export Implementation:**

```python
def export_mla(tracker):
    """Export citations in MLA format"""
    mla = []

    for paper in tracker.citations['papers'].values():
        authors = paper.get('authors', ['Unknown'])

        # Format authors (MLA style)
        if len(authors) == 1:
            author_str = f"{authors[0]}."
        elif len(authors) == 2:
            author_str = f"{authors[0]} and {authors[1]}."
        elif len(authors) > 2:
            author_str = f"{authors[0]}, et al."
        else:
            author_str = "Unknown."

        # Format date
        date_str = paper.get('first_used', '')[:10]  # YYYY-MM-DD

        citation = f'{author_str} "{paper["title"]}." ArXiv, {date_str}, {paper.get("url", "N/A")}.'
        mla.append(citation)

    return '\n\n'.join(sorted(mla))

# Add to CitationTracker class
from multi_modal_rag.orchestration.citation_tracker import CitationTracker

tracker = CitationTracker()
mla_text = export_mla(tracker)

with open('references_mla.txt', 'w') as f:
    f.write(mla_text)
```

### Chicago Format

Chicago Manual of Style format.

```python
def export_chicago(tracker):
    """Export citations in Chicago format"""
    chicago = []

    for paper in tracker.citations['papers'].values():
        authors = paper.get('authors', ['Unknown'])

        # Format authors (Chicago style)
        if len(authors) == 1:
            author_str = f"{authors[0]}"
        elif len(authors) > 1:
            author_str = f"{authors[0]} et al."
        else:
            author_str = "Unknown"

        year = paper.get('first_used', '')[:4] or 'n.d.'

        citation = f'{author_str}. {year}. "{paper["title"]}." Accessed {paper.get("first_used", "")[:10]}. {paper.get("url", "N/A")}.'
        chicago.append(citation)

    return '\n\n'.join(sorted(chicago))
```

## Integrating with Reference Managers

### Zotero Integration

Export to Zotero-compatible format:

```python
import json

def export_for_zotero(tracker):
    """Export in Zotero-compatible JSON format"""
    zotero_items = []

    for cid, paper in tracker.citations['papers'].items():
        item = {
            "itemType": "journalArticle",
            "title": paper['title'],
            "creators": [
                {"creatorType": "author", "name": author}
                for author in paper.get('authors', [])
            ],
            "abstractNote": paper.get('abstract', ''),
            "url": paper.get('url', ''),
            "accessDate": paper.get('first_used', ''),
            "tags": [
                {"tag": concept}
                for concept in paper.get('key_concepts', [])
            ],
            "notes": [
                {"note": f"Used {paper['use_count']} times in research"}
            ]
        }
        zotero_items.append(item)

    with open('zotero_import.json', 'w') as f:
        json.dump(zotero_items, f, indent=2)

    return len(zotero_items)

# Usage
tracker = CitationTracker()
count = export_for_zotero(tracker)
print(f"Exported {count} items for Zotero")
```

**Import to Zotero:**
1. Open Zotero
2. Go to File > Import
3. Select `zotero_import.json`
4. Citations are added to your library

### Mendeley Integration

Export for Mendeley:

```python
def export_for_mendeley(tracker):
    """Export BibTeX for Mendeley import"""
    # Mendeley uses BibTeX format
    bibtex = tracker.export_bibliography('bibtex')

    with open('mendeley_import.bib', 'w') as f:
        f.write(bibtex)

    return "mendeley_import.bib"

# Usage
tracker = CitationTracker()
filename = export_for_mendeley(tracker)
print(f"Import {filename} into Mendeley")
```

**Import to Mendeley:**
1. Open Mendeley Desktop
2. Go to File > Import > BibTeX
3. Select `mendeley_import.bib`

### EndNote Integration

```python
def export_for_endnote(tracker):
    """Export in EndNote format (RIS)"""
    ris_entries = []

    for paper in tracker.citations['papers'].values():
        entry = f"""TY  - JOUR
TI  - {paper['title']}
{"".join([f"AU  - {author}\n" for author in paper.get('authors', [])])}PY  - {paper.get('first_used', '')[:4]}
UR  - {paper.get('url', '')}
AB  - {paper.get('abstract', '')}
ER  -
"""
        ris_entries.append(entry)

    with open('endnote_import.ris', 'w') as f:
        f.write('\n'.join(ris_entries))

    return len(ris_entries)

# Usage
tracker = CitationTracker()
count = export_for_endnote(tracker)
print(f"Exported {count} citations for EndNote")
```

## Custom Citation Formats

### Creating Custom Formats

Add custom export methods to the CitationTracker:

```python
from multi_modal_rag.orchestration.citation_tracker import CitationTracker

class CustomCitationTracker(CitationTracker):
    """Extended citation tracker with custom formats"""

    def export_markdown(self) -> str:
        """Export citations as markdown list"""
        md = "# Research Citations\n\n"

        # Papers section
        if self.citations['papers']:
            md += "## Papers\n\n"
            for cid, paper in sorted(
                self.citations['papers'].items(),
                key=lambda x: x[1]['use_count'],
                reverse=True
            ):
                authors = ', '.join(paper.get('authors', ['Unknown'])[:3])
                if len(paper.get('authors', [])) > 3:
                    authors += " et al."

                md += f"- **{paper['title']}**\n"
                md += f"  - Authors: {authors}\n"
                md += f"  - URL: [{paper.get('url', 'N/A')}]({paper.get('url', '#')})\n"
                md += f"  - Used {paper['use_count']} times\n\n"

        # Videos section
        if self.citations['videos']:
            md += "## Videos\n\n"
            for cid, video in self.citations['videos'].items():
                md += f"- **{video['title']}**\n"
                md += f"  - Creator: {', '.join(video.get('authors', ['Unknown']))}\n"
                md += f"  - URL: [{video.get('url', 'N/A')}]({video.get('url', '#')})\n\n"

        # Podcasts section
        if self.citations['podcasts']:
            md += "## Podcasts\n\n"
            for cid, podcast in self.citations['podcasts'].items():
                md += f"- **{podcast['title']}**\n"
                md += f"  - Host: {', '.join(podcast.get('authors', ['Unknown']))}\n"
                md += f"  - URL: [{podcast.get('url', 'N/A')}]({podcast.get('url', '#')})\n\n"

        return md

    def export_html(self) -> str:
        """Export citations as HTML"""
        html = """<!DOCTYPE html>
<html>
<head>
    <title>Research Citations</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; }
        h1 { color: #333; }
        .citation { margin-bottom: 20px; padding: 10px; border-left: 3px solid #007bff; }
        .title { font-weight: bold; font-size: 1.1em; }
        .meta { color: #666; font-size: 0.9em; }
    </style>
</head>
<body>
    <h1>Research Citations</h1>
"""

        for cid, paper in self.citations['papers'].items():
            authors = ', '.join(paper.get('authors', ['Unknown'])[:3])
            html += f"""
    <div class="citation">
        <div class="title">{paper['title']}</div>
        <div class="meta">
            Authors: {authors}<br>
            URL: <a href="{paper.get('url', '#')}">{paper.get('url', 'N/A')}</a><br>
            Used {paper['use_count']} times
        </div>
    </div>
"""

        html += """
</body>
</html>
"""
        return html

    def export_csv(self) -> str:
        """Export citations as CSV"""
        import csv
        from io import StringIO

        output = StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow(['Type', 'Title', 'Authors', 'URL', 'Use Count', 'First Used'])

        # Papers
        for paper in self.citations['papers'].values():
            writer.writerow([
                'Paper',
                paper['title'],
                '; '.join(paper.get('authors', [])),
                paper.get('url', ''),
                paper['use_count'],
                paper.get('first_used', '')
            ])

        # Videos
        for video in self.citations['videos'].values():
            writer.writerow([
                'Video',
                video['title'],
                '; '.join(video.get('authors', [])),
                video.get('url', ''),
                video['use_count'],
                video.get('first_used', '')
            ])

        return output.getvalue()

# Usage
tracker = CustomCitationTracker()

# Export as markdown
md = tracker.export_markdown()
with open('citations.md', 'w') as f:
    f.write(md)

# Export as HTML
html = tracker.export_html()
with open('citations.html', 'w') as f:
    f.write(html)

# Export as CSV
csv_data = tracker.export_csv()
with open('citations.csv', 'w') as f:
    f.write(csv_data)

print("Exported citations in markdown, HTML, and CSV formats")
```

## Advanced Usage

### Filtered Export

Export only certain citations based on criteria:

```python
from multi_modal_rag.orchestration.citation_tracker import CitationTracker

def export_filtered_citations(tracker, min_use_count=2, content_types=['papers']):
    """Export only frequently used citations"""
    filtered = {
        'papers': {},
        'videos': {},
        'podcasts': {}
    }

    for content_type in content_types:
        type_key = f'{content_type}' if content_type.endswith('s') else f'{content_type}s'

        for cid, citation in tracker.citations[type_key].items():
            if citation['use_count'] >= min_use_count:
                filtered[type_key][cid] = citation

    # Export to BibTeX
    bibtex = []
    for cid, paper in filtered['papers'].items():
        entry = f"""@article{{{cid},
    title={{{paper['title']}}},
    author={{{' and '.join(paper.get('authors', ['Unknown']))}}},
    year={{{paper.get('first_used', '')[:4]}}},
    url={{{paper.get('url', '')}}}
}}"""
        bibtex.append(entry)

    return '\n\n'.join(bibtex)

# Usage
tracker = CitationTracker()
frequently_cited = export_filtered_citations(tracker, min_use_count=3)

with open('frequently_cited.bib', 'w') as f:
    f.write(frequently_cited)
```

### Automated Export Workflow

Create a script that automatically exports citations after each research session:

```python
import os
from datetime import datetime
from multi_modal_rag.orchestration.citation_tracker import CitationTracker

def auto_export_citations():
    """Automatically export citations in multiple formats"""

    tracker = CitationTracker()

    # Create exports directory
    export_dir = 'exports/citations'
    os.makedirs(export_dir, exist_ok=True)

    # Timestamp for versioning
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Export in all formats
    formats = {
        'bibtex': tracker.export_bibliography('bibtex'),
        'apa': tracker.export_bibliography('apa'),
        'json': tracker.export_bibliography('json')
    }

    exported_files = []

    for format_name, content in formats.items():
        filename = f'{export_dir}/citations_{timestamp}.{format_name}'
        if format_name == 'json':
            filename = f'{export_dir}/citations_{timestamp}.json'
        elif format_name == 'bibtex':
            filename = f'{export_dir}/citations_{timestamp}.bib'
        else:
            filename = f'{export_dir}/citations_{timestamp}.txt'

        with open(filename, 'w') as f:
            f.write(content)

        exported_files.append(filename)

    # Also create a latest version (overwrite)
    for format_name, content in formats.items():
        latest_filename = f'{export_dir}/citations_latest.{format_name if format_name == "json" else "bib" if format_name == "bibtex" else "txt"}'
        with open(latest_filename, 'w') as f:
            f.write(content)

        exported_files.append(latest_filename)

    print(f"Exported {len(formats)} citation formats:")
    for file in exported_files:
        print(f"  - {file}")

    return exported_files

# Run automatic export
if __name__ == '__main__':
    auto_export_citations()
```

### Citation Report Generation

Generate detailed citation reports:

```python
from multi_modal_rag.orchestration.citation_tracker import CitationTracker
from datetime import datetime

def generate_citation_report(tracker):
    """Generate comprehensive citation report"""

    report = []
    report.append("="*60)
    report.append("CITATION USAGE REPORT")
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("="*60)

    # Summary statistics
    total_papers = len(tracker.citations['papers'])
    total_videos = len(tracker.citations['videos'])
    total_podcasts = len(tracker.citations['podcasts'])
    total_citations = total_papers + total_videos + total_podcasts

    report.append(f"\nTOTAL CITATIONS: {total_citations}")
    report.append(f"  Papers: {total_papers}")
    report.append(f"  Videos: {total_videos}")
    report.append(f"  Podcasts: {total_podcasts}")

    # Most cited sources
    report.append("\n" + "="*60)
    report.append("TOP 10 MOST CITED SOURCES")
    report.append("="*60)

    most_cited = tracker.get_most_cited(10)
    for i, citation in enumerate(most_cited, 1):
        report.append(f"\n{i}. {citation['title']}")
        report.append(f"   Type: {citation['type']}")
        report.append(f"   Citations: {citation['use_count']}")

    # Recent activity
    report.append("\n" + "="*60)
    report.append("RECENT CITATION ACTIVITY (Last 10)")
    report.append("="*60)

    recent = tracker.get_recent_citations(10)
    for entry in recent:
        report.append(f"\n{entry['timestamp']}")
        report.append(f"  Query: {entry['query']}")
        report.append(f"  Source: {entry['citation_id']}")

    return '\n'.join(report)

# Usage
tracker = CitationTracker()
report = generate_citation_report(tracker)

with open('citation_report.txt', 'w') as f:
    f.write(report)

print(report)
```

## Next Steps

- Learn about [Custom Searches](custom-searches.md) to find more relevant sources
- Explore [Visualization Dashboard](visualization.md) to analyze citation patterns
- Check [Extending the System](extending.md) to add custom citation formats
- Review [Collecting Papers](collect-papers.md) to expand your research database
