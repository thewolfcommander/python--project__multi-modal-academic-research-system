# Data Processors Module

## Overview

The Data Processors module handles extraction and analysis of content from collected academic materials. It uses Google Gemini's multimodal AI capabilities to extract text, analyze diagrams, and understand video content.

## Module Architecture

```
multi_modal_rag/data_processors/
├── pdf_processor.py      # PDF text/image extraction and analysis
└── video_processor.py    # Video content analysis
```

---

## PDFProcessor

**File**: `multi_modal_rag/data_processors/pdf_processor.py`

### Class Overview

Processes PDF documents to extract text, images, and diagrams. Uses Google Gemini Vision to analyze visual content and generate textual descriptions that can be indexed and searched.

### Initialization

```python
from multi_modal_rag.data_processors import PDFProcessor

processor = PDFProcessor(gemini_api_key="YOUR_API_KEY")
```

**Parameters**:
- `gemini_api_key` (str): Google Gemini API key from https://makersuite.google.com/app/apikey

**Models Used**:
- `gemini-2.0-flash`: Fast text analysis model (free tier)
- `gemini-2.0-flash-exp`: Vision model for diagram analysis (free tier)

### Methods

#### `extract_text_and_images(pdf_path: str) -> Dict`

Extracts all text and images from a PDF document using PyMuPDF (fitz).

**Parameters**:
- `pdf_path` (str): Absolute path to PDF file

**Returns**: Dictionary with extracted content:

```python
{
    'text_pages': List[Dict[str, Any]],  # Text content per page
    'images': List[Dict[str, Any]],      # Extracted images
    'combined_text': str,                # All text concatenated
    'metadata': {
        'page_count': int,
        'title': str,
        'author': str
    }
}
```

**Detailed Structure**:

```python
# text_pages structure
text_pages = [
    {
        'page': 1,           # Page number (1-indexed)
        'text': str          # Extracted text from page
    },
    # ... more pages
]

# images structure
images = [
    {
        'page': int,         # Page number where image appears
        'index': int,        # Index of image on that page
        'image': PIL.Image,  # PIL Image object
        'bytes': bytes       # Raw image bytes
    },
    # ... more images
]

# combined_text format
combined_text = """
[Page 1]
Text from page 1...

[Page 2]
Text from page 2...
"""
```

**Example**:

```python
processor = PDFProcessor(gemini_api_key="your_key")
content = processor.extract_text_and_images("papers/arxiv_paper.pdf")

print(f"Total pages: {content['metadata']['page_count']}")
print(f"Document title: {content['metadata']['title']}")
print(f"Images found: {len(content['images'])}")

# Access text from specific page
first_page_text = content['text_pages'][0]['text']
print(f"First page: {first_page_text[:500]}...")

# Access images
for img_data in content['images']:
    print(f"Image on page {img_data['page']}: {img_data['image'].size}")
```

**Technical Details**:
- Uses PyMuPDF (fitz) for robust PDF parsing
- Extracts embedded images in original format
- Preserves image metadata (page location, index)
- Handles encrypted PDFs (if not password-protected)
- Efficiently processes large PDFs

---

#### `analyze_with_gemini(pdf_content: Dict) -> Dict`

Analyzes extracted PDF content using Google Gemini AI for deeper understanding.

**Parameters**:
- `pdf_content` (Dict): Output from `extract_text_and_images()`

**Returns**: Analysis dictionary:

```python
{
    'summary': str,                          # AI-generated summary
    'key_concepts': List[str],              # Extracted concepts
    'diagram_descriptions': List[Dict],      # Visual content analysis
    'extracted_equations': List[str],        # Mathematical equations (reserved)
    'citations': List[str]                   # Referenced papers (reserved)
}
```

**Detailed Structure**:

```python
# diagram_descriptions structure
diagram_descriptions = [
    {
        'page': int,             # Page number
        'description': str       # AI-generated description
    },
    # ... more diagrams
]

# key_concepts extraction
key_concepts = [
    "Transformer architecture",
    "Self-attention mechanism",
    "Positional encoding",
    # ... more concepts
]
```

**Example**:

