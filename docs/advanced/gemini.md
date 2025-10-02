# Gemini Integration Deep Dive

Comprehensive guide to Google Gemini integration in the Multi-Modal Academic Research System.

## Table of Contents

- [Overview](#overview)
- [Gemini Models](#gemini-models)
- [Current Usage](#current-usage)
- [API Configuration](#api-configuration)
- [Advanced Features](#advanced-features)
- [Optimization Strategies](#optimization-strategies)
- [Error Handling](#error-handling)
- [Best Practices](#best-practices)

---

## Overview

### What is Gemini?

Gemini is Google's family of multimodal large language models that can:
- Generate text
- Understand images
- Analyze videos
- Process multiple modalities simultaneously

### Why Gemini for This System?

**Advantages**:
1. **Multimodal**: Can analyze both text and images (for PDF diagrams)
2. **Free tier**: 60 requests/minute free
3. **Quality**: State-of-the-art performance
4. **Long context**: Up to 1M tokens (Gemini 1.5 Pro)
5. **No subscription**: No monthly costs

**Current uses**:
- Generate research answers from retrieved context
- Analyze PDF diagrams and figures
- Extract key concepts from papers
- Summarize video content

---

## Gemini Models

### Available Models

#### Gemini 1.5 Flash (Current Default for Text)

```python
model = genai.GenerativeModel('gemini-1.5-flash')
```

**Specifications**:
- **Context window**: 1M tokens
- **Speed**: Fast (optimized for speed)
- **Cost**: Free tier: 15 RPM, 1M TPM
- **Best for**: Question answering, summarization, chat

**Characteristics**:
- Multimodal (text, images, video)
- Fast inference
- Good quality vs speed tradeoff
- Lower cost than Pro

#### Gemini 1.5 Pro

```python
model = genai.GenerativeModel('gemini-1.5-pro')
```

**Specifications**:
- **Context window**: 2M tokens
- **Speed**: Slower than Flash
- **Cost**: Free tier: 2 RPM
- **Best for**: Complex reasoning, detailed analysis

**Characteristics**:
- Highest quality
- Better at complex tasks
- Larger context window
- More expensive (rate-limited on free tier)

#### Gemini Pro Vision (Legacy)

```python
model = genai.GenerativeModel('gemini-pro-vision')
```

**Note**: Being replaced by Gemini 1.5 models which are fully multimodal.

### Model Comparison

| Feature | Flash | Pro | Pro Vision |
|---------|-------|-----|------------|
| Text generation | Excellent | Excellent | Good |
| Image understanding | Excellent | Excellent | Excellent |
| Video understanding | Yes | Yes | Yes |
| Speed | Fast | Medium | Medium |
| Context length | 1M tokens | 2M tokens | ~16K tokens |
| Free tier RPM | 15 | 2 | 2 |
| Best for | Production | Complex tasks | Image-only |

---

## Current Usage

### 1. Question Answering (research_orchestrator.py)

```python
from langchain_google_genai import ChatGoogleGenerativeAI

# Initialize model
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.7,
    max_tokens=2048
)

# Create prompt with context
prompt = f"""
You are a research assistant. Answer the question based on the provided context.

Context:
{retrieved_documents}

Question: {user_question}

Provide a detailed answer with citations [1], [2], etc.
"""

# Generate response
response = llm.invoke(prompt)
```

**Parameters explained**:
- `temperature`: Controls randomness (0 = deterministic, 1 = creative)
  - Use 0.1-0.3 for factual answers
  - Use 0.7-0.9 for creative tasks
- `max_tokens`: Maximum response length
- `top_p`: Nucleus sampling (alternative to temperature)
- `top_k`: Top-k sampling (limits vocabulary)

### 2. Vision Analysis (pdf_processor.py)

```python
import google.generativeai as genai
from PIL import Image

# Configure API
genai.configure(api_key=api_key)

# Initialize vision model
vision_model = genai.GenerativeModel('gemini-1.5-flash')

# Analyze image
image = Image.open("diagram.png")

prompt = """
Describe this scientific diagram in detail.
Include:
- Main components
- Relationships shown
- Key concepts
- Any labels or annotations
"""

response = vision_model.generate_content([prompt, image])
description = response.text
```

**Use cases**:
- Extract information from diagrams
- Describe charts and graphs
- Read text from images (OCR alternative)
- Analyze experimental setups

### 3. Content Extraction

```python
def extract_key_concepts(text, max_concepts=10):
    """Extract key concepts using Gemini."""

    prompt = f"""
    Extract the {max_concepts} most important concepts from this text.
    Return as a comma-separated list.

    Text: {text[:3000]}  # Limit input length

    Concepts:
    """

    response = model.generate_content(prompt)

    # Parse response
    concepts = [c.strip() for c in response.text.split(',')]

    return concepts[:max_concepts]
```

---

## API Configuration

### Basic Setup

```python
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure API
api_key = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=api_key)

# Create model
model = genai.GenerativeModel('gemini-1.5-flash')
```

### Advanced Configuration

```python
from google.generativeai.types import GenerationConfig, SafetySettings

# Generation configuration
generation_config = GenerationConfig(
    temperature=0.7,
    top_p=0.95,
    top_k=40,
    max_output_tokens=2048,
    stop_sequences=["\n\n\n"]  # Stop at triple newline
)

# Safety settings
safety_settings = {
    "HARM_CATEGORY_HARASSMENT": "BLOCK_MEDIUM_AND_ABOVE",
    "HARM_CATEGORY_HATE_SPEECH": "BLOCK_MEDIUM_AND_ABOVE",
    "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_MEDIUM_AND_ABOVE",
    "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_MEDIUM_AND_ABOVE"
}

# Create model with config
model = genai.GenerativeModel(
    'gemini-1.5-flash',
    generation_config=generation_config,
    safety_settings=safety_settings
)
```

### Streaming Responses

```python
def stream_response(prompt):
    """Stream response token by token."""

    response = model.generate_content(
        prompt,
        stream=True
    )

    for chunk in response:
        if chunk.text:
            print(chunk.text, end='', flush=True)
            yield chunk.text
```

**Benefits**:
- Lower perceived latency
- Better user experience
- Can start processing before full response

**Use in Gradio**:
```python
def chat_with_streaming(message, history):
    """Gradio chat with streaming."""

    prompt = format_prompt(message, history)

    partial_response = ""
    for chunk in stream_response(prompt):
        partial_response += chunk
        yield partial_response
```

---

## Advanced Features

### 1. Function Calling

Gemini can call functions to get real-time data:

```python
def search_papers(query: str, max_results: int = 5):
    """Search for papers (will be called by Gemini)."""
    # Implementation
    return search_results

# Define function schema
tools = [
    {
        "function_declarations": [
            {
                "name": "search_papers",
                "description": "Search for academic papers",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query"
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum results to return"
                        }
                    },
                    "required": ["query"]
                }
            }
        ]
    }
]

# Create model with tools
model = genai.GenerativeModel(
    'gemini-1.5-flash',
    tools=tools
)

# Use model
response = model.generate_content(
    "Find me papers about transformers in NLP"
)

# Model might call search_papers function
if response.candidates[0].content.parts[0].function_call:
    function_call = response.candidates[0].content.parts[0].function_call
    function_name = function_call.name
    function_args = function_call.args

    # Execute function
    if function_name == "search_papers":
        results = search_papers(**function_args)

        # Send results back to model
        response = model.generate_content([
            response.candidates[0].content,
            genai.protos.Content(parts=[
                genai.protos.Part(
                    function_response=genai.protos.FunctionResponse(
                        name=function_name,
                        response={"results": results}
                    )
                )
            ])
        ])
```

### 2. Multimodal Prompts

Combine text and images:

```python
def analyze_paper_figure(figure_path, paper_context):
    """Analyze figure in context of paper."""

    image = Image.open(figure_path)

    prompt = f"""
    Paper context: {paper_context}

    Analyze this figure from the paper:
    1. What does it show?
    2. How does it relate to the paper's main findings?
    3. What are the key takeaways?
    """

    response = model.generate_content([prompt, image])
    return response.text
```

### 3. Conversation History

Maintain context across turns:

```python
class GeminiChat:
    """Chat session with conversation history."""

    def __init__(self):
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.chat = self.model.start_chat(history=[])

    def send_message(self, message):
        """Send message and get response."""
        response = self.chat.send_message(message)
        return response.text

    def get_history(self):
        """Get conversation history."""
        return self.chat.history

# Usage
chat = GeminiChat()
response1 = chat.send_message("What is machine learning?")
response2 = chat.send_message("How does it differ from deep learning?")
# Model remembers previous context
```

### 4. JSON Mode

Get structured output:

```python
def extract_structured_data(text):
    """Extract structured data from text."""

    prompt = f"""
    Extract information from this paper and return as JSON:

    {{
        "title": "paper title",
        "authors": ["author1", "author2"],
        "year": 2024,
        "key_findings": ["finding1", "finding2"],
        "methodology": "description"
    }}

    Text: {text}

    JSON:
    """

    response = model.generate_content(prompt)

    # Parse JSON
    import json
    try:
        data = json.loads(response.text)
        return data
    except json.JSONDecodeError:
        # Handle parsing errors
        return None
```

---

## Optimization Strategies

### 1. Prompt Engineering

**Be specific**:
```python
# Bad
prompt = "Tell me about this paper"

# Good
prompt = """
Analyze this paper and provide:
1. Main research question (1 sentence)
2. Methodology (2-3 sentences)
3. Key findings (3-5 bullet points)
4. Limitations (2-3 sentences)
5. Future work suggestions (2-3 bullet points)

Focus on technical details and be concise.
"""
```

**Use examples (few-shot)**:
```python
prompt = """
Extract key concepts from papers. Format: concept | definition

Example 1:
Text: "We propose a transformer architecture..."
Output: Transformer | Neural network architecture using self-attention

Example 2:
Text: "Our method achieves 95% accuracy using BERT..."
Output: BERT | Bidirectional Encoder Representations from Transformers

Now extract from:
Text: {input_text}
Output:
"""
```

**Add constraints**:
```python
prompt = f"""
Answer the question in exactly 3 paragraphs.
Use only information from the context.
Include citations [1], [2], etc.
End with "Confidence: HIGH/MEDIUM/LOW"

Context: {context}
Question: {question}
"""
```

### 2. Context Window Management

```python
def truncate_context(documents, max_tokens=30000):
    """Truncate context to fit in token limit."""

    # Rough estimate: 1 token ≈ 4 characters
    max_chars = max_tokens * 4

    truncated = []
    total_chars = 0

    for doc in documents:
        doc_text = doc['content']
        if total_chars + len(doc_text) > max_chars:
            # Truncate this document
            remaining = max_chars - total_chars
            doc_text = doc_text[:remaining]
            truncated.append(doc_text)
            break
        else:
            truncated.append(doc_text)
            total_chars += len(doc_text)

    return "\n\n".join(truncated)
```

### 3. Caching

Cache responses for common queries:

```python
import hashlib
import json
import os

class GeminiCache:
    """Cache Gemini responses."""

    def __init__(self, cache_dir='cache'):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)

    def get_cache_key(self, prompt, model_name):
        """Generate cache key."""
        key_string = f"{model_name}:{prompt}"
        return hashlib.md5(key_string.encode()).hexdigest()

    def get(self, prompt, model_name):
        """Get cached response."""
        key = self.get_cache_key(prompt, model_name)
        cache_file = os.path.join(self.cache_dir, f"{key}.json")

        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                return json.load(f)['response']

        return None

    def set(self, prompt, model_name, response):
        """Cache response."""
        key = self.get_cache_key(prompt, model_name)
        cache_file = os.path.join(self.cache_dir, f"{key}.json")

        with open(cache_file, 'w') as f:
            json.dump({
                'prompt': prompt,
                'response': response,
                'model': model_name
            }, f)

# Usage
cache = GeminiCache()

def generate_with_cache(prompt, model):
    """Generate with caching."""
    cached = cache.get(prompt, model.model_name)
    if cached:
        return cached

    response = model.generate_content(prompt)
    cache.set(prompt, model.model_name, response.text)
    return response.text
```

### 4. Batch Processing

Process multiple requests efficiently:

```python
import asyncio
from typing import List

async def process_batch(prompts: List[str], model, delay=1.0):
    """Process multiple prompts with rate limiting."""

    results = []

    for prompt in prompts:
        response = model.generate_content(prompt)
        results.append(response.text)

        # Rate limiting
        await asyncio.sleep(delay)

    return results

# Usage
prompts = [
    "Summarize paper 1",
    "Summarize paper 2",
    # ... more prompts
]

results = asyncio.run(process_batch(prompts, model, delay=1.0))
```

---

## Error Handling

### Common Errors

#### 1. Rate Limit Exceeded

```python
from google.api_core import exceptions
import time

def generate_with_retry(prompt, model, max_retries=3):
    """Generate with retry on rate limit."""

    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            return response.text

        except exceptions.ResourceExhausted as e:
            if attempt < max_retries - 1:
                wait_time = (2 ** attempt) * 60  # Exponential backoff
                print(f"Rate limited. Waiting {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise

    return None
```

#### 2. Safety Filters

```python
def handle_safety_blocking(prompt, model):
    """Handle content blocked by safety filters."""

    try:
        response = model.generate_content(prompt)

        # Check if response was blocked
        if not response.candidates:
            print("Response blocked by safety filters")
            return None

        if response.candidates[0].finish_reason == "SAFETY":
            print("Response blocked due to safety")
            # Try with more permissive settings
            return generate_with_permissive_safety(prompt, model)

        return response.text

    except Exception as e:
        print(f"Error: {e}")
        return None
```

#### 3. Token Limit Exceeded

```python
def generate_with_truncation(prompt, context, model, max_tokens=30000):
    """Generate with automatic context truncation."""

    # Estimate token count
    estimated_tokens = len(prompt + context) / 4

    if estimated_tokens > max_tokens:
        # Truncate context
        max_context_chars = (max_tokens - len(prompt)/4) * 4
        context = context[:int(max_context_chars)]
        print(f"Context truncated to fit token limit")

    full_prompt = f"{prompt}\n\nContext: {context}"

    try:
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        print(f"Error: {e}")
        return None
```

---

## Best Practices

### 1. Prompt Design

**Structure prompts clearly**:
```python
prompt = f"""
Role: You are an expert research assistant specializing in {domain}.

Task: {task_description}

Context:
{context}

Instructions:
1. {instruction_1}
2. {instruction_2}
3. {instruction_3}

Output format:
{format_specification}

Question: {question}
"""
```

### 2. Temperature Settings

**Guidelines**:
- **Factual QA**: 0.1 - 0.3 (low randomness)
- **Summarization**: 0.3 - 0.5 (some variation)
- **Creative tasks**: 0.7 - 0.9 (high creativity)
- **Code generation**: 0.2 - 0.4 (mostly deterministic)

### 3. Cost Management

**Monitor usage**:
```python
import time

class UsageTracker:
    """Track API usage."""

    def __init__(self):
        self.requests = []

    def log_request(self, tokens_used):
        """Log a request."""
        self.requests.append({
            'timestamp': time.time(),
            'tokens': tokens_used
        })

    def get_recent_usage(self, minutes=1):
        """Get usage in last N minutes."""
        cutoff = time.time() - (minutes * 60)
        recent = [r for r in self.requests if r['timestamp'] > cutoff]
        return {
            'count': len(recent),
            'tokens': sum(r['tokens'] for r in recent)
        }

# Usage
tracker = UsageTracker()

def generate_with_tracking(prompt, model):
    """Generate with usage tracking."""
    response = model.generate_content(prompt)

    # Estimate tokens (rough)
    tokens = len(prompt + response.text) / 4
    tracker.log_request(tokens)

    # Check if approaching limit
    recent = tracker.get_recent_usage(minutes=1)
    if recent['count'] >= 50:  # 60 RPM free tier
        print("Warning: Approaching rate limit")

    return response.text
```

### 4. Testing

**Test prompts systematically**:
```python
def test_prompt_variations(prompt_templates, test_cases):
    """Test different prompt variations."""

    results = []

    for template in prompt_templates:
        for test_case in test_cases:
            prompt = template.format(**test_case)

            response = model.generate_content(prompt)

            results.append({
                'template': template,
                'test_case': test_case,
                'response': response.text,
                'quality_score': evaluate_response(response.text)
            })

    # Analyze results
    best_template = max(
        results,
        key=lambda x: x['quality_score']
    )['template']

    return best_template, results
```

---

## Migration to Other LLMs

If needed, here's how to switch:

### OpenAI GPT

```python
from langchain_openai import ChatOpenAI

# Replace
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")

# With
llm = ChatOpenAI(model="gpt-4", temperature=0.7)

# Rest of code stays the same (LangChain compatibility)
```

### Anthropic Claude

```python
from langchain_anthropic import ChatAnthropic

llm = ChatAnthropic(model="claude-3-opus-20240229")
```

### Local LLMs (Ollama)

```python
from langchain_community.llms import Ollama

llm = Ollama(model="llama2")
```

---

## Additional Resources

- [Gemini API Documentation](https://ai.google.dev/docs)
- [Gemini Prompt Guide](https://ai.google.dev/docs/prompt_best_practices)
- [Safety Settings](https://ai.google.dev/docs/safety_setting_gemini)
- [LangChain Gemini Integration](https://python.langchain.com/docs/integrations/llms/google_ai)

## Summary

**Key Takeaways**:
1. Use Gemini 1.5 Flash for production (fast, efficient)
2. Implement proper error handling and retries
3. Cache responses when possible
4. Structure prompts clearly
5. Monitor rate limits
6. Test prompts systematically
7. Consider cost vs quality tradeoffs
