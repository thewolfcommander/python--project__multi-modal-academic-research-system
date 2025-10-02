# Installation Guide

Complete step-by-step instructions for installing the Multi-Modal Academic Research System.

## Table of Contents

- [System Requirements](#system-requirements)
- [Prerequisites](#prerequisites)
- [Installation Steps](#installation-steps)
- [Verifying Installation](#verifying-installation)
- [Common Installation Issues](#common-installation-issues)
- [Platform-Specific Notes](#platform-specific-notes)

---

## System Requirements

### Minimum Requirements

- **Operating System**: macOS, Linux, or Windows 10/11
- **Python**: Python 3.9 or higher (Python 3.11 recommended)
- **RAM**: 4GB minimum, 8GB recommended
- **Disk Space**: 5GB free space (for dependencies, models, and data)
- **Internet**: Stable internet connection for downloading dependencies and API access

### Recommended Specifications

- **Python**: Python 3.11.x
- **RAM**: 8GB or more (for processing large PDFs and running embedding models)
- **Disk Space**: 10GB+ for storing papers, videos, and processed data
- **GPU**: Optional, but helpful for faster embedding generation

---

## Prerequisites

Before installing the Multi-Modal Academic Research System, ensure you have:

1. **Python 3.9+** installed on your system
   ```bash
   python --version  # Should show Python 3.9.x or higher
   ```

2. **pip** package manager (comes with Python)
   ```bash
   pip --version
   ```

3. **Docker** installed (for OpenSearch)
   - Download from: https://www.docker.com/get-started
   - Verify installation: `docker --version`

4. **Git** (optional, for cloning the repository)
   ```bash
   git --version
   ```

5. **Google Gemini API Key** (free tier available)
   - Get your key at: https://makersuite.google.com/app/apikey
   - No credit card required for the free tier

---

## Installation Steps

### Step 1: Clone or Download the Repository

**Option A: Using Git**
```bash
git clone <repository-url>
cd multi-modal-academic-research-system
```

**Option B: Download ZIP**
- Download and extract the project ZIP file
- Navigate to the extracted directory

### Step 2: Create a Virtual Environment

Creating a virtual environment isolates the project dependencies from your system Python.

**macOS/Linux:**
```bash
python -m venv venv
```

**Windows:**
```bash
python -m venv venv
```

### Step 3: Activate the Virtual Environment

**macOS/Linux:**
```bash
source venv/bin/activate
```

**Windows Command Prompt:**
```bash
venv\Scripts\activate
```

**Windows PowerShell:**
```bash
venv\Scripts\Activate.ps1
```

You should see `(venv)` prepended to your command prompt, indicating the virtual environment is active.

### Step 4: Upgrade pip (Recommended)

```bash
pip install --upgrade pip
```

### Step 5: Install Python Dependencies

Install all required packages from `requirements.txt`:

```bash
pip install -r requirements.txt
```

This will install approximately 30+ packages including:
- OpenSearch client
- LangChain and Google Gemini integration
- Gradio for the web UI
- PDF processing libraries
- YouTube and podcast collectors
- Sentence transformers for embeddings
- And many more...

**Expected installation time**: 5-10 minutes depending on your internet connection.

### Step 6: Configure Environment Variables

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file with your preferred text editor:
   ```bash
   # On macOS/Linux
   nano .env

   # Or use any text editor
   code .env  # VS Code
   vim .env   # Vim
   ```

3. Add your Gemini API key:
   ```
   GEMINI_API_KEY=your_actual_api_key_here
   OPENSEARCH_HOST=localhost
   OPENSEARCH_PORT=9200
   ```

### Step 7: Start OpenSearch

OpenSearch is required for indexing and searching academic content.

**Using Docker (Recommended):**

```bash
docker run -d \
  --name opensearch-research \
  -p 9200:9200 \
  -p 9600:9600 \
  -e "discovery.type=single-node" \
  -e "OPENSEARCH_INITIAL_ADMIN_PASSWORD=MyStrongPassword@2024!" \
  opensearchproject/opensearch:latest
```

**Verify OpenSearch is running:**
```bash
curl -X GET https://localhost:9200 -ku admin:MyStrongPassword@2024!
```

You should see JSON output with cluster information.

### Step 8: Initialize Data Directories

The application will create these automatically, but you can create them manually:

```bash
mkdir -p data/papers data/videos data/podcasts data/processed
mkdir -p logs configs
```

### Step 9: Download Embedding Models

On first run, the sentence transformer model will be downloaded automatically (~90MB). To download it now:

```bash
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

---

## Verifying Installation

### Test 1: Check Python Environment

```bash
python -c "import sys; print(f'Python {sys.version}')"
```

### Test 2: Verify Dependencies

```bash
python -c "import opensearchpy, langchain, gradio, google.generativeai; print('All core dependencies installed successfully')"
```

### Test 3: Check OpenSearch Connection

```bash
python -c "from opensearchpy import OpenSearch; client = OpenSearch(hosts=[{'host': 'localhost', 'port': 9200}], http_auth=('admin', 'MyStrongPassword@2024!'), use_ssl=True, verify_certs=False); print(client.info())"
```

### Test 4: Run the Application

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
Running on public URL: https://[random-id].gradio.live
```

Open the local URL in your browser. If you see the Research Assistant interface, installation is complete!

---

## Common Installation Issues

### Issue 1: Python Version Mismatch

**Problem**: `python --version` shows Python 2.x or Python < 3.9

**Solution**:
- Try `python3 --version` instead
- Use `python3` and `pip3` commands throughout installation
- Install Python 3.11 from python.org

### Issue 2: pip Install Fails with Permission Error

**Problem**: `ERROR: Could not install packages due to an EnvironmentError: [Errno 13] Permission denied`

**Solution**:
- Ensure virtual environment is activated (you should see `(venv)`)
- If not in venv: Activate it again: `source venv/bin/activate`
- Never use `sudo pip install` - this can break your system Python

### Issue 3: OpenSearch Won't Start

**Problem**: Docker container fails or port 9200 is already in use

**Solutions**:
1. Check if OpenSearch is already running:
   ```bash
   docker ps | grep opensearch
   ```

2. Stop existing container:
   ```bash
   docker stop opensearch-research
   docker rm opensearch-research
   ```

3. Check if port 9200 is in use:
   ```bash
   # macOS/Linux
   lsof -i :9200

   # Windows
   netstat -ano | findstr :9200
   ```

4. Use a different port if needed (update `.env` file):
   ```bash
   docker run -d -p 9201:9200 -e "discovery.type=single-node" opensearchproject/opensearch:latest
   ```
   Then set `OPENSEARCH_PORT=9201` in `.env`

### Issue 4: ModuleNotFoundError

**Problem**: `ModuleNotFoundError: No module named 'opensearchpy'` (or other package)

**Solutions**:
1. Verify virtual environment is active:
   ```bash
   which python  # Should show path to venv/bin/python
   ```

2. Reinstall requirements:
   ```bash
   pip install -r requirements.txt
   ```

3. Install missing package individually:
   ```bash
   pip install opensearch-py
   ```

### Issue 5: Gemini API Key Not Recognized

**Problem**: `⚠️  Please set GEMINI_API_KEY in your .env file`

**Solutions**:
1. Verify `.env` file exists in project root:
   ```bash
   ls -la .env
   ```

2. Check the file content (key should not have quotes):
   ```
   # Correct
   GEMINI_API_KEY=AIzaSyAbc123...

   # Incorrect
   GEMINI_API_KEY="AIzaSyAbc123..."  # Remove quotes
   ```

3. Ensure no trailing spaces or newlines

4. Restart the application after editing `.env`

### Issue 6: SSL Certificate Errors with OpenSearch

**Problem**: `SSL: CERTIFICATE_VERIFY_FAILED` errors

**Solution**: The application already disables SSL verification for local OpenSearch. If issues persist:
1. Check firewall settings
2. Verify OpenSearch container is running: `docker ps`
3. Try accessing OpenSearch directly: `curl -k https://localhost:9200`

### Issue 7: Out of Memory Errors

**Problem**: System runs out of memory during PDF processing or embedding generation

**Solutions**:
1. Close other applications
2. Process fewer documents at once
3. Restart the application
4. Increase Docker memory limits if using Docker Desktop

### Issue 8: Slow Download of Embedding Models

**Problem**: First run takes very long downloading models

**Solution**:
- Be patient - the all-MiniLM-L6-v2 model is ~90MB
- Check internet connection
- Download manually using the command in Step 9
- The model is cached locally after first download

### Issue 9: Port 7860 Already in Use

**Problem**: Gradio cannot start because port 7860 is occupied

**Solution**:
1. Find what's using the port:
   ```bash
   # macOS/Linux
   lsof -i :7860

   # Windows
   netstat -ano | findstr :7860
   ```

2. Kill the process or modify `main.py` to use a different port:
   ```python
   app.launch(
       server_name="0.0.0.0",
       server_port=7861,  # Changed port
       share=True
   )
   ```

---

## Platform-Specific Notes

### macOS

- **M1/M2 Macs**: All dependencies are compatible with ARM architecture
- **Rosetta**: Not required; native ARM support available
- **Permission Issues**: You may need to allow terminal to access folders in System Preferences

### Linux

- **Ubuntu/Debian**: Install system dependencies:
  ```bash
  sudo apt-get update
  sudo apt-get install python3-dev python3-pip python3-venv
  ```

- **Fedora/RHEL**:
  ```bash
  sudo dnf install python3-devel python3-pip
  ```

### Windows

- **PowerShell Execution Policy**: If activation fails:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```

- **Long Path Support**: Enable long paths in Windows (required for some packages):
  - Run as Administrator:
    ```
    reg add "HKLM\SYSTEM\CurrentControlSet\Control\FileSystem" /v LongPathsEnabled /t REG_DWORD /d 1 /f
    ```

- **Visual C++ Redistributables**: Some packages require Visual Studio build tools:
  - Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/

---

## Next Steps

After successful installation:

1. **Quick Start**: Follow the [Quick Start Guide](quick-start.md) to run your first query
2. **Configuration**: Review the [Configuration Guide](configuration.md) for advanced settings
3. **Architecture**: Learn about the system in the [Technology Stack](../architecture/technology-stack.md) document

---

## Getting Help

If you encounter issues not covered here:

1. Check the logs in the `logs/` directory
2. Review the [Configuration Guide](configuration.md)
3. Consult the main [CLAUDE.md](../../CLAUDE.md) file
4. Check GitHub issues or create a new one

---

**Installation complete! You're ready to start researching with your Multi-Modal Academic Research System.**