```python
processor = PDFProcessor(gemini_api_key="your_key")

# Step 1: Extract content
pdf_content = processor.extract_text_and_images("papers/transformer_paper.pdf")

# Step 2: Analyze with AI
analysis = processor.analyze_with_gemini(pdf_content)

# View summary
print("Summary:")
print(analysis['summary'])

# View key concepts
print("\nKey Concepts:")
for concept in analysis['key_concepts']:
    print(f"  - {concept}")

# View diagram descriptions
print("\nDiagrams:")
for diagram in analysis['diagram_descriptions']:
    print(f"Page {diagram['page']}: {diagram['description']}")
```

**AI Analysis Workflow**:

1. **Text Analysis** (First 10,000 characters):
   - Generates comprehensive 2-3 sentence summary
   - Extracts 3-5 main concepts and definitions
   - Identifies key references (planned feature)

2. **Visual Analysis** (First 5 images):
   - Identifies diagram type (flowchart, graph, architecture, etc.)
   - Lists key components visible in diagram
   - Explains the concept the diagram illustrates
   - Extracts any text or labels from the image

**Prompt Template for Text**:

```
Analyze this academic paper and extract:
1. A comprehensive summary (2-3 sentences)
2. Key concepts and definitions (list 3-5 main concepts)
3. Any references mentioned

Paper content:
{first_10000_chars}

Provide response in clear sections.
```

**Prompt Template for Images**:

```
Describe this diagram/figure from an academic paper:
1. What type of diagram is it? (flowchart, graph, architecture, etc.)
2. What are the key components?
3. What concept does it illustrate?
4. Extract any text or labels from the image
```

**Example Output**:

```python
{
    'summary': 'This paper introduces the Transformer architecture, a novel neural network model that relies entirely on attention mechanisms. The model achieves state-of-the-art results on machine translation tasks while being more parallelizable than recurrent architectures.',

    'key_concepts': [
        'Self-attention mechanism',
        'Multi-head attention',
        'Positional encoding',
        'Encoder-decoder architecture',
        'Layer normalization'
    ],

    'diagram_descriptions': [
        {
            'page': 3,
            'description': 'This is an architecture diagram showing the Transformer model structure. The diagram shows two main components: an encoder stack on the left and decoder stack on the right. Key components include multi-head attention layers, feed-forward networks, and residual connections. The diagram labels show N=6 layers in each stack.'
        },
        {
            'page': 5,
            'description': 'This is a flowchart illustrating the scaled dot-product attention mechanism. The diagram shows matrix multiplication between Query (Q) and Key (K), followed by scaling, softmax, and multiplication with Value (V). The formula "Attention(Q,K,V) = softmax(QK^T/√d_k)V" is visible.'
        }
    ],

    'extracted_equations': [],  # Reserved for future enhancement
    'citations': []             # Reserved for future enhancement
}
```

