# multi_modal_rag/ui/gradio_app.py
from ast import Dict
import gradio as gr
from typing import List, Tuple
import json
from multi_modal_rag.logging_config import get_logger
from multi_modal_rag.database import CollectionDatabaseManager

logger = get_logger(__name__)

class ResearchAssistantUI:
    """Gradio UI for the Research Assistant"""

    def __init__(self, orchestrator, citation_tracker, data_collectors, opensearch_manager=None, db_manager=None):
        self.orchestrator = orchestrator
        self.citation_tracker = citation_tracker
        self.data_collectors = data_collectors
        self.opensearch_manager = opensearch_manager
        self.db_manager = db_manager or CollectionDatabaseManager()
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

                # Data Visualization Tab
                with gr.TabItem("Data Visualization"):
                    with gr.Row():
                        with gr.Column():
                            gr.Markdown("### Collection Statistics")
                            stats_display = gr.JSON(label="Statistics")
                            refresh_stats_btn = gr.Button("🔄 Refresh Statistics")

                            gr.Markdown("### Quick Stats")
                            quick_stats = gr.Markdown("")

                        with gr.Column():
                            gr.Markdown("### Recent Collections")
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

                    collections_table = gr.Dataframe(
                        headers=["ID", "Type", "Title", "Source", "Indexed", "Date"],
                        label="Collection Data",
                        wrap=True
                    )

                    gr.Markdown("### External Visualization")
                    gr.Markdown("""
                        For advanced visualization with charts and filtering, visit the FastAPI dashboard:

                        **[Open Visualization Dashboard](http://localhost:8000/viz)** (Start FastAPI server first)

                        To start the FastAPI server, run:
                        ```bash
                        python -m uvicorn multi_modal_rag.api.api_server:app --host 0.0.0.0 --port 8000
                        ```
                    """)

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

            # Data visualization handlers
            refresh_stats_btn.click(
                fn=self.get_database_statistics,
                outputs=[stats_display, quick_stats]
            )

            refresh_collections_btn.click(
                fn=self.get_collection_data,
                inputs=[content_type_filter, limit_slider],
                outputs=collections_table
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
        collection_ids = []  # Track collection IDs for marking as indexed

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

                # Track in database
                for paper in papers:
                    collection_id = self.db_manager.add_collection(
                        content_type='paper',
                        title=paper.get('title', 'Unknown'),
                        source='arxiv',
                        url=paper.get('pdf_url', ''),
                        metadata={
                            'query': query,
                            'categories': paper.get('categories', [])
                        }
                    )
                    self.db_manager.add_paper(collection_id, paper)
                    collection_ids.append(collection_id)
                self.db_manager.log_collection_stats('paper', query, len(papers), 'arxiv')

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

                # Track in database
                for video in videos:
                    collection_id = self.db_manager.add_collection(
                        content_type='video',
                        title=video.get('title', 'Unknown'),
                        source='youtube',
                        url=video.get('url', ''),
                        metadata={
                            'query': query,
                            'description': video.get('description', '')
                        }
                    )
                    self.db_manager.add_video(collection_id, video)
                    collection_ids.append(collection_id)
                self.db_manager.log_collection_stats('video', query, len(videos), 'youtube')

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

                # Track in database
                for episode in episodes:
                    collection_id = self.db_manager.add_collection(
                        content_type='podcast',
                        title=episode.get('title', 'Unknown'),
                        source='podcast',
                        url=episode.get('link', ''),
                        metadata={
                            'query': query,
                            'description': episode.get('description', '')
                        }
                    )
                    self.db_manager.add_podcast(collection_id, episode)
                    collection_ids.append(collection_id)
                self.db_manager.log_collection_stats('podcast', query, len(episodes), 'rss')

            # Index the collected data into OpenSearch
            if collected_items and self.opensearch_manager:
                status_updates.append("\n📊 Indexing data into OpenSearch...")
                logger.info(f"Starting to index {len(collected_items)} items")

                indexed_count = self._index_data(collected_items, source_type)

                status_updates.append(f"✅ Indexed {indexed_count} items into OpenSearch")
                results['items_indexed'] = indexed_count
                logger.info(f"Successfully indexed {indexed_count} items")

                # Mark all collection items as indexed in database
                for cid in collection_ids:
                    self.db_manager.mark_as_indexed(cid)

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

    def get_database_statistics(self) -> Tuple:
        """Get database statistics for visualization"""
        try:
            stats = self.db_manager.get_statistics()

            # Format quick stats markdown
            by_type = stats.get('by_type', {})
            total = sum(by_type.values())
            indexed = stats.get('indexed', 0)
            recent = stats.get('recent_7_days', 0)

            quick_stats_md = f"""
            ### Overview
            - **Total Collections**: {total}
            - **Indexed**: {indexed} ({indexed/total*100:.1f}% if total > 0 else 0%)
            - **Recent (7 days)**: {recent}

            ### By Type
            - **Papers**: {by_type.get('paper', 0)}
            - **Videos**: {by_type.get('video', 0)}
            - **Podcasts**: {by_type.get('podcast', 0)}
            """

            return stats, quick_stats_md
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}, f"Error loading statistics: {str(e)}"

    def get_collection_data(self, content_type_filter: str, limit: int) -> List:
        """Get collection data for table display"""
        try:
            # Map filter to database type
            type_map = {
                'All': None,
                'Papers': 'paper',
                'Videos': 'video',
                'Podcasts': 'podcast'
            }

            db_type = type_map.get(content_type_filter)

            if db_type:
                collections = self.db_manager.get_collections_by_type(db_type, limit)
            else:
                collections = self.db_manager.get_all_collections(limit)

            # Format for Gradio table
            table_data = []
            for item in collections:
                table_data.append([
                    item['id'],
                    item['content_type'],
                    item['title'][:100] + '...' if len(item['title']) > 100 else item['title'],
                    item['source'] or 'N/A',
                    'Yes' if item['indexed'] else 'No',
                    item['collection_date'].split('T')[0] if 'T' in item['collection_date'] else item['collection_date']
                ])

            return table_data
        except Exception as e:
            logger.error(f"Error getting collection data: {e}")
            return [["Error", "Error", f"Failed to load data: {str(e)}", "", "", ""]]