# multi_modal_rag/data_collectors/podcast_collector.py
import os
import feedparser
import requests
from pydub import AudioSegment
import whisper
from typing import List, Dict
from multi_modal_rag.logging_config import get_logger

logger = get_logger(__name__)

class PodcastCollector:
    """Collect educational podcasts"""
    
    def __init__(self, save_dir: str = "data/podcasts"):
        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)
        self.whisper_model = None
        logger.info(f"PodcastCollector initialized with save_dir: {save_dir}")
        
    def get_educational_podcasts(self) -> Dict[str, str]:
        """
        Free educational podcast RSS feeds
        """
        return {
            "Lex Fridman Podcast": "https://lexfridman.com/feed/podcast/",
            "Machine Learning Street Talk": "https://anchor.fm/s/1e4a0eac/podcast/rss",
            "Data Skeptic": "https://dataskeptic.com/feed.rss",
            "The TWIML AI Podcast": "https://twimlai.com/feed/",
            "Learning Machines 101": "http://www.learningmachines101.com/rss",
            "Talking Machines": "http://www.thetalkingmachines.com/rss",
            "AI in Business": "https://feeds.soundcloud.com/users/soundcloud:users:343566194/sounds.rss",
            "Eye on AI": "https://www.eye-on.ai/podcast-rss.xml"
        }
    
    def collect_podcast_episodes(self, rss_url: str, max_episodes: int = 10) -> List[Dict]:
        """
        Collect episodes from a podcast RSS feed
        """
        logger.info(f"Collecting podcast episodes from RSS: {rss_url} (max: {max_episodes})")
        try:
            logger.debug(f"Parsing RSS feed: {rss_url}")
            feed = feedparser.parse(rss_url)

            # Check if feed was parsed successfully
            if hasattr(feed, 'bozo_exception'):
                logger.warning(f"RSS feed parsing warning for {rss_url}: {feed.bozo_exception}")

            if not hasattr(feed, 'entries') or len(feed.entries) == 0:
                logger.error(f"No entries found in RSS feed: {rss_url}")
                return []

            logger.info(f"Found {len(feed.entries)} total episodes in feed")
            episodes = []

            for idx, entry in enumerate(feed.entries[:max_episodes], 1):
                logger.debug(f"Processing episode {idx}/{min(max_episodes, len(feed.entries))}: {entry.get('title', 'Untitled')}")

                episode = {
                    'title': entry.get('title', ''),
                    'description': entry.get('summary', ''),
                    'published': entry.get('published', ''),
                    'link': entry.get('link', ''),
                    'audio_url': None,
                    'transcript': None
                }

                # Find audio URL
                for link in entry.get('links', []):
                    if 'audio' in link.get('type', ''):
                        episode['audio_url'] = link['href']
                        logger.debug(f"Found audio URL in links: {link['href']}")
                        break

                # Alternative: check enclosures
                if not episode['audio_url'] and 'enclosures' in entry:
                    for enclosure in entry.enclosures:
                        if 'audio' in enclosure.get('type', ''):
                            episode['audio_url'] = enclosure['href']
                            logger.debug(f"Found audio URL in enclosures: {enclosure['href']}")
                            break

                if not episode['audio_url']:
                    logger.warning(f"No audio URL found for episode: {episode['title']}")

                episodes.append(episode)

            logger.info(f"Successfully collected {len(episodes)} episodes from {rss_url}")
            return episodes

        except Exception as e:
            logger.error(f"Error collecting podcast episodes from {rss_url}: {type(e).__name__}: {e}", exc_info=True)
            return []
    
    def transcribe_audio(self, audio_url: str, episode_id: str) -> str:
        """
        Download and transcribe podcast audio using Whisper (free)
        """
        logger.info(f"Starting audio transcription for episode: {episode_id}")
        try:
            # Download audio
            audio_path = os.path.join(self.save_dir, f"{episode_id}.mp3")
            logger.debug(f"Downloading audio from {audio_url} to {audio_path}")

            response = requests.get(audio_url, stream=True, timeout=60)
            response.raise_for_status()

            total_size = 0
            with open(audio_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    total_size += len(chunk)

            logger.info(f"Downloaded {total_size / (1024*1024):.2f} MB audio file")

            # Load Whisper model (first time only)
            if self.whisper_model is None:
                logger.info("Loading Whisper model (this may take a moment on first use)...")
                self.whisper_model = whisper.load_model("base")
                logger.info("Whisper model loaded successfully")

            # Transcribe
            logger.info("Transcribing audio (this may take several minutes)...")
            result = self.whisper_model.transcribe(audio_path)
            transcript_text = result["text"]

            logger.info(f"Successfully transcribed audio ({len(transcript_text)} chars) for episode: {episode_id}")
            return transcript_text

        except requests.exceptions.RequestException as e:
            logger.error(f"Error downloading audio from {audio_url}: {type(e).__name__}: {e}", exc_info=True)
            return None
        except Exception as e:
            logger.error(f"Error transcribing audio for episode {episode_id}: {type(e).__name__}: {e}", exc_info=True)
            return None