**Error Handling**:
- If Gemini API fails, returns raw text (first 500 chars) as summary
- Logs warnings for failed image analyses but continues processing
- Continues to next image if one fails (doesn't halt entire analysis)

**Performance Notes**:
- Text analysis: ~2-5 seconds
- Per-image analysis: ~3-7 seconds
- Total time for paper with 5 images: ~30-40 seconds
- Uses free tier Gemini models (no cost)

---

## VideoProcessor

**File**: `multi_modal_rag/data_processors/video_processor.py`

### Class Overview

Processes video content, primarily educational YouTube videos, by analyzing metadata, descriptions, and transcripts using Google Gemini AI.

### Initialization

```python
from multi_modal_rag.data_processors import VideoProcessor

processor = VideoProcessor(gemini_api_key="YOUR_API_KEY")
```

**Parameters**:
- `gemini_api_key` (str): Google Gemini API key

**Model Used**:
- `gemini-2.0-flash`: Fast text analysis (free tier)

### Methods

#### `extract_key_frames(video_url: str, num_frames: int = 10) -> List[Image.Image]`

Extracts key frames from video for visual analysis.

**Status**: Simplified implementation (placeholder)

**Parameters**:
- `video_url` (str): Video URL
- `num_frames` (int, optional): Number of frames to extract. Default: 10

**Returns**: List of PIL Image objects (currently empty list)

**Note**: Full implementation would require:
```python
import cv2

def extract_key_frames(self, video_path: str, num_frames: int = 10):
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    interval = total_frames // num_frames

    frames = []
    for i in range(num_frames):
        cap.set(cv2.CAP_PROP_POS_FRAMES, i * interval)
        ret, frame = cap.read()
        if ret:
            image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            frames.append(image)

    cap.release()
    return frames
```

---

#### `analyze_video_content(video_metadata: Dict) -> Dict`

Analyzes video content using metadata, description, and transcript.

**Parameters**:
- `video_metadata` (Dict): Video data from YouTubeLectureCollector:

```python
{
    'title': str,
    'description': str,
    'transcript': str,
    'author': str,
    'length': int,
    'views': int,
    # ... other metadata
}
```

**Returns**: String containing structured analysis (JSON format intended)

**Example**:

```python
from multi_modal_rag.data_collectors import YouTubeLectureCollector
from multi_modal_rag.data_processors import VideoProcessor

# Collect video metadata
collector = YouTubeLectureCollector()
video_data = collector.collect_video_metadata(
    "https://www.youtube.com/watch?v=aircAruvnKk"
)

# Analyze content
processor = VideoProcessor(gemini_api_key="your_key")
analysis = processor.analyze_video_content(video_data)

print(analysis)
```

**Analysis Prompt Template**:

```
Analyze this educational video:
Title: {title}
Description: {description}
Transcript: {first_5000_chars_of_transcript}

Extract:
1. Main topics covered
2. Key learning points
3. Prerequisites needed
4. Technical concepts explained
5. Practical applications mentioned

Format as structured JSON.
```

**Example Analysis Output**:

```json
{
    "main_topics": [
        "Neural networks fundamentals",
        "Gradient descent optimization",
        "Backpropagation algorithm"
    ],
    "key_learning_points": [
        "Understanding how neurons process information",
        "Relationship between weights and predictions",
        "How networks learn from errors"
    ],
    "prerequisites": [
        "Basic calculus (derivatives)",
        "Linear algebra (matrix multiplication)",
        "Python programming"
    ],
    "technical_concepts": [
        "Activation functions",
        "Loss functions",
        "Learning rate",
        "Forward and backward passes"
    ],
    "practical_applications": [
        "Image classification",
        "Natural language processing",
        "Recommendation systems"
    ]
}
```

**Limitations**:
- Uses first 5,000 characters of transcript (to fit within context limits)
- Returns text response (JSON parsing needed by caller)
- Does not analyze actual video frames (uses transcript only)

---

## Integration Workflow

### Complete PDF Processing Pipeline

```python
from multi_modal_rag.data_collectors import AcademicPaperCollector
from multi_modal_rag.data_processors import PDFProcessor

# Step 1: Collect papers
collector = AcademicPaperCollector()
papers = collector.collect_arxiv_papers("attention is all you need", max_results=1)

# Step 2: Process PDFs
processor = PDFProcessor(gemini_api_key="your_key")

for paper in papers:
    print(f"\nProcessing: {paper['title']}")

    # Extract content
    content = processor.extract_text_and_images(paper['local_path'])
    print(f"  Pages: {content['metadata']['page_count']}")
    print(f"  Images: {len(content['images'])}")

    # Analyze with AI
    analysis = processor.analyze_with_gemini(content)

    # Prepare for indexing
    indexable_doc = {
        'title': paper['title'],
        'authors': paper['authors'],
        'abstract': paper['abstract'],
        'content': content['combined_text'],
        'summary': analysis['summary'],
        'key_concepts': analysis['key_concepts'],
        'diagram_descriptions': [
            d['description'] for d in analysis['diagram_descriptions']
        ],
        'publication_date': paper['published'],
        'content_type': 'paper'
    }

    # Ready to index in OpenSearch
    print(f"  Key concepts: {', '.join(analysis['key_concepts'][:3])}")
```

### Complete Video Processing Pipeline

```python
from multi_modal_rag.data_collectors import YouTubeLectureCollector
from multi_modal_rag.data_processors import VideoProcessor

# Step 1: Collect videos
collector = YouTubeLectureCollector()
videos = collector.search_youtube_lectures("neural networks", max_results=3)

# Step 2: Process videos
processor = VideoProcessor(gemini_api_key="your_key")

for video in videos:
    if video['transcript'] != "Transcript not available":
        print(f"\nProcessing: {video['title']}")

        # Analyze content
        analysis = processor.analyze_video_content(video)

        # Prepare for indexing
        indexable_doc = {
            'title': video['title'],
            'authors': [video['author']],
            'content': video['description'],
            'transcript': video['transcript'],
            'analysis': analysis,  # Structured analysis from Gemini
            'url': video['url'],
            'content_type': 'video'
        }

        print(f"  Duration: {video['length']} seconds")
        print(f"  Transcript length: {len(video['transcript'])} chars")
```

---

## Gemini Vision Integration

### How Diagram Analysis Works

The PDF processor uses Gemini's vision capabilities to "see" and understand diagrams:

1. **Image Extraction**: PyMuPDF extracts images as PIL Image objects
2. **Image Conversion**: PIL images converted to PNG bytes
3. **Multimodal Prompt**: Image + text prompt sent to Gemini Vision
4. **Description Generation**: AI generates textual description
5. **Indexing**: Description stored as searchable text

**Code Flow**:

```python
# Extract image from PDF (PyMuPDF)
image_bytes = doc.extract_image(xref)["image"]
image = Image.open(io.BytesIO(image_bytes))

# Convert to PNG for Gemini
img_bytes = io.BytesIO()
image.save(img_bytes, format='PNG')
img_bytes = img_bytes.getvalue()

# Create multimodal content
contents = [
    types.Content(
        role="user",
        parts=[
            types.Part.from_text(text=image_prompt),
            types.Part.from_bytes(data=img_bytes, mime_type="image/png")
        ]
    )
]

# Get AI description
response = self.client.models.generate_content(
    model=self.vision_model,
    contents=contents
)

description = response.text
```

### Why This Matters

Traditional RAG systems can only search text. By converting diagrams to text descriptions:

1. **Searchability**: Users can find papers by describing diagrams
   - Query: "architecture diagram with encoder and decoder"
   - Matches: Transformer paper (from diagram description)

2. **Understanding**: AI can explain complex visual concepts
   - Diagram → "This shows a neural network with 3 layers..."

3. **Citation**: LLM can reference visual evidence
   - Answer: "As shown in the attention mechanism diagram [Paper, 2023]..."

---

## Gemini SDK Usage

### New SDK Pattern (2024)

The processors use the latest Gemini SDK:

```python
from google import genai
from google.genai import types

# Initialize client
client = genai.Client(api_key="YOUR_KEY")

# Text generation
contents = [
    types.Content(
        role="user",
        parts=[types.Part.from_text(text="Your prompt")]
    )
]

response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=contents
)

print(response.text)

# Vision (multimodal)
contents = [
    types.Content(
        role="user",
        parts=[
            types.Part.from_text(text="Describe this image"),
            types.Part.from_bytes(data=image_bytes, mime_type="image/png")
        ]
    )
]

response = client.models.generate_content(
    model="gemini-2.0-flash-exp",
    contents=contents
)
```

### Free Tier Limits

- **gemini-2.0-flash**: 15 requests/minute, 1 million tokens/minute
- **gemini-2.0-flash-exp**: Same limits
- **Rate limiting**: Not implemented (Gemini handles server-side)

---

## Error Handling

### PDF Processing Errors

```python
try:
    content = processor.extract_text_and_images("paper.pdf")
except Exception as e:
    print(f"Extraction failed: {e}")
    # Handle: file not found, corrupt PDF, permission error
```

**Common Issues**:
- **File not found**: Check path is absolute and file exists
- **Corrupt PDF**: Try redownloading or using different source
- **Encrypted PDF**: Password-protected PDFs not supported
- **Memory error**: Large PDFs may need streaming/chunking

### Gemini API Errors

```python
try:
    analysis = processor.analyze_with_gemini(content)
except Exception as e:
    print(f"Analysis failed: {e}")
    # Fallback: use raw text
    analysis = {
        'summary': content['combined_text'][:500],
        'key_concepts': [],
        'diagram_descriptions': []
    }
```

**Common Issues**:
- **API key invalid**: Check key from https://makersuite.google.com
- **Rate limit exceeded**: Wait and retry (15 req/min limit)
- **Content too long**: Truncate to 10,000 chars (already implemented)
- **Image too large**: Resize before sending (not currently implemented)

---

## Performance Optimization

### Processing Speed

**PDF Processing** (100-page paper with 10 images):
- Text extraction: ~2-5 seconds (PyMuPDF)
- Text analysis: ~3-5 seconds (Gemini)
- Image analysis (10 images): ~30-50 seconds (Gemini Vision)
- **Total**: ~35-60 seconds

**Video Processing**:
- Transcript analysis: ~3-7 seconds (Gemini)
- **Total**: ~3-7 seconds (no video frame analysis yet)

### Optimization Tips

1. **Limit Images**: Process first 5 images only (implemented)
   ```python
   for img_data in pdf_content['images'][:5]:  # Limit to 5
   ```

2. **Batch Processing**: Process multiple papers in parallel
   ```python
   from concurrent.futures import ThreadPoolExecutor

   with ThreadPoolExecutor(max_workers=3) as executor:
       futures = [executor.submit(process_pdf, path) for path in pdf_paths]
       results = [f.result() for f in futures]
   ```

3. **Cache Results**: Store analysis to avoid reprocessing
   ```python
   import json

   cache_file = f"cache/{paper_id}_analysis.json"
   if os.path.exists(cache_file):
       with open(cache_file) as f:
           analysis = json.load(f)
   else:
       analysis = processor.analyze_with_gemini(content)
       with open(cache_file, 'w') as f:
           json.dump(analysis, f)
   ```

4. **Truncate Transcripts**: Limit to 5,000 chars (implemented)
   ```python
   transcript[:5000]  # First 5K characters only
   ```

---

## Dependencies

```python
# pdf_processor.py
from google import genai
from google.genai import types
from pypdf import PdfReader
from PIL import Image
import fitz  # PyMuPDF

# video_processor.py
from google import genai
from google.genai import types
from PIL import Image
```

**Installation**:
```bash
pip install google-generativeai pypdf pillow pymupdf
```

---

## Troubleshooting

### Issue: Gemini API authentication fails

**Error**: `Invalid API key`

**Solution**:
1. Get API key from https://makersuite.google.com/app/apikey
2. Ensure key is not expired
3. Check for extra spaces in key string

### Issue: PDF extraction returns empty text

**Cause**: Scanned PDF (images of text, not real text)

**Solution**: Use OCR (not currently implemented):
```python
from pdf2image import convert_from_path
import pytesseract

images = convert_from_path('scanned.pdf')
text = pytesseract.image_to_string(images[0])
```

### Issue: Gemini returns incomplete JSON

**Cause**: Model doesn't always format as JSON

**Solution**: Parse flexibly or use prompt engineering:
```python
prompt = """
Analyze this video. Respond ONLY with valid JSON in this exact format:
{
    "main_topics": ["topic1", "topic2"],
    "key_learning_points": ["point1", "point2"]
}
"""
```

### Issue: Image analysis fails silently

**Cause**: Exception caught and logged, but processing continues

**Solution**: Check logs for specific error:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
# Will show: "Warning: Failed to analyze image on page X: <error>"
```

---

## Future Enhancements

### Planned Features

1. **Equation Extraction**: Parse LaTeX equations from PDFs
2. **Citation Parsing**: Extract and link paper references
3. **Video Frame Analysis**: Analyze actual video frames (not just transcript)
4. **Table Extraction**: Parse tables from PDFs into structured data
5. **OCR Integration**: Handle scanned PDFs
6. **Audio Analysis**: Process video audio separately from transcript

### Extension Points

```python
# Add equation extraction
def extract_equations(self, pdf_content: Dict) -> List[str]:
    """Extract LaTeX equations using regex or Gemini"""
    pass

# Add table parsing
def extract_tables(self, pdf_content: Dict) -> List[Dict]:
    """Parse tables from PDF"""
    pass

# Add OCR for scanned PDFs
def ocr_scanned_pdf(self, pdf_path: str) -> str:
    """Use OCR for image-based PDFs"""
    pass
```
