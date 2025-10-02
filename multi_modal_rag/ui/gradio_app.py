# multi_modal_rag/ui/gradio_app.py
from ast import Dict
import gradio as gr
from typing import List, Tuple
import json
from multi_modal_rag.logging_config import get_logger

logger = get_logger(__name__)

class ResearchAssistantUI:
    """Gradio UI for the Research Assistant"""

    def __init__(self, orchestrator, citation_tracker, data_collectors, opensearch_manager=None):
        self.orchestrator = orchestrator
        self.citation_tracker = citation_tracker
        self.data_collectors = data_collectors
        self.opensearch_manager = opensearch_manager
        self.collected_data = []  # Store collected data for indexing
        logger.info("ResearchAssistantUI initialized")
        
    def create_interface(self):
        """Create Gradio interface"""
        
        with gr.Blocks(title="Multi-Modal Research Assistant", theme=gr.themes.Base()) as app:
            gr.Markdown("# 🎓 Multi-Modal Research Assistant")
            gr.Markdown("Query academic papers, video lectures, and podcasts with citation tracking")
            
            with gr.Tabs():
                # Research Tab
                with gr.TabItem("Research"):
                    with gr.Row():
                        with gr.Column(scale=2):
                            query_input = gr.Textbox(
                                label="Research Query",
                                placeholder="Enter your research question...",
                                lines=2
                            )
                            
                            with gr.Row():
                                search_btn = gr.Button("🔍 Search", variant="primary")
                                clear_btn = gr.Button("Clear")
                            
                            search_filters = gr.CheckboxGroup(
                                ["Papers", "Videos", "Podcasts"],
                                value=["Papers", "Videos", "Podcasts"],
                                label="Content Types"
                            )
                            
                        with gr.Column(scale=3):
                            answer_output = gr.Markdown(label="Answer")
                            citations_output = gr.JSON(label="Citations")
                            related_queries = gr.Markdown(label="Related Queries")
                
                # Data Collection Tab
                with gr.TabItem("Data Collection"):
                    with gr.Row():
                        with gr.Column():
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
                            
                        with gr.Column():
                            collection_status = gr.Textbox(
                                label="Collection Status",
                                lines=10
                            )
                            
                            collection_results = gr.JSON(label="Collection Results")
                
                # Citation Manager Tab
                with gr.TabItem("Citation Manager"):
                    with gr.Row():
                        with gr.Column():
                            citation_report = gr.JSON(label="Citation Report")
                            
                            refresh_report_btn = gr.Button("🔄 Refresh Report")
                            
                        with gr.Column():
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
                
                # Settings Tab
                with gr.TabItem("Settings"):
                    with gr.Row():
                        with gr.Column():
                            gr.Markdown("### OpenSearch Settings")
                            opensearch_host = gr.Textbox(
                                label="Host",
                                value="localhost"
                            )
                            opensearch_port = gr.Number(
                                label="Port",
                                value=9200
                            )
                            
                            gr.Markdown("### API Keys")
                            gemini_key = gr.Textbox(
                                label="Gemini API Key",
                                type="password",
                                placeholder="Enter your Gemini API key"
                            )
                            
                            save_settings_btn = gr.Button("💾 Save Settings")
                            
                        with gr.Column():
                            gr.Markdown("### Index Management")
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
            
            # Event handlers
            search_btn.click(
                fn=self.handle_search,
                inputs=[query_input, search_filters],
                outputs=[answer_output, citations_output, related_queries]
            )

            collect_btn.click(
                fn=self.handle_data_collection,
                inputs=[collection_type, collection_query, max_results],
                outputs=[collection_status, collection_results]
            )

            refresh_report_btn.click(
                fn=self.get_citation_report,
                outputs=citation_report
            )

            export_btn.click(
                fn=self.export_citations,
                inputs=export_format,
                outputs=exported_citations
            )

            # Index management handlers
            reindex_btn.click(
                fn=self.handle_reindex,
                inputs=[index_name],
                outputs=[index_status]
            )
            
        return app
    
    def handle_search(self, query: str, content_types: List[str]) -> Tuple:
        """Handle research query"""
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
    
    def handle_data_collection(self, source_type: str, query: str, max_results: int) -> Tuple:
        """Handle data collection and indexing"""
        logger.info(f"Starting data collection: source={source_type}, query={query}, max_results={max_results}")
        status_updates = []
        results = {}
        collected_items = []

        try:
            if source_type == "ArXiv Papers":
                status_updates.append("Collecting papers from ArXiv...")
                logger.info("Collecting ArXiv papers...")
                papers = self.data_collectors['paper_collector'].collect_arxiv_papers(
                    query, max_results
                )
                collected_items = papers
                results['papers_collected'] = len(papers)
                status_updates.append(f"✅ Collected {len(papers)} papers")
                logger.info(f"Collected {len(papers)} papers")

            elif source_type == "YouTube Lectures":
                status_updates.append("Searching YouTube for lectures...")
                logger.info("Collecting YouTube videos...")
                videos = self.data_collectors['video_collector'].search_youtube_lectures(
                    query, max_results
                )
                collected_items = videos
                results['videos_collected'] = len(videos)
                status_updates.append(f"✅ Collected {len(videos)} videos")
                logger.info(f"Collected {len(videos)} videos")

            elif source_type == "Podcasts":
                status_updates.append("Collecting podcast episodes...")
                logger.info("Collecting podcast episodes...")
                # Collect from multiple podcast feeds
                episodes = []
                for name, url in self.data_collectors['podcast_collector'].get_educational_podcasts().items():
                    eps = self.data_collectors['podcast_collector'].collect_podcast_episodes(
                        url, max_episodes=5
                    )
                    episodes.extend(eps)
                    if len(episodes) >= max_results:
                        break

                collected_items = episodes
                results['podcasts_collected'] = len(episodes)
                status_updates.append(f"✅ Collected {len(episodes)} episodes")
                logger.info(f"Collected {len(episodes)} episodes")

            # Index the collected data into OpenSearch
            if collected_items and self.opensearch_manager:
                status_updates.append("\n📊 Indexing data into OpenSearch...")
                logger.info(f"Starting to index {len(collected_items)} items")

                indexed_count = self._index_data(collected_items, source_type)

                status_updates.append(f"✅ Indexed {indexed_count} items into OpenSearch")
                results['items_indexed'] = indexed_count
                logger.info(f"Successfully indexed {indexed_count} items")

                # Store for later use
                self.collected_data.extend(collected_items)
            else:
                status_updates.append("\n⚠️  OpenSearch not available - data not indexed")
                logger.warning("OpenSearch manager not available, skipping indexing")

            status_updates.append("\n✅ Collection and indexing complete!")

        except Exception as e:
            error_msg = f"❌ Error: {str(e)}"
            status_updates.append(error_msg)
            logger.error(f"Error in data collection: {type(e).__name__}: {e}", exc_info=True)

        return '\n'.join(status_updates), results

    def _index_data(self, items: List, source_type: str) -> int:
        """Helper method to index collected data into OpenSearch"""
        logger.info(f"Indexing {len(items)} items of type: {source_type}")
        indexed_count = 0

        try:
            # Prepare documents for indexing
            documents = []
            for item in items:
                doc = self._format_document(item, source_type)
                if doc:
                    documents.append(doc)

            if documents:
                logger.debug(f"Prepared {len(documents)} documents for indexing")
                # Bulk index all documents
                self.opensearch_manager.bulk_index("research_assistant", documents)
                indexed_count = len(documents)
            else:
                logger.warning("No documents were prepared for indexing")

        except Exception as e:
            logger.error(f"Error indexing data: {type(e).__name__}: {e}", exc_info=True)

        return indexed_count

    def _format_document(self, item: dict, source_type: str) -> dict:
        """Format collected item into OpenSearch document format"""
        logger.debug(f"Formatting document from source_type: {source_type}")

        try:
            if source_type == "YouTube Lectures":
                return {
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
            elif source_type == "ArXiv Papers":
                return {
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
            elif source_type == "Podcasts":
                return {
                    'content_type': 'podcast',
                    'title': item.get('title', 'Unknown'),
                    'content': item.get('description', ''),
                    'transcript': item.get('transcript', ''),
                    'authors': [item.get('author', 'Unknown')],
                    'url': item.get('link', ''),
                    'publication_date': item.get('published', None),
                    'metadata': {
                        'audio_url': item.get('audio_url', '')
                    }
                }
            else:
                logger.warning(f"Unknown source_type: {source_type}")
                return None

        except Exception as e:
            logger.error(f"Error formatting document: {type(e).__name__}: {e}", exc_info=True)
            return None

    def handle_reindex(self, index_name: str) -> str:
        """Handle reindexing of all collected data"""
        logger.info(f"Starting reindex of all data to index: {index_name}")

        if not self.collected_data:
            msg = "⚠️  No data available to reindex. Collect data first."
            logger.warning(msg)
            return msg

        if not self.opensearch_manager:
            msg = "❌ OpenSearch not available"
            logger.error(msg)
            return msg

        try:
            # Reindex all collected data
            total_indexed = 0
            for source_type in ["YouTube Lectures", "ArXiv Papers", "Podcasts"]:
                items = [item for item in self.collected_data if self._matches_source_type(item, source_type)]
                if items:
                    count = self._index_data(items, source_type)
                    total_indexed += count

            msg = f"✅ Successfully reindexed {total_indexed} items to '{index_name}'"
            logger.info(msg)
            return msg

        except Exception as e:
            msg = f"❌ Error during reindexing: {str(e)}"
            logger.error(f"Reindex error: {type(e).__name__}: {e}", exc_info=True)
            return msg

    def _matches_source_type(self, item: dict, source_type: str) -> bool:
        """Check if item matches the source type"""
        if source_type == "YouTube Lectures":
            return 'video_id' in item
        elif source_type == "ArXiv Papers":
            return 'arxiv_id' in item.get('metadata', {}) or 'abstract' in item
        elif source_type == "Podcasts":
            return 'audio_url' in item or 'podcast' in str(item).lower()
        return False

    def get_citation_report(self) -> Dict:
        """Get citation usage report"""
        return self.citation_tracker.get_citation_report()
    
    def export_citations(self, format: str) -> str:
        """Export citations in specified format"""
        format_map = {
            'BibTeX': 'bibtex',
            'APA': 'apa',
            'JSON': 'json'
        }
        
        return self.citation_tracker.export_bibliography(format_map[format])