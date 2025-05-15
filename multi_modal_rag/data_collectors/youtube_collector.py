# multi_modal_rag/data_collectors/youtube_collector.py
import os
from youtube_transcript_api import YouTubeTranscriptApi
from pytube import YouTube, Channel, Playlist
import requests
from typing import List, Dict
import re

class YouTubeLectureCollector:
    """Collect educational content from YouTube"""
    
    def __init__(self, save_dir: str = "data/videos"):
        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)
        
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
        Collect metadata and transcript from a YouTube video
        """
        try:
            yt = YouTube(video_url)
            video_id = self.extract_video_id(video_url)
            
            # Get transcript
            transcript = None
            try:
                transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
                transcript = " ".join([item['text'] for item in transcript_list])
            except:
                transcript = "Transcript not available"
            
            metadata = {
                'video_id': video_id,
                'title': yt.title,
                'description': yt.description,
                'author': yt.author,
                'length': yt.length,
                'views': yt.views,
                'url': video_url,
                'transcript': transcript,
                'thumbnail_url': yt.thumbnail_url,
                'publish_date': str(yt.publish_date) if yt.publish_date else None
            }
            
            return metadata
            
        except Exception as e:
            print(f"Error collecting video {video_url}: {e}")
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
        Search for educational videos using YouTube Data API alternative
        """
        # Using youtube-search-python as a free alternative
        from youtubesearchpython import VideosSearch
        
        search = VideosSearch(f"{query} lecture tutorial course", limit=max_results)
        results = search.result()
        
        videos = []
        for video in results['result']:
            video_data = self.collect_video_metadata(video['link'])
            if video_data:
                videos.append(video_data)
                
        return videos