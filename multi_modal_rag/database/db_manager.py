# multi_modal_rag/database/db_manager.py
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
import os
from multi_modal_rag.logging_config import get_logger

logger = get_logger(__name__)


class CollectionDatabaseManager:
    """SQLite database manager for tracking collected data"""

    def __init__(self, db_path: str = "data/collections.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_database()
        logger.info(f"CollectionDatabaseManager initialized with database at {db_path}")

    def _init_database(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Main collections table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS collections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content_type TEXT NOT NULL,
                title TEXT NOT NULL,
                source TEXT,
                url TEXT,
                collection_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT,
                status TEXT DEFAULT 'collected',
                indexed BOOLEAN DEFAULT 0
            )
        """)

        # Papers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS papers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                collection_id INTEGER,
                arxiv_id TEXT,
                pmc_id TEXT,
                abstract TEXT,
                authors TEXT,
                published_date TEXT,
                categories TEXT,
                pdf_path TEXT,
                FOREIGN KEY (collection_id) REFERENCES collections(id)
            )
        """)

        # Videos table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                collection_id INTEGER,
                video_id TEXT,
                channel TEXT,
                duration INTEGER,
                views INTEGER,
                thumbnail_url TEXT,
                transcript_available BOOLEAN DEFAULT 0,
                FOREIGN KEY (collection_id) REFERENCES collections(id)
            )
        """)

        # Podcasts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS podcasts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                collection_id INTEGER,
                episode_id TEXT,
                podcast_name TEXT,
                audio_url TEXT,
                duration INTEGER,
                FOREIGN KEY (collection_id) REFERENCES collections(id)
            )
        """)

        # Collection statistics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS collection_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content_type TEXT,
                query TEXT,
                results_count INTEGER,
                collection_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                source_api TEXT
            )
        """)

        conn.commit()
        conn.close()
        logger.info("Database schema initialized successfully")

    def add_collection(self, content_type: str, title: str, source: str,
                      url: str, metadata: Dict, indexed: bool = False) -> int:
        """Add a new collection item and return its ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO collections (content_type, title, source, url, metadata, indexed)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (content_type, title, source, url, json.dumps(metadata), indexed))

            collection_id = cursor.lastrowid
            conn.commit()
            logger.debug(f"Added collection item: {collection_id} - {title}")
            return collection_id
        except Exception as e:
            logger.error(f"Error adding collection: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()

    def add_paper(self, collection_id: int, paper_data: Dict):
        """Add paper-specific data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO papers (collection_id, arxiv_id, pmc_id, abstract,
                                   authors, published_date, categories, pdf_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                collection_id,
                paper_data.get('arxiv_id'),
                paper_data.get('pmc_id'),
                paper_data.get('abstract'),
                json.dumps(paper_data.get('authors', [])),
                paper_data.get('published'),
                json.dumps(paper_data.get('categories', [])),
                paper_data.get('local_path')
            ))

            conn.commit()
            logger.debug(f"Added paper data for collection_id: {collection_id}")
        except Exception as e:
            logger.error(f"Error adding paper: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()

    def add_video(self, collection_id: int, video_data: Dict):
        """Add video-specific data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO videos (collection_id, video_id, channel, duration,
                                   views, thumbnail_url, transcript_available)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                collection_id,
                video_data.get('video_id'),
                video_data.get('author'),
                video_data.get('length', 0),
                video_data.get('views', 0),
                video_data.get('thumbnail_url'),
                bool(video_data.get('transcript'))
            ))

            conn.commit()
            logger.debug(f"Added video data for collection_id: {collection_id}")
        except Exception as e:
            logger.error(f"Error adding video: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()

    def add_podcast(self, collection_id: int, podcast_data: Dict):
        """Add podcast-specific data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO podcasts (collection_id, episode_id, podcast_name,
                                     audio_url, duration)
                VALUES (?, ?, ?, ?, ?)
            """, (
                collection_id,
                podcast_data.get('episode_id'),
                podcast_data.get('podcast_name'),
                podcast_data.get('audio_url'),
                podcast_data.get('duration', 0)
            ))

            conn.commit()
            logger.debug(f"Added podcast data for collection_id: {collection_id}")
        except Exception as e:
            logger.error(f"Error adding podcast: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()

    def mark_as_indexed(self, collection_id: int):
        """Mark a collection item as indexed"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                UPDATE collections SET indexed = 1 WHERE id = ?
            """, (collection_id,))
            conn.commit()
        except Exception as e:
            logger.error(f"Error marking as indexed: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()

    def log_collection_stats(self, content_type: str, query: str,
                           results_count: int, source_api: str):
        """Log collection statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO collection_stats (content_type, query, results_count, source_api)
                VALUES (?, ?, ?, ?)
            """, (content_type, query, results_count, source_api))
            conn.commit()
        except Exception as e:
            logger.error(f"Error logging stats: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()

    def get_all_collections(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Get all collections with pagination"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT * FROM collections
                ORDER BY collection_date DESC
                LIMIT ? OFFSET ?
            """, (limit, offset))

            rows = cursor.fetchall()
            results = []
            for row in rows:
                result = dict(row)
                result['metadata'] = json.loads(result['metadata']) if result['metadata'] else {}
                results.append(result)

            return results
        finally:
            conn.close()

    def get_collections_by_type(self, content_type: str, limit: int = 100) -> List[Dict]:
        """Get collections filtered by type"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT * FROM collections
                WHERE content_type = ?
                ORDER BY collection_date DESC
                LIMIT ?
            """, (content_type, limit))

            rows = cursor.fetchall()
            results = []
            for row in rows:
                result = dict(row)
                result['metadata'] = json.loads(result['metadata']) if result['metadata'] else {}
                results.append(result)

            return results
        finally:
            conn.close()

    def get_collection_with_details(self, collection_id: int) -> Optional[Dict]:
        """Get full collection details including type-specific data"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM collections WHERE id = ?", (collection_id,))
            collection = cursor.fetchone()

            if not collection:
                return None

            result = dict(collection)
            result['metadata'] = json.loads(result['metadata']) if result['metadata'] else {}

            # Get type-specific details
            if result['content_type'] == 'paper':
                cursor.execute("SELECT * FROM papers WHERE collection_id = ?", (collection_id,))
                paper = cursor.fetchone()
                if paper:
                    paper_dict = dict(paper)
                    paper_dict['authors'] = json.loads(paper_dict['authors']) if paper_dict['authors'] else []
                    paper_dict['categories'] = json.loads(paper_dict['categories']) if paper_dict['categories'] else []
                    result['details'] = paper_dict

            elif result['content_type'] == 'video':
                cursor.execute("SELECT * FROM videos WHERE collection_id = ?", (collection_id,))
                video = cursor.fetchone()
                if video:
                    result['details'] = dict(video)

            elif result['content_type'] == 'podcast':
                cursor.execute("SELECT * FROM podcasts WHERE collection_id = ?", (collection_id,))
                podcast = cursor.fetchone()
                if podcast:
                    result['details'] = dict(podcast)

            return result
        finally:
            conn.close()

    def get_statistics(self) -> Dict:
        """Get database statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            stats = {}

            # Total collections by type
            cursor.execute("""
                SELECT content_type, COUNT(*) as count
                FROM collections
                GROUP BY content_type
            """)
            stats['by_type'] = {row[0]: row[1] for row in cursor.fetchall()}

            # Total indexed vs not indexed
            cursor.execute("""
                SELECT indexed, COUNT(*) as count
                FROM collections
                GROUP BY indexed
            """)
            indexed_stats = {row[0]: row[1] for row in cursor.fetchall()}
            stats['indexed'] = indexed_stats.get(1, 0)
            stats['not_indexed'] = indexed_stats.get(0, 0)

            # Recent collections (last 7 days)
            cursor.execute("""
                SELECT COUNT(*) FROM collections
                WHERE collection_date >= datetime('now', '-7 days')
            """)
            stats['recent_7_days'] = cursor.fetchone()[0]

            # Collection stats
            cursor.execute("""
                SELECT content_type, source_api, SUM(results_count) as total
                FROM collection_stats
                GROUP BY content_type, source_api
            """)
            stats['collection_history'] = [
                {'type': row[0], 'source': row[1], 'total': row[2]}
                for row in cursor.fetchall()
            ]

            return stats
        finally:
            conn.close()

    def search_collections(self, query: str, limit: int = 50) -> List[Dict]:
        """Search collections by title or source"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        try:
            search_pattern = f"%{query}%"
            cursor.execute("""
                SELECT * FROM collections
                WHERE title LIKE ? OR source LIKE ?
                ORDER BY collection_date DESC
                LIMIT ?
            """, (search_pattern, search_pattern, limit))

            rows = cursor.fetchall()
            results = []
            for row in rows:
                result = dict(row)
                result['metadata'] = json.loads(result['metadata']) if result['metadata'] else {}
                results.append(result)

            return results
        finally:
            conn.close()
