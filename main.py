# main.py
import os
from dotenv import load_dotenv
from multi_modal_rag.data_collectors.paper_collector import AcademicPaperCollector
from multi_modal_rag.data_collectors.youtube_collector import YouTubeLectureCollector
from multi_modal_rag.data_collectors.podcast_collector import PodcastCollector
from multi_modal_rag.data_processors.pdf_processor import PDFProcessor
from multi_modal_rag.data_processors.video_processor import VideoProcessor
from multi_modal_rag.indexing.opensearch_manager import OpenSearchManager
from multi_modal_rag.orchestration.research_orchestrator import ResearchOrchestrator
from multi_modal_rag.orchestration.citation_tracker import CitationTracker
from multi_modal_rag.ui.gradio_app import ResearchAssistantUI

def main():
    """Main application entry point"""
    
    # Load environment variables
    load_dotenv()
    
    # Get API keys (Gemini is the only required API)
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    
    if not GEMINI_API_KEY:
        print("⚠️  Please set GEMINI_API_KEY in your .env file")
        print("Get your free API key at: https://makersuite.google.com/app/apikey")
        return
    
    # Initialize components
    print("🚀 Initializing Multi-Modal Research Assistant...")
    
    # Data collectors
    paper_collector = AcademicPaperCollector()
    video_collector = YouTubeLectureCollector()
    podcast_collector = PodcastCollector()
    
    # Data processors
    pdf_processor = PDFProcessor(GEMINI_API_KEY)
    video_processor = VideoProcessor(GEMINI_API_KEY)
    
    # OpenSearch manager
    opensearch_manager = OpenSearchManager()
    
    # Create index if it doesn't exist
    opensearch_manager.create_index("research_assistant")
    
    # Orchestrator and citation tracker
    orchestrator = ResearchOrchestrator(GEMINI_API_KEY, opensearch_manager)
    citation_tracker = CitationTracker()
    
    # Create UI
    data_collectors = {
        'paper_collector': paper_collector,
        'video_collector': video_collector,
        'podcast_collector': podcast_collector
    }
    
    ui = ResearchAssistantUI(orchestrator, citation_tracker, data_collectors)
    app = ui.create_interface()
    
    print("✅ Research Assistant ready!")
    print("🌐 Opening web interface...")
    
    # Launch app
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True  # Creates a public link
    )

if __name__ == "__main__":
    main()