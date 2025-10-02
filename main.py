# main.py
import os
from dotenv import load_dotenv
from multi_modal_rag.logging_config import setup_logging, get_logger
from multi_modal_rag.data_collectors.paper_collector import AcademicPaperCollector
from multi_modal_rag.data_collectors.youtube_collector import YouTubeLectureCollector
from multi_modal_rag.data_collectors.podcast_collector import PodcastCollector
from multi_modal_rag.data_processors.pdf_processor import PDFProcessor
from multi_modal_rag.data_processors.video_processor import VideoProcessor
from multi_modal_rag.indexing.opensearch_manager import OpenSearchManager
from multi_modal_rag.orchestration.research_orchestrator import ResearchOrchestrator
from multi_modal_rag.orchestration.citation_tracker import CitationTracker
from multi_modal_rag.ui.gradio_app import ResearchAssistantUI
from multi_modal_rag.database import CollectionDatabaseManager

def main():
    """Main application entry point"""

    # Initialize logging first
    logger, log_file = setup_logging()
    logger.info("="*80)
    logger.info("Starting Multi-Modal Research Assistant Application")
    logger.info(f"Log file location: {log_file}")
    logger.info("="*80)

    # Load environment variables
    logger.info("Loading environment variables from .env file")
    load_dotenv()
    
    # Get API keys (Gemini is the only required API)
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

    if not GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY not found in environment variables")
        print("⚠️  Please set GEMINI_API_KEY in your .env file")
        print("Get your free API key at: https://makersuite.google.com/app/apikey")
        return

    logger.info("✅ GEMINI_API_KEY found")

    # Initialize components
    print("🚀 Initializing Multi-Modal Research Assistant...")
    logger.info("Initializing application components...")

    try:
        # Data collectors
        logger.info("Creating data collectors...")
        paper_collector = AcademicPaperCollector()
        video_collector = YouTubeLectureCollector()
        podcast_collector = PodcastCollector()
        logger.info("✅ Data collectors created")

        # Data processors
        logger.info("Creating data processors...")
        pdf_processor = PDFProcessor(GEMINI_API_KEY)
        video_processor = VideoProcessor(GEMINI_API_KEY)
        logger.info("✅ Data processors created")

        # OpenSearch manager
        logger.info("Creating OpenSearch manager...")
        opensearch_manager = OpenSearchManager()

        # Create index if it doesn't exist
        logger.info("Creating/verifying research_assistant index...")
        opensearch_manager.create_index("research_assistant")

        # Orchestrator and citation tracker
        logger.info("Creating orchestrator and citation tracker...")
        orchestrator = ResearchOrchestrator(GEMINI_API_KEY, opensearch_manager)
        citation_tracker = CitationTracker()
        logger.info("✅ Orchestrator and citation tracker created")

        # Database manager
        logger.info("Creating database manager...")
        db_manager = CollectionDatabaseManager()
        logger.info("✅ Database manager created")

        # Create UI
        logger.info("Creating Gradio UI...")
        data_collectors = {
            'paper_collector': paper_collector,
            'video_collector': video_collector,
            'podcast_collector': podcast_collector
        }

        ui = ResearchAssistantUI(
            orchestrator,
            citation_tracker,
            data_collectors,
            opensearch_manager=opensearch_manager,  # Pass OpenSearch manager for indexing
            db_manager=db_manager  # Pass database manager for tracking
        )
        app = ui.create_interface()
        logger.info("✅ Gradio UI created")

        print("✅ Research Assistant ready!")
        print("🌐 Opening web interface...")
        print(f"📝 Logs are being written to: {log_file}")

        logger.info("Launching Gradio application...")
        logger.info("Server: 0.0.0.0:7860 (with public sharing enabled)")

        # Launch app
        app.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=True  # Creates a public link
        )

    except Exception as e:
        logger.critical(f"Fatal error during application startup: {type(e).__name__}: {e}", exc_info=True)
        print(f"❌ Fatal error: {e}")
        print(f"📝 Check logs for details: {log_file}")
        raise

if __name__ == "__main__":
    main()