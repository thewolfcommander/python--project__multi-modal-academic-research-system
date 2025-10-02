# multi_modal_rag/indexing/opensearch_manager.py
from opensearchpy import OpenSearch, helpers
from typing import List, Dict
import json
from sentence_transformers import SentenceTransformer
from multi_modal_rag.logging_config import get_logger

logger = get_logger(__name__)

class OpenSearchManager:
    """Manage OpenSearch indexing and retrieval"""
    
    def __init__(self, host: str = 'localhost', port: int = 9200,
                 use_ssl: bool = True, username: str = 'admin', password: str = 'MyStrongPassword@2024!'):
        # For free tier, you can use OpenSearch locally via Docker
        logger.info(f"Initializing OpenSearchManager with host={host}, port={port}, use_ssl={use_ssl}")
        self.host = host
        self.port = port
        self.client = None
        self.connected = False

        try:
            logger.debug(f"Creating OpenSearch client connection...")
            self.client = OpenSearch(
                hosts=[{'host': host, 'port': port}],
                http_auth=(username, password),
                http_compress=True,
                use_ssl=use_ssl,
                verify_certs=False,
                ssl_assert_hostname=False,
                ssl_show_warn=False,
                timeout=5
            )
            # Test connection
            logger.debug("Testing OpenSearch connection...")
            info = self.client.info()
            self.connected = True
            logger.info(f"✅ Successfully connected to OpenSearch at {host}:{port}")
            logger.debug(f"OpenSearch cluster info: {info.get('cluster_name', 'N/A')}, version: {info.get('version', {}).get('number', 'N/A')}")
            print(f"✅ Connected to OpenSearch at {host}:{port}")
        except Exception as e:
            logger.error(f"⚠️  Failed to connect to OpenSearch at {host}:{port}: {type(e).__name__}: {e}", exc_info=True)
            logger.warning("App will run with limited search functionality")
            print(f"⚠️  OpenSearch not available at {host}:{port}: {e}")
            print("   App will run with limited search functionality")

        # Embedding model for semantic search
        logger.info("Loading sentence transformer model 'all-MiniLM-L6-v2'...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info("Sentence transformer model loaded successfully")
        
    def create_index(self, index_name: str):
        """
        Create index with proper mappings for multi-modal content
        """
        logger.info(f"Attempting to create index: {index_name}")
        if not self.connected:
            logger.error(f"⚠️  Cannot create index '{index_name}' - OpenSearch not connected")
            print(f"⚠️  Cannot create index - OpenSearch not connected")
            return False

        logger.debug(f"Preparing index mapping for '{index_name}'")
        index_body = {
            'settings': {
                'index': {
                    'number_of_shards': 2,
                    'number_of_replicas': 1,
                    'knn': True
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

        try:
            if not self.client.indices.exists(index=index_name):
                logger.debug(f"Index '{index_name}' does not exist, creating now...")
                self.client.indices.create(index=index_name, body=index_body)
                logger.info(f"✅ Index '{index_name}' created successfully")
                print(f"Index '{index_name}' created successfully")
            else:
                logger.info(f"Index '{index_name}' already exists, skipping creation")
                print(f"Index '{index_name}' already exists")
        except Exception as e:
            logger.error(f"Error creating index '{index_name}': {type(e).__name__}: {e}", exc_info=True)
            return False

        return True
            
    def index_document(self, index_name: str, document: Dict):
        """
        Index a single document with embeddings
        """
        logger.debug(f"Indexing single document to '{index_name}': {document.get('title', 'Untitled')}")
        if not self.connected:
            logger.error(f"⚠️  Cannot index document - OpenSearch not connected")
            print(f"⚠️  Cannot index document - OpenSearch not connected")
            return None

        try:
            # Generate embedding for searchable content
            searchable_text = f"{document.get('title', '')} {document.get('abstract', '')} {document.get('content', '')[:1000]}"
            logger.debug(f"Generating embedding for document (text length: {len(searchable_text)})")
            embedding = self.embedding_model.encode(searchable_text).tolist()

            document['embedding'] = embedding

            response = self.client.index(
                index=index_name,
                body=document
            )

            logger.info(f"✅ Successfully indexed document: {document.get('title', 'Untitled')}")
            return response

        except Exception as e:
            logger.error(f"Error indexing document to '{index_name}': {type(e).__name__}: {e}", exc_info=True)
            return None
    
    def bulk_index(self, index_name: str, documents: List[Dict]):
        """
        Bulk index multiple documents
        """
        logger.info(f"Starting bulk indexing of {len(documents)} documents to '{index_name}'")
        if not self.connected:
            logger.error(f"⚠️  Cannot bulk index - OpenSearch not connected")
            print(f"⚠️  Cannot bulk index - OpenSearch not connected")
            return None

        try:
            actions = []

            for idx, doc in enumerate(documents, 1):
                logger.debug(f"Processing document {idx}/{len(documents)} for bulk index: {doc.get('title', 'Untitled')}")
                # Generate embedding
                searchable_text = f"{doc.get('title', '')} {doc.get('abstract', '')} {doc.get('content', '')[:1000]}"
                doc['embedding'] = self.embedding_model.encode(searchable_text).tolist()

                action = {
                    "_index": index_name,
                    "_source": doc
                }
                actions.append(action)

            logger.debug(f"Executing bulk index operation...")
            success, failed = helpers.bulk(self.client, actions, stats_only=True)
            logger.info(f"✅ Bulk indexed {success} documents successfully to '{index_name}'")
            if failed > 0:
                logger.warning(f"⚠️  {failed} documents failed to index")
            print(f"Indexed {success} documents")
            return success

        except Exception as e:
            logger.error(f"Error during bulk indexing to '{index_name}': {type(e).__name__}: {e}", exc_info=True)
            return None
    
    def hybrid_search(self, index_name: str, query: str, k: int = 10) -> List[Dict]:
        """
        Perform hybrid search (keyword + semantic)
        """
        logger.info(f"Performing hybrid search on '{index_name}' for query: '{query}' (k={k})")
        if not self.connected:
            logger.error(f"⚠️  Cannot search - OpenSearch not connected")
            print(f"⚠️  Cannot search - OpenSearch not connected")
            return []

        try:
            # Simplified text-based search (vector search disabled for OpenSearch 3.x compatibility)
            search_query = {
                'size': k,
                'query': {
                    'multi_match': {
                        'query': query,
                        'fields': ['title^3', 'abstract^2', 'content', 'transcript', 'key_concepts^2'],
                        'type': 'best_fields',
                        'fuzziness': 'AUTO'
                    }
                }
            }

            logger.debug(f"Executing search query: {search_query}")
            response = self.client.search(index=index_name, body=search_query)

            total_hits = response['hits']['total']['value'] if isinstance(response['hits']['total'], dict) else response['hits']['total']
            logger.info(f"Search returned {total_hits} total hits, retrieving top {len(response['hits']['hits'])} results")

            results = []
            for idx, hit in enumerate(response['hits']['hits'], 1):
                logger.debug(f"Result {idx}: {hit['_source'].get('title', 'Untitled')} (score: {hit['_score']:.4f})")
                results.append({
                    'score': hit['_score'],
                    'source': hit['_source']
                })

            logger.info(f"✅ Successfully completed search, returning {len(results)} results")
            return results

        except Exception as e:
            logger.error(f"Error during hybrid search on '{index_name}': {type(e).__name__}: {e}", exc_info=True)
            return []