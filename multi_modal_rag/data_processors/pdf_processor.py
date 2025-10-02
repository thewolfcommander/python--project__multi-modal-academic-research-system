# multi_modal_rag/data_processors/pdf_processor.py
import os
from google import genai
from google.genai import types
from pypdf import PdfReader
import base64
from PIL import Image
import fitz  # PyMuPDF for better image extraction
from typing import List, Dict
import io

class PDFProcessor:
    """Process PDFs with diagrams using Gemini"""

    def __init__(self, gemini_api_key: str):
        # Use newer Gemini SDK
        self.client = genai.Client(api_key=gemini_api_key)
        # Use free Gemini models - flash-lite is the fastest free tier
        self.text_model = "gemini-2.0-flash"
        self.vision_model = "gemini-2.0-flash-exp"  # Supports vision
        
    def extract_text_and_images(self, pdf_path: str) -> Dict:
        """
        Extract text and images from PDF
        """
        doc = fitz.open(pdf_path)
        
        content = {
            'text_pages': [],
            'images': [],
            'combined_text': "",
            'metadata': {
                'page_count': len(doc),
                'title': doc.metadata.get('title', ''),
                'author': doc.metadata.get('author', '')
            }
        }
        
        for page_num, page in enumerate(doc):
            # Extract text
            text = page.get_text()
            content['text_pages'].append({
                'page': page_num + 1,
                'text': text
            })
            content['combined_text'] += f"\n[Page {page_num + 1}]\n{text}"
            
            # Extract images
            image_list = page.get_images(full=True)
            
            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                
                # Convert to PIL Image
                image = Image.open(io.BytesIO(image_bytes))
                
                content['images'].append({
                    'page': page_num + 1,
                    'index': img_index,
                    'image': image,
                    'bytes': image_bytes
                })
        
        doc.close()
        return content
    
    def analyze_with_gemini(self, pdf_content: Dict) -> Dict:
        """
        Use Gemini to understand PDF content including diagrams
        """
        analysis = {
            'summary': None,
            'key_concepts': [],
            'diagram_descriptions': [],
            'extracted_equations': [],
            'citations': []
        }

        try:
            # Analyze text content
            text_prompt = f"""
            Analyze this academic paper and extract:
            1. A comprehensive summary (2-3 sentences)
            2. Key concepts and definitions (list 3-5 main concepts)
            3. Any references mentioned

            Paper content:
            {pdf_content['combined_text'][:10000]}

            Provide response in clear sections.
            """

            # Use new SDK pattern
            contents = [
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=text_prompt)],
                ),
            ]

            response = self.client.models.generate_content(
                model=self.text_model,
                contents=contents,
            )
            analysis['summary'] = response.text

            # Extract key concepts from response (simple extraction)
            if response.text:
                # Simple extraction - split by common delimiters
                lines = response.text.split('\n')
                for line in lines:
                    if any(keyword in line.lower() for keyword in ['concept:', 'key:', '-', '•']):
                        concept = line.strip('- •*').strip()
                        if concept and len(concept) < 100:
                            analysis['key_concepts'].append(concept)

            # Analyze images/diagrams
            for img_data in pdf_content['images'][:5]:  # Process first 5 images
                try:
                    image_prompt = """
                    Describe this diagram/figure from an academic paper:
                    1. What type of diagram is it? (flowchart, graph, architecture, etc.)
                    2. What are the key components?
                    3. What concept does it illustrate?
                    4. Extract any text or labels from the image
                    """

                    # Convert PIL image to bytes for the new SDK
                    img_bytes = io.BytesIO()
                    img_data['image'].save(img_bytes, format='PNG')
                    img_bytes = img_bytes.getvalue()

                    # Use new SDK pattern for vision
                    contents = [
                        types.Content(
                            role="user",
                            parts=[
                                types.Part.from_text(text=image_prompt),
                                types.Part.from_bytes(
                                    data=img_bytes,
                                    mime_type="image/png"
                                ),
                            ],
                        ),
                    ]

                    img_response = self.client.models.generate_content(
                        model=self.vision_model,
                        contents=contents,
                    )

                    analysis['diagram_descriptions'].append({
                        'page': img_data['page'],
                        'description': img_response.text
                    })
                except Exception as e:
                    print(f"Warning: Failed to analyze image on page {img_data['page']}: {e}")
                    continue

        except Exception as e:
            print(f"Error analyzing PDF content: {e}")
            analysis['summary'] = pdf_content['combined_text'][:500]  # Fallback to raw text

        return analysis