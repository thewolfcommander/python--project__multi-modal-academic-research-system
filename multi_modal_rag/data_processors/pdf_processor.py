# multi_modal_rag/data_processors/pdf_processor.py
import google.generativeai as genai
from pypdf import PdfReader
import base64
from PIL import Image
import fitz  # PyMuPDF for better image extraction
from typing import List, Dict
import io

class PDFProcessor:
    """Process PDFs with diagrams using Gemini"""
    
    def __init__(self, gemini_api_key: str):
        genai.configure(api_key=gemini_api_key)
        # Use gemini-pro for text, gemini-pro-vision for images
        self.text_model = genai.GenerativeModel('gemini-pro')
        self.vision_model = genai.GenerativeModel('gemini-pro-vision')
        
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

            text_response = self.text_model.generate_content(text_prompt)
            analysis['summary'] = text_response.text

            # Extract key concepts from response (simple extraction)
            if text_response.text:
                # Simple extraction - split by common delimiters
                lines = text_response.text.split('\n')
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

                    img_response = self.vision_model.generate_content([image_prompt, img_data['image']])

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