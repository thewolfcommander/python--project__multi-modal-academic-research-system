# multi_modal_rag/data_collectors/paper_collector.py
import arxiv
import requests
from typing import List, Dict
import os
import time
from scholarly import scholarly
import json

class AcademicPaperCollector:
    """Collect free academic papers from various sources"""
    
    def __init__(self, save_dir: str = "data/papers"):
        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)
        
    def collect_arxiv_papers(self, query: str, max_results: int = 100) -> List[Dict]:
        """
        Collect papers from arXiv (completely free)
        """
        papers = []
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )
        
        for result in search.results():
            paper_data = {
                'title': result.title,
                'abstract': result.summary,
                'authors': [author.name for author in result.authors],
                'pdf_url': result.pdf_url,
                'arxiv_id': result.entry_id,
                'published': result.published.isoformat(),
                'categories': result.categories
            }
            
            # Download PDF
            pdf_path = os.path.join(self.save_dir, f"{result.entry_id.split('/')[-1]}.pdf")
            result.download_pdf(dirpath=self.save_dir, filename=f"{result.entry_id.split('/')[-1]}.pdf")
            paper_data['local_path'] = pdf_path
            
            papers.append(paper_data)
            time.sleep(1)  # Be respectful to the API
            
        return papers
    
    def collect_pubmed_central(self, query: str, max_results: int = 50) -> List[Dict]:
        """
        Collect from PubMed Central Open Access Subset
        """
        base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
        
        # Search for PMC IDs
        search_url = f"{base_url}esearch.fcgi"
        search_params = {
            'db': 'pmc',
            'term': f'{query} AND "open access"[filter]',
            'retmax': max_results,
            'retmode': 'json'
        }
        
        response = requests.get(search_url, params=search_params)
        search_results = response.json()
        
        papers = []
        if 'esearchresult' in search_results:
            pmc_ids = search_results['esearchresult'].get('idlist', [])
            
            for pmc_id in pmc_ids[:max_results]:
                # Fetch paper details
                fetch_url = f"{base_url}efetch.fcgi"
                fetch_params = {
                    'db': 'pmc',
                    'id': pmc_id,
                    'retmode': 'xml'
                }
                
                paper_data = {
                    'pmc_id': pmc_id,
                    'source': 'pubmed_central',
                    'pdf_url': f"https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{pmc_id}/pdf/"
                }
                papers.append(paper_data)
                time.sleep(0.5)
                
        return papers
    
    def collect_semantic_scholar(self, query: str, max_results: int = 50) -> List[Dict]:
        """
        Collect from Semantic Scholar (free API)
        """
        base_url = "https://api.semanticscholar.org/graph/v1/paper/search"
        
        params = {
            'query': query,
            'limit': max_results,
            'fields': 'title,abstract,authors,year,url,openAccessPdf'
        }
        
        response = requests.get(base_url, params=params)
        papers = []
        
        if response.status_code == 200:
            data = response.json()
            for paper in data.get('data', []):
                if paper.get('openAccessPdf'):
                    paper_data = {
                        'title': paper.get('title'),
                        'abstract': paper.get('abstract'),
                        'authors': paper.get('authors', []),
                        'year': paper.get('year'),
                        'pdf_url': paper['openAccessPdf']['url'],
                        'source': 'semantic_scholar'
                    }
                    papers.append(paper_data)
                    
        return papers