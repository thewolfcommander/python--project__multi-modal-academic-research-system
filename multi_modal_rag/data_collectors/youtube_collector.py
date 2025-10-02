# multi_modal_rag/data_collectors/youtube_collector.py
import os
from youtube_transcript_api import YouTubeTranscriptApi
from typing import List, Dict
import re
from multi_modal_rag.logging_config import get_logger

logger = get_logger(__name__)

class YouTubeLectureCollector:
    """Collect educational content from YouTube"""
    
    def __init__(self, save_dir: str = "data/videos"):
        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)
        logger.info(f"YouTubeLectureCollector initialized with save_dir: {save_dir}")
        
    def get_educational_channels(self) -> List[str]:
        """
        Free educational YouTube channels
        """
        return [
            "https://www.youtube.com/@mitocw",  # MIT OpenCourseWare
            "https://www.youtube.com/@stanford",  # Stanford
            "https://www.youtube.com/@GoogleDeepMind",  # DeepMind
            "https://www.youtube.com/@OpenAI",  # OpenAI
            "https://www.youtube.com/@khanacademy",  # Khan Academy
            "https://www.youtube.com/@3blue1brown",  # 3Blue1Brown
            "https://www.youtube.com/@TwoMinutePapers",  # Two Minute Papers
            "https://www.youtube.com/@YannicKilcher",  # Yannic Kilcher
            "https://www.youtube.com/@CSdojo",  # CS Dojo
        ]
    
    def collect_video_metadata(self, video_url: str) -> Dict:
        """
        Collect metadata and transcript from a YouTube video using yt-dlp
        """
        logger.info(f"Attempting to collect metadata for video: {video_url}")
        try:
            import yt_dlp

            video_id = self.extract_video_id(video_url)
            logger.debug(f"Extracted video ID: {video_id}")

            # Get video metadata using yt-dlp
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,  # Get full metadata
            }

            logger.debug(f"Fetching metadata with yt-dlp for: {video_url}")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)

            # Get transcript
            transcript = None
            try:
                logger.debug(f"Fetching transcript for video ID: {video_id}")
                transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
                transcript = " ".join([item['text'] for item in transcript_list])
                logger.info(f"Successfully retrieved transcript ({len(transcript)} chars)")
            except Exception as transcript_error:
                transcript = "Transcript not available"
                logger.warning(f"Transcript not available for video {video_id}: {transcript_error}")

            metadata = {
                'video_id': video_id,
                'title': info.get('title', 'Unknown'),
                'description': info.get('description', ''),
                'author': info.get('uploader', info.get('channel', 'Unknown')),
                'length': info.get('duration', 0),
                'views': info.get('view_count', 0),
                'url': video_url,
                'transcript': transcript,
                'thumbnail_url': info.get('thumbnail', ''),
                'publish_date': info.get('upload_date', None)
            }

            logger.info(f"Successfully collected metadata for: {metadata['title']} by {metadata['author']}")
            return metadata

        except ImportError:
            logger.error("yt-dlp is not installed. Please run: pip install yt-dlp")
            print("⚠️  yt-dlp is not installed. Run: pip install yt-dlp")
            return None
        except Exception as e:
            logger.error(f"Error collecting video {video_url}: {type(e).__name__}: {e}", exc_info=True)
            return None
    
    def extract_video_id(self, url: str) -> str:
        """Extract video ID from YouTube URL"""
        patterns = [
            r'(?:youtube\.com\/watch\?v=)([\w-]+)',
            r'(?:youtu\.be\/)([\w-]+)',
            r'(?:youtube\.com\/embed\/)([\w-]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def search_youtube_lectures(self, query: str, max_results: int = 50) -> List[Dict]:
        """
        Search for educational videos using yt-dlp (robust, maintained alternative)
        """
        logger.info(f"Starting YouTube search for query: '{query}' with max_results: {max_results}")
        try:
            import yt_dlp

            search_query = f"ytsearch{max_results}:{query} lecture tutorial course"
            logger.debug(f"Using yt-dlp search query: '{search_query}'")

            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,  # Don't download, just get metadata
                'default_search': 'ytsearch',
            }

            videos = []
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                logger.debug("Executing yt-dlp search...")
                search_results = ydl.extract_info(search_query, download=False)

                if not search_results or 'entries' not in search_results:
                    logger.warning("No search results returned from yt-dlp")
                    return []

                logger.info(f"yt-dlp returned {len(search_results['entries'])} results")

                for idx, entry in enumerate(search_results['entries'], 1):
                    if not entry:
                        continue

                    video_url = f"https://www.youtube.com/watch?v={entry['id']}"
                    logger.debug(f"Processing video {idx}/{len(search_results['entries'])}: {video_url}")

                    video_data = self.collect_video_metadata(video_url)
                    if video_data:
                        videos.append(video_data)
                    else:
                        logger.warning(f"Failed to collect metadata for video {idx}")

            logger.info(f"Successfully collected {len(videos)} videos")
            return videos

        except ImportError:
            logger.error("yt-dlp is not installed. Please run: pip install yt-dlp")
            print("⚠️  yt-dlp is not installed. Run: pip install yt-dlp")
            return []
        except Exception as e:
            logger.error(f"Error searching YouTube lectures for query '{query}': {type(e).__name__}: {e}", exc_info=True)
            return []