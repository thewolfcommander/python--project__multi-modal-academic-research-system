# multi_modal_rag/orchestration/citation_tracker.py
from typing import List, Dict, Set
import json
from datetime import datetime

class CitationTracker:
    """Track and manage citations across research sessions"""
    
    def __init__(self, storage_path: str = "data/citations.json"):
        self.storage_path = storage_path
        self.citations = self.load_citations()
        
    def load_citations(self) -> Dict:
        """Load existing citations from storage"""
        try:
            with open(self.storage_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                'papers': {},
                'videos': {},
                'podcasts': {},
                'usage_history': []
            }
    
    def save_citations(self):
        """Save citations to storage"""
        with open(self.storage_path, 'w') as f:
            json.dump(self.citations, f, indent=2)
    
    def add_citation(self, citation: Dict, query: str):
        """Add a new citation with usage tracking"""
        content_type = citation['content_type']
        citation_id = self.generate_citation_id(citation)
        
        # Store citation if new
        if citation_id not in self.citations[f'{content_type}s']:
            self.citations[f'{content_type}s'][citation_id] = {
                'title': citation['title'],
                'authors': citation.get('authors', []),
                'url': citation.get('url', ''),
                'first_used': datetime.now().isoformat(),
                'use_count': 0,
                'queries': []
            }
        
        # Update usage
        self.citations[f'{content_type}s'][citation_id]['use_count'] += 1
        self.citations[f'{content_type}s'][citation_id]['queries'].append({
            'query': query,
            'timestamp': datetime.now().isoformat()
        })
        
        # Add to history
        self.citations['usage_history'].append({
            'citation_id': citation_id,
            'content_type': content_type,
            'query': query,
            'timestamp': datetime.now().isoformat()
        })
        
        self.save_citations()
        
    def generate_citation_id(self, citation: Dict) -> str:
        """Generate unique ID for citation"""
        import hashlib
        
        unique_string = f"{citation.get('title', '')}{citation.get('url', '')}"
        return hashlib.md5(unique_string.encode()).hexdigest()[:12]
    
    def get_citation_report(self) -> Dict:
        """Generate citation usage report"""
        report = {
            'total_papers': len(self.citations['papers']),
            'total_videos': len(self.citations['videos']),
            'total_podcasts': len(self.citations['podcasts']),
            'most_cited': self.get_most_cited(5),
            'recent_citations': self.get_recent_citations(10)
        }
        
        return report
    
    def get_most_cited(self, n: int = 5) -> List[Dict]:
        """Get most frequently cited sources"""
        all_citations = []
        
        for content_type in ['papers', 'videos', 'podcasts']:
            for cid, citation in self.citations[content_type].items():
                all_citations.append({
                    'id': cid,
                    'type': content_type,
                    'title': citation['title'],
                    'use_count': citation['use_count']
                })
        
        return sorted(all_citations, key=lambda x: x['use_count'], reverse=True)[:n]
    
    def get_recent_citations(self, n: int = 10) -> List[Dict]:
        """Get most recent citations"""
        return self.citations['usage_history'][-n:][::-1]
    
    def export_bibliography(self, format: str = 'bibtex') -> str:
        """Export citations in standard bibliography format"""
        if format == 'bibtex':
            return self.export_bibtex()
        elif format == 'apa':
            return self.export_apa()
        else:
            return json.dumps(self.citations, indent=2)
    
    def export_bibtex(self) -> str:
        """Export citations in BibTeX format"""
        bibtex = []
        
        for cid, paper in self.citations['papers'].items():
            entry = f"""@article{{{cid},
    title={{{paper['title']}}},
    author={{{' and '.join(paper.get('authors', ['Unknown']))}}},
    year={{{paper.get('first_used', '')[:4]}}},
    url={{{paper.get('url', '')}}}
}}"""
            bibtex.append(entry)
        
        return '\n\n'.join(bibtex)
    
    def export_apa(self) -> str:
        """Export citations in APA format"""
        apa = []
        
        for paper in self.citations['papers'].values():
            authors = paper.get('authors', ['Unknown'])
            year = paper.get('first_used', '')[:4] or 'n.d.'
            
            if authors:
                author_str = authors[0] if len(authors) == 1 else f"{authors[0]} et al."
            else:
                author_str = "Unknown"
                
            citation = f"{author_str} ({year}). {paper['title']}. Retrieved from {paper.get('url', 'N/A')}"
            apa.append(citation)
        
        return '\n'.join(sorted(apa))