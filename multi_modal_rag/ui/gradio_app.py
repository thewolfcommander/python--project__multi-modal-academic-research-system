# multi_modal_rag/ui/gradio_app.py
from ast import Dict
import gradio as gr
from typing import List, Tuple
import json

class ResearchAssistantUI:
    """Gradio UI for the Research Assistant"""
    
    def __init__(self, orchestrator, citation_tracker, data_collectors):
        self.orchestrator = orchestrator
        self.citation_tracker = citation_tracker
        self.data_collectors = data_collectors
        
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
        """Handle data collection"""
        status_updates = []
        results = {}
        
        try:
            if source_type == "ArXiv Papers":
                status_updates.append("Collecting papers from ArXiv...")
                papers = self.data_collectors['paper_collector'].collect_arxiv_papers(
                    query, max_results
                )
                results['papers_collected'] = len(papers)
                status_updates.append(f"✅ Collected {len(papers)} papers")
                
            elif source_type == "YouTube Lectures":
                status_updates.append("Searching YouTube for lectures...")
                videos = self.data_collectors['video_collector'].search_youtube_lectures(
                    query, max_results
                )
                results['videos_collected'] = len(videos)
                status_updates.append(f"✅ Collected {len(videos)} videos")
                
            elif source_type == "Podcasts":
                status_updates.append("Collecting podcast episodes...")
                # Collect from multiple podcast feeds
                episodes = []
                for name, url in self.data_collectors['podcast_collector'].get_educational_podcasts().items():
                    eps = self.data_collectors['podcast_collector'].collect_podcast_episodes(
                        url, max_episodes=5
                    )
                    episodes.extend(eps)
                    if len(episodes) >= max_results:
                        break
                        
                results['podcasts_collected'] = len(episodes)
                status_updates.append(f"✅ Collected {len(episodes)} episodes")
            
            status_updates.append("\n✅ Collection complete!")
            
        except Exception as e:
            status_updates.append(f"❌ Error: {str(e)}")
            
        return '\n'.join(status_updates), results
    
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