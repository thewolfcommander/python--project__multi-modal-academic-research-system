# multi_modal_rag/data_collectors/podcast_collector.py
import os
import feedparser
import requests
from pydub import AudioSegment
import whisper
from typing import List, Dict

class PodcastCollector:
    """Collect educational podcasts"""
    
    def __init__(self, save_dir: str = "data/podcasts"):
        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)
        self.whisper_model = None
        
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
        feed = feedparser.parse(rss_url)
        episodes = []
        
        for entry in feed.entries[:max_episodes]:
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
                    break
            
            # Alternative: check enclosures
            if not episode['audio_url'] and 'enclosures' in entry:
                for enclosure in entry.enclosures:
                    if 'audio' in enclosure.get('type', ''):
                        episode['audio_url'] = enclosure['href']
                        break
            
            episodes.append(episode)
            
        return episodes
    
    def transcribe_audio(self, audio_url: str, episode_id: str) -> str:
        """
        Download and transcribe podcast audio using Whisper (free)
        """
        try:
            # Download audio
            audio_path = os.path.join(self.save_dir, f"{episode_id}.mp3")
            
            response = requests.get(audio_url, stream=True)
            with open(audio_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Load Whisper model (first time only)
            if self.whisper_model is None:
                self.whisper_model = whisper.load_model("base")
            
            # Transcribe
            result = self.whisper_model.transcribe(audio_path)
            
            return result["text"]
            
        except Exception as e:
            print(f"Error transcribing audio: {e}")
            return None