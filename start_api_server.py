#!/usr/bin/env python
"""
Start the FastAPI visualization server

This script starts the FastAPI server for data visualization.
The server provides REST API endpoints and a web-based visualization dashboard.

Usage:
    python start_api_server.py

The server will be available at:
    - API endpoints: http://localhost:8000/api/
    - Visualization dashboard: http://localhost:8000/viz
    - API docs: http://localhost:8000/docs
"""

import uvicorn
from multi_modal_rag.logging_config import setup_logging, get_logger

def main():
    """Start the FastAPI server"""
    # Initialize logging
    logger, log_file = setup_logging()
    logger.info("="*80)
    logger.info("Starting FastAPI Visualization Server")
    logger.info(f"Log file location: {log_file}")
    logger.info("="*80)

    print("🚀 Starting FastAPI Visualization Server...")
    print("📊 Dashboard will be available at: http://localhost:8000/viz")
    print("📡 API endpoints at: http://localhost:8000/api/")
    print("📖 API docs at: http://localhost:8000/docs")
    print(f"📝 Logs are being written to: {log_file}")
    print("\nPress CTRL+C to stop the server\n")

    logger.info("Starting Uvicorn server on 0.0.0.0:8000")

    try:
        uvicorn.run(
            "multi_modal_rag.api.api_server:app",
            host="0.0.0.0",
            port=8000,
            reload=True,  # Auto-reload on code changes
            log_level="info"
        )
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        print("\n✅ Server stopped")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        print(f"\n❌ Server error: {e}")
        raise

if __name__ == "__main__":
    main()
