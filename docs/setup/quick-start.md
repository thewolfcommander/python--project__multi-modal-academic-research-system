# Quick Start Guide

Get up and running with the Multi-Modal Academic Research System in 5 minutes.

## Table of Contents

- [Prerequisites Checklist](#prerequisites-checklist)
- [5-Minute Setup](#5-minute-setup)
- [Your First Query](#your-first-query)
- [Collecting Your First Papers](#collecting-your-first-papers)
- [Understanding the Interface](#understanding-the-interface)
- [Next Steps](#next-steps)

---

## Prerequisites Checklist

Before you begin, ensure you have completed:

- [ ] Python 3.9+ installed (`python --version`)
- [ ] Docker installed and running (`docker --version`)
- [ ] Google Gemini API key (free from https://makersuite.google.com/app/apikey)
- [ ] Project downloaded/cloned to your local machine

**Not ready?** See the full [Installation Guide](installation.md) for detailed setup instructions.

---

## 5-Minute Setup

### Step 1: Start OpenSearch (1 minute)

Open a terminal and run:

```bash
docker run -d \
  --name opensearch-research \
  -p 9200:9200 \
  -e "discovery.type=single-node" \
  -e "OPENSEARCH_INITIAL_ADMIN_PASSWORD=MyStrongPassword@2024!" \
  opensearchproject/opensearch:latest
```

Wait 30 seconds for OpenSearch to initialize.

### Step 2: Set Up Python Environment (2 minutes)

Navigate to the project directory and run:

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configure API Key (1 minute)

Create your `.env` file:

```bash
cp .env.example .env
```

Edit `.env` and add your Gemini API key:

```env
GEMINI_API_KEY=your_actual_api_key_here
OPENSEARCH_HOST=localhost
OPENSEARCH_PORT=9200
```

### Step 4: Launch the Application (1 minute)

```bash
python main.py
```

You should see:

```
🚀 Initializing Multi-Modal Research Assistant...
✅ Connected to OpenSearch at localhost:9200
✅ Research Assistant ready!
🌐 Opening web interface...

Running on local URL:  http://0.0.0.0:7860
Running on public URL: https://xxxxx.gradio.live
```

**Success!** Open http://localhost:7860 in your browser.

---

## Your First Query

The system comes with no data initially. Let's test it with a simple query to understand the interface, then collect some papers.

### Test the System

1. Navigate to the **Research** tab (should be open by default)
2. In the query box, type: "What is machine learning?"
3. Click **Ask Question**

**Expected Result**: You'll see a message indicating no documents are available yet. This is normal - you need to collect data first!

---

## Collecting Your First Papers

Let's populate the system with academic papers about a topic.

### Step 1: Navigate to Data Collection

1. Click the **Data Collection** tab at the top of the interface

### Step 2: Collect Papers from ArXiv

1. Find the **Collect Papers** section
2. Enter a topic you're interested in, for example:
   - "machine learning"
   - "natural language processing"
   - "computer vision"
   - "quantum computing"

3. Set **Number of papers** to: `5` (for a quick start)

4. Click **Collect Papers**

**What happens**: The system will:
- Search ArXiv for the latest papers on your topic
- Download the PDFs
- Extract text and diagrams
- Analyze diagrams using Gemini Vision
- Generate embeddings
- Index everything in OpenSearch

**Time**: Expect 2-5 minutes for 5 papers.

### Step 3: Monitor Progress

You'll see status updates like:
```
✅ Collected 5 papers on 'machine learning'
Processing paper 1/5: "Deep Learning for Computer Vision"...
✅ Indexed paper: Deep Learning for Computer Vision
Processing paper 2/5: "Attention Is All You Need"...
...
```

### Step 4: Run Your First Real Query

1. Go back to the **Research** tab
2. Enter a query related to your collected papers:
   - "What are the key concepts in machine learning?"
   - "Explain neural networks"
   - "How do transformers work?"

3. Click **Ask Question**

**Expected Result**: You'll receive:
- A comprehensive answer synthesized from the papers
- Citations in brackets [1], [2], etc.
- Source information showing which papers were used

Example response:
```
Machine learning is a subset of artificial intelligence that enables
systems to learn and improve from experience [1]. Key concepts include:

1. Neural Networks: Computational models inspired by biological neurons [1][2]
2. Training: The process of adjusting model parameters using data [2]
3. Deep Learning: Multi-layer neural networks for complex patterns [3]

Sources:
[1] "Deep Learning Fundamentals" (Smith et al., 2023)
[2] "Introduction to Neural Networks" (Johnson, 2023)
[3] "Modern Machine Learning" (Lee et al., 2024)
```

---

## Understanding the Interface

The Research Assistant has four main tabs:

### 1. Research Tab

**Purpose**: Query your knowledge base and get AI-powered answers with citations

**Key Features**:
- Query input box
- AI-generated responses with citations
- Conversation history
- Source attribution

**Usage Tips**:
- Ask specific questions for better results
- Use follow-up questions to dive deeper
- Check citations to verify information

### 2. Data Collection Tab

**Purpose**: Gather academic content from multiple sources

**Sources Available**:
- **Academic Papers**: ArXiv, PubMed Central, Semantic Scholar
- **YouTube Videos**: Educational channels and lectures
- **Podcasts**: Academic and educational podcast episodes

**Parameters**:
- Topic/search query
- Number of items to collect
- Source preference

**Usage Tips**:
- Start with 5-10 papers to avoid long wait times
- Choose topics that match your research interests
- Mix different sources (papers, videos, podcasts) for diverse perspectives

### 3. Citation Manager Tab

**Purpose**: View and export citations from your research sessions

**Features**:
- List of all cited sources
- Export to BibTeX format
- Citation details (authors, title, date, URL)

**Usage Tips**:
- Export citations after each research session
- Use BibTeX exports in your LaTeX documents
- Keep track of sources for academic writing

### 4. Settings Tab

**Purpose**: Configure system settings and connections

**Settings**:
- OpenSearch connection (host, port)
- API keys (Gemini)
- Index management
- System health status

**Usage Tips**:
- Check connection status if searches fail
- Verify OpenSearch is running
- Update API keys if needed

---

## Quick Tips for Success

### 1. Collection Strategy

**Start Small**: Collect 5-10 papers initially to test the system
- Faster processing
- Easier to verify quality
- Quick feedback on topics

**Scale Up**: Once comfortable, collect 20-50 papers per topic
- Better coverage
- More comprehensive answers
- Diverse perspectives

### 2. Query Techniques

**Be Specific**:
- Good: "What is the attention mechanism in transformers?"
- Less effective: "Tell me about AI"

**Ask Follow-ups**:
- "Can you explain that in simpler terms?"
- "What are the practical applications?"
- "How does this compare to other approaches?"

**Request Evidence**:
- "What evidence supports this claim?"
- "Which papers discuss this topic?"

### 3. Content Diversity

Mix different content types for richer research:
- **Papers**: Detailed technical information, formulas, experiments
- **Videos**: Visual explanations, demonstrations, lectures
- **Podcasts**: Discussions, interviews, high-level overviews

### 4. Regular Maintenance

**Update Your Knowledge Base**:
- Collect new papers weekly on your topics
- Keep content current with latest research

**Monitor Storage**:
- PDFs and processed data accumulate in `data/` folder
- Clean up old content periodically

**Check Logs**:
- Review `logs/` directory for any errors
- Helps troubleshoot issues early

---

## Common Quick Start Issues

### Issue: "Cannot connect to OpenSearch"

**Quick Fix**:
```bash
# Check if OpenSearch is running
docker ps | grep opensearch

# If not running, start it
docker start opensearch-research

# If container doesn't exist, create it (see Step 1)
```

### Issue: "GEMINI_API_KEY not found"

**Quick Fix**:
1. Verify `.env` file exists: `ls -la .env`
2. Check content: `cat .env`
3. Ensure key has no quotes: `GEMINI_API_KEY=AIza...` not `GEMINI_API_KEY="AIza..."`
4. Restart application: `python main.py`

### Issue: Papers collecting but not processing

**Quick Fix**:
- Check logs in `logs/` directory for errors
- Verify Gemini API key is valid
- Try with fewer papers (1-2) to isolate issues
- Check internet connection

### Issue: Slow performance

**Quick Fix**:
- Start with fewer papers (5 instead of 20)
- Close other applications to free memory
- Wait for first-time model downloads to complete
- Check Docker has enough memory allocated (4GB+ recommended)

---

## Example Workflows

### Workflow 1: Research a New Topic

1. **Collect**: Data Collection → Enter "quantum computing" → Collect 10 papers
2. **Explore**: Research → "What is quantum computing?"
3. **Deep Dive**: Research → "How do quantum gates work?"
4. **Compare**: Research → "What are the differences between quantum and classical computing?"
5. **Export**: Citation Manager → Export BibTeX

### Workflow 2: Literature Review

1. **Broad Collection**: Collect 30 papers on your research area
2. **Overview**: "What are the main research directions in [topic]?"
3. **Specific Topics**: "What methods are used for [specific problem]?"
4. **Gaps**: "What are open challenges in [topic]?"
5. **Timeline**: "How has [topic] evolved over time?"

### Workflow 3: Learning a New Concept

1. **Mixed Media**: Collect papers + YouTube videos on the topic
2. **Introduction**: "Explain [concept] in simple terms"
3. **Technical**: "What is the mathematical foundation of [concept]?"
4. **Visual**: Videos provide diagrams and animations
5. **Practice**: "What are example applications of [concept]?"

---

## Next Steps

Now that you're up and running:

### Learn More

1. **Configuration Guide**: Customize settings, logging, and advanced options
   - See [Configuration Guide](configuration.md)

2. **Architecture**: Understand how the system works under the hood
   - See [Technology Stack](../architecture/technology-stack.md)

3. **Full Documentation**: Explore all features and capabilities
   - See [Main README](../../CLAUDE.md)

### Expand Your Knowledge Base

- Collect papers from multiple sources (ArXiv, PubMed, Semantic Scholar)
- Add YouTube lectures from educational channels
- Include podcast episodes for diverse perspectives

### Optimize Your Workflow

- Create topic-specific collections
- Use citation exports for your papers
- Experiment with different query styles
- Build a comprehensive research database

---

## Troubleshooting

**Still having issues?**

1. **Check Logs**: `logs/research_system_*.log` contains detailed error information
2. **Verify Setup**: Run through the [Installation Guide](installation.md) checklist
3. **Review Configuration**: See [Configuration Guide](configuration.md)
4. **Common Issues**: Full list in [Installation Guide - Common Issues](installation.md#common-installation-issues)

---

## Getting Help

- **Documentation**: Start with CLAUDE.md in the project root
- **Logs**: Check `logs/` directory for error details
- **Issues**: Report bugs or request features on GitHub

---

**Congratulations! You're now ready to conduct AI-powered academic research with multi-modal sources.**

Happy researching!
