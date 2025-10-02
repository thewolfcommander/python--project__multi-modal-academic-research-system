# multi_modal_rag/api/api_server.py
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from typing import Optional, List
import os
from multi_modal_rag.database import CollectionDatabaseManager
from multi_modal_rag.logging_config import get_logger

logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Multi-Modal Research Data API",
    description="API for visualizing collected research data",
    version="1.0.0"
)

# Add CORS middleware to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database manager
db_manager = CollectionDatabaseManager()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Multi-Modal Research Data API",
        "endpoints": {
            "collections": "/api/collections",
            "statistics": "/api/statistics",
            "search": "/api/search",
            "visualization": "/viz"
        }
    }


@app.get("/api/collections")
async def get_collections(
    content_type: Optional[str] = Query(None, description="Filter by content type: paper, video, podcast"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    """Get all collections with optional filtering"""
    try:
        if content_type:
            collections = db_manager.get_collections_by_type(content_type, limit)
        else:
            collections = db_manager.get_all_collections(limit, offset)

        return {
            "count": len(collections),
            "collections": collections
        }
    except Exception as e:
        logger.error(f"Error fetching collections: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/collections/{collection_id}")
async def get_collection_details(collection_id: int):
    """Get detailed information about a specific collection"""
    try:
        collection = db_manager.get_collection_with_details(collection_id)
        if not collection:
            raise HTTPException(status_code=404, detail="Collection not found")
        return collection
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching collection details: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/statistics")
async def get_statistics():
    """Get database statistics"""
    try:
        stats = db_manager.get_statistics()
        return stats
    except Exception as e:
        logger.error(f"Error fetching statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/search")
async def search_collections(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(50, ge=1, le=500)
):
    """Search collections by title or source"""
    try:
        results = db_manager.search_collections(q, limit)
        return {
            "query": q,
            "count": len(results),
            "results": results
        }
    except Exception as e:
        logger.error(f"Error searching collections: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/viz", response_class=HTMLResponse)
async def visualization_page():
    """Serve the visualization HTML page"""
    html_file = os.path.join(
        os.path.dirname(__file__),
        "static",
        "visualization.html"
    )

    try:
        with open(html_file, "r") as f:
            return f.read()
    except FileNotFoundError:
        return """
        <html>
            <body>
                <h1>Visualization page not found</h1>
                <p>Please ensure visualization.html exists in the static directory</p>
            </body>
        </html>
        """


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    logger.info("Starting FastAPI server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
