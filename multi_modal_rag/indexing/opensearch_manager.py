# multi_modal_rag/indexing/opensearch_manager.py
from opensearchpy import OpenSearch, helpers
from typing import List, Dict
import json
from sentence_transformers import SentenceTransformer

class OpenSearchManager:
    """Manage OpenSearch indexing and retrieval"""
    
    def __init__(self, host: str = 'localhost', port: int = 9200):
        # For free tier, you can use OpenSearch locally via Docker
        self.client = OpenSearch(
            hosts=[{'host': host, 'port': port}],
            http_compress=True,
            use_ssl=False,
            verify_certs=False,
            ssl_assert_hostname=False,
            ssl_show_warn=False,
        )
        
        # Embedding model for semantic search
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
    def create_index(self, index_name: str):
        """
        Create index with proper mappings for multi-modal content
        """
        index_body = {
            'settings': {
                'index': {
                    'number_of_shards': 2,
                    'number_of_replicas': 1,
                    'knn': True,
                    'knn.space_type': 'cosinesimil'
                }
            },
            'mappings': {
                'properties': {
                    'content_type': {'type': 'keyword'},  # paper, video, podcast
                    'title': {
                        'type': 'text',
                        'fields': {
                            'keyword': {'type': 'keyword'}
                        }
                    },
                    'abstract': {'type': 'text'},
                    'content': {'type': 'text'},
                    'authors': {'type': 'keyword'},
                    'publication_date': {'type': 'date'},
                    'url': {'type': 'keyword'},
                    'transcript': {'type': 'text'},
                    'diagram_descriptions': {'type': 'text'},
                    'key_concepts': {'type': 'keyword'},
                    'citations': {
                        'type': 'nested',
                        'properties': {
                            'text': {'type': 'text'},
                            'source': {'type': 'keyword'}
                        }
                    },
                    'embedding': {
                        'type': 'knn_vector',
                        'dimension': 384  # for all-MiniLM-L6-v2
                    },
                    'metadata': {
                        'type': 'object',
                        'enabled': True
                    }
                }
            }
        }
        
        if not self.client.indices.exists(index=index_name):
            self.client.indices.create(index=index_name, body=index_body)
            print(f"Index '{index_name}' created successfully")
            
    def index_document(self, index_name: str, document: Dict):
        """
        Index a single document with embeddings
        """
        # Generate embedding for searchable content
        searchable_text = f"{document.get('title', '')} {document.get('abstract', '')} {document.get('content', '')[:1000]}"
        embedding = self.embedding_model.encode(searchable_text).tolist()
        
        document['embedding'] = embedding
        
        response = self.client.index(
            index=index_name,
            body=document
        )
        
        return response
    
    def bulk_index(self, index_name: str, documents: List[Dict]):
        """
        Bulk index multiple documents
        """
        actions = []
        
        for doc in documents:
            # Generate embedding
            searchable_text = f"{doc.get('title', '')} {doc.get('abstract', '')} {doc.get('content', '')[:1000]}"
            doc['embedding'] = self.embedding_model.encode(searchable_text).tolist()
            
            action = {
                "_index": index_name,
                "_source": doc
            }
            actions.append(action)
        
        helpers.bulk(self.client, actions)
        print(f"Indexed {len(documents)} documents")
    
    def hybrid_search(self, index_name: str, query: str, k: int = 10) -> List[Dict]:
        """
        Perform hybrid search (keyword + semantic)
        """
        # Generate query embedding
        query_embedding = self.embedding_model.encode(query).tolist()
        
        # Hybrid query combining text and vector search
        search_query = {
            'size': k,
            'query': {
                'bool': {
                    'should': [
                        {
                            'multi_match': {
                                'query': query,
                                'fields': ['title^2', 'abstract', 'content', 'transcript'],
                                'type': 'best_fields'
                            }
                        },
                        {
                            'script_score': {
                                'query': {'match_all': {}},
                                'script': {
                                    'source': "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                                    'params': {
                                        'query_vector': query_embedding
                                    }
                                }
                            }
                        }
                    ]
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