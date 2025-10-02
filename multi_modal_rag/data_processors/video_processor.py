# multi_modal_rag/data_processors/video_processor.py
from google import genai
from google.genai import types
from PIL import Image
from typing import List, Dict

class VideoProcessor:
    """Process video content for key frames and visual analysis"""

    def __init__(self, gemini_api_key: str):
        # Use newer Gemini SDK
        self.client = genai.Client(api_key=gemini_api_key)
        self.model = "gemini-2.0-flash"  # Free tier model
        
    def extract_key_frames(self, video_url: str, num_frames: int = 10) -> List[Image.Image]:
        """
        Extract key frames from video for analysis
        """
        # For YouTube videos, we'll use thumbnail and transcript
        # For actual video processing, you'd download and process the video
        
        frames = []
        # This is a simplified version - in production, you'd use cv2 to process video
        
        return frames
    
    def analyze_video_content(self, video_metadata: Dict) -> Dict:
        """
        Analyze video content using transcript and metadata
        """
        prompt = f"""
        Analyze this educational video:
        Title: {video_metadata['title']}
        Description: {video_metadata['description']}
        Transcript: {video_metadata['transcript'][:5000]}
        
        Extract:
        1. Main topics covered
        2. Key learning points
        3. Prerequisites needed
        4. Technical concepts explained
        5. Practical applications mentioned
        
        Format as structured JSON.
        """
        
        # Use new SDK pattern
        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt)],
            ),
        ]

        response = self.client.models.generate_content(
            model=self.model,
            contents=contents,
        )
        return response.text