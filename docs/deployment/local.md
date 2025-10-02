# Local Deployment Guide

This guide covers setting up and running the Multi-Modal Academic Research System on your local development machine.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [Environment Configuration](#environment-configuration)
4. [Running the Application](#running-the-application)
5. [Running Multiple Instances](#running-multiple-instances)
6. [Port Configuration](#port-configuration)
7. [Local Development Workflow](#local-development-workflow)
8. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

- **Operating System**: macOS, Linux, or Windows 10/11
- **Python**: Version 3.9 or higher
- **RAM**: Minimum 4GB, recommended 8GB+
- **Disk Space**: Minimum 5GB for application and data
- **Docker**: For running OpenSearch (or install OpenSearch natively)

### Required Software

1. **Python 3.9+**
   ```bash
   # Check Python version
   python --version
   # or
   python3 --version
   ```

2. **pip** (Python package manager)
   ```bash
   # Check pip version
   pip --version
   ```

3. **Docker Desktop** (recommended for OpenSearch)
   - Download from: https://www.docker.com/products/docker-desktop
   - Verify installation:
     ```bash
     docker --version
     docker-compose --version
     ```

4. **Git** (for cloning repository)
   ```bash
   git --version
   ```

## Initial Setup

### 1. Clone the Repository

```bash
# Clone the repository
git clone <repository-url>
cd multi-modal-academic-research-system

# Verify repository structure
ls -la
```

### 2. Create Virtual Environment

Using a virtual environment isolates project dependencies from your system Python.

**macOS/Linux:**
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Verify activation (should show venv in path)
which python
```

**Windows:**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Verify activation
where python
```

### 3. Install Dependencies

```bash
# Upgrade pip to latest version
pip install --upgrade pip

# Install all required packages
pip install -r requirements.txt

# Verify installation
pip list
```

**Expected Key Packages:**
- opensearch-py==2.4.0
- langchain==0.2.16
- google-generativeai==0.7.2
- gradio==4.8.0
- sentence-transformers==2.7.0

### 4. Create Data Directories

The application stores data in various directories:

```bash
# Create all necessary directories
mkdir -p data/papers
mkdir -p data/videos
mkdir -p data/podcasts
mkdir -p data/processed
mkdir -p configs
mkdir -p logs

# Verify directory structure
tree -d -L 2
```

## Environment Configuration

### 1. Create Environment File

```bash
# Copy example environment file
cp .env.example .env

# Edit the file with your preferred editor
nano .env
# or
vim .env
# or
code .env  # VS Code
```

### 2. Configure Environment Variables

Edit `.env` file with the following configuration:

```bash
# ============================================
# API Keys (Required)
# ============================================
# Get your Gemini API key from: https://makersuite.google.com/app/apikey
GEMINI_API_KEY=your_actual_api_key_here

# ============================================
# OpenSearch Configuration
# ============================================
OPENSEARCH_HOST=localhost
OPENSEARCH_PORT=9200
OPENSEARCH_USER=admin
OPENSEARCH_PASSWORD=admin
OPENSEARCH_USE_SSL=false
OPENSEARCH_VERIFY_CERTS=false

# ============================================
# Application Configuration
# ============================================
# Gradio server settings
GRADIO_SERVER_NAME=0.0.0.0
GRADIO_SERVER_PORT=7860
GRADIO_SHARE=true

# Index name for OpenSearch
OPENSEARCH_INDEX_NAME=research_assistant

# Embedding model
EMBEDDING_MODEL=all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384

# ============================================
# Data Collection Settings
# ============================================
# Maximum papers to collect per query
MAX_PAPERS_PER_QUERY=10

# Maximum videos to collect per query
MAX_VIDEOS_PER_QUERY=10

# Rate limiting (requests per minute)
API_RATE_LIMIT=60

# ============================================
# Logging Configuration
# ============================================
LOG_LEVEL=INFO
LOG_FILE=logs/research_assistant.log
```

### 3. Obtain Gemini API Key

The Gemini API key is **required** for the application to function:

1. Visit: https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated key
5. Paste it into your `.env` file

**Security Note:** Never commit your `.env` file with real API keys to version control.

## Running the Application

### 1. Start OpenSearch

**Using Docker (Recommended):**

```bash
# Start OpenSearch in background
docker run -d \
  --name opensearch-node1 \
  -p 9200:9200 \
  -p 9600:9600 \
  -e "discovery.type=single-node" \
  -e "OPENSEARCH_INITIAL_ADMIN_PASSWORD=MyStrongPassword123!" \
  opensearchproject/opensearch:latest

# Verify OpenSearch is running
curl -X GET "http://localhost:9200" -u admin:MyStrongPassword123!

# Check container logs
docker logs opensearch-node1
```

**Expected Response:**
```json
{
  "name" : "opensearch-node1",
  "cluster_name" : "docker-cluster",
  "version" : {
    "number" : "2.11.0",
    ...
  },
  "tagline" : "The OpenSearch Project: https://opensearch.org/"
}
```

**Stop OpenSearch:**
```bash
docker stop opensearch-node1
docker rm opensearch-node1
```

### 2. Start the Application

```bash
# Ensure virtual environment is activated
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# Run the application
python main.py
```

**Expected Output:**
```
🚀 Initializing Multi-Modal Research Assistant...
✅ Research Assistant ready!
🌐 Opening web interface...
📝 Logs are being written to: logs/research_assistant.log

Running on local URL:  http://0.0.0.0:7860
Running on public URL: https://xxxxx.gradio.live

This share link expires in 72 hours.
```

### 3. Access the Application

- **Local URL**: http://localhost:7860
- **Public URL**: Provided in console output (valid for 72 hours)
- **Local Network**: http://<your-ip>:7860

## Running Multiple Instances

You may want to run multiple instances for different use cases or testing.

### Method 1: Different Ports

```bash
# Terminal 1 - Instance 1 on port 7860
export GRADIO_SERVER_PORT=7860
python main.py

# Terminal 2 - Instance 2 on port 7861
export GRADIO_SERVER_PORT=7861
python main.py

# Terminal 3 - Instance 3 on port 7862
export GRADIO_SERVER_PORT=7862
python main.py
```

### Method 2: Different Virtual Environments

```bash
# Create separate environments for each instance
python3 -m venv venv1
python3 -m venv venv2

# Setup instance 1
source venv1/bin/activate
pip install -r requirements.txt
cp .env .env1
# Edit .env1 with different GRADIO_SERVER_PORT
python main.py

# Setup instance 2 (new terminal)
source venv2/bin/activate
pip install -r requirements.txt
cp .env .env2
# Edit .env2 with different GRADIO_SERVER_PORT and INDEX_NAME
python main.py
```

### Method 3: Different OpenSearch Indices

To avoid data conflicts, use separate indices:

```bash
# Instance 1 - .env file
OPENSEARCH_INDEX_NAME=research_assistant_dev
GRADIO_SERVER_PORT=7860

# Instance 2 - .env.test file
OPENSEARCH_INDEX_NAME=research_assistant_test
GRADIO_SERVER_PORT=7861

# Run instances
python main.py  # Uses .env
python main.py --env-file .env.test  # Custom env file (if supported)
```

## Port Configuration

### Understanding Port Usage

The application uses the following ports:

1. **7860** - Gradio web interface (default)
2. **9200** - OpenSearch HTTP API
3. **9600** - OpenSearch Performance Analyzer (optional)

### Changing the Gradio Port

**Method 1: Environment Variable**
```bash
# In .env file
GRADIO_SERVER_PORT=8080

# Or set temporarily
export GRADIO_SERVER_PORT=8080
python main.py
```

**Method 2: Modify main.py**
```python
# In main.py, find:
app.launch(
    server_name="0.0.0.0",
    server_port=7860,  # Change this
    share=True
)
```

### Checking Port Availability

```bash
# macOS/Linux
lsof -i :7860
netstat -an | grep 7860

# Windows
netstat -ano | findstr :7860
```

### Freeing Up Ports

```bash
# Find process using port
lsof -ti:7860

# Kill process
kill -9 $(lsof -ti:7860)

# Or on Windows
# Find PID
netstat -ano | findstr :7860
# Kill using Task Manager or:
taskkill /PID <pid> /F
```

## Local Development Workflow

### Daily Development Routine

1. **Start Development Session**
   ```bash
   # Navigate to project
   cd /path/to/multi-modal-academic-research-system

   # Activate virtual environment
   source venv/bin/activate

   # Start OpenSearch (if not running)
   docker start opensearch-node1

   # Verify OpenSearch
   curl -X GET "http://localhost:9200/_cluster/health"

   # Start application
   python main.py
   ```

2. **Make Changes**
   - Edit code in your preferred IDE
   - Save changes
   - Restart application to see changes

3. **View Logs**
   ```bash
   # Tail application logs
   tail -f logs/research_assistant.log

   # View OpenSearch logs
   docker logs -f opensearch-node1
   ```

4. **End Development Session**
   ```bash
   # Stop application (Ctrl+C)

   # Optionally stop OpenSearch
   docker stop opensearch-node1

   # Deactivate virtual environment
   deactivate
   ```

### Development Tips

1. **Auto-Reload During Development**

   Use a file watcher to restart on changes:
   ```bash
   # Install watchdog
   pip install watchdog

   # Create restart script
   echo '#!/bin/bash
   while true; do
     python main.py
     sleep 2
   done' > run_dev.sh

   chmod +x run_dev.sh
   ./run_dev.sh
   ```

2. **Debugging**

   Enable debug logging in `.env`:
   ```bash
   LOG_LEVEL=DEBUG
   ```

   Or use Python debugger:
   ```python
   # Add to code
   import pdb; pdb.set_trace()
   ```

3. **Testing Changes**

   ```bash
   # Run with test index
   export OPENSEARCH_INDEX_NAME=test_index
   python main.py
   ```

## Troubleshooting

### Common Issues and Solutions

#### 1. Port Already in Use

**Error:**
```
OSError: [Errno 48] Address already in use
```

**Solution:**
```bash
# Find and kill process on port 7860
lsof -ti:7860 | xargs kill -9

# Or change port
export GRADIO_SERVER_PORT=7861
python main.py
```

#### 2. OpenSearch Connection Failed

**Error:**
```
ConnectionRefusedError: [Errno 61] Connection refused
```

**Solutions:**

a) **Check if OpenSearch is running:**
```bash
docker ps | grep opensearch
curl http://localhost:9200
```

b) **Start OpenSearch:**
```bash
docker start opensearch-node1
# or
docker run -d --name opensearch-node1 -p 9200:9200 -e "discovery.type=single-node" opensearchproject/opensearch:latest
```

c) **Check firewall settings:**
```bash
# macOS
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add python3
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --unblock python3

# Linux (UFW)
sudo ufw allow 9200
```

d) **Verify .env configuration:**
```bash
# Check OPENSEARCH_HOST and OPENSEARCH_PORT
cat .env | grep OPENSEARCH
```

#### 3. Missing GEMINI_API_KEY

**Error:**
```
⚠️  Please set GEMINI_API_KEY in your .env file
```

**Solution:**
1. Get API key from: https://makersuite.google.com/app/apikey
2. Add to `.env`:
   ```bash
   GEMINI_API_KEY=your_actual_key_here
   ```
3. Restart application

#### 4. Module Not Found Errors

**Error:**
```
ModuleNotFoundError: No module named 'opensearch'
```

**Solution:**
```bash
# Verify virtual environment is activated
which python
# Should show path inside venv/

# Reinstall dependencies
pip install -r requirements.txt

# Check installed packages
pip list | grep opensearch
```

#### 5. Permission Denied Errors

**Error:**
```
PermissionError: [Errno 13] Permission denied: 'data/papers'
```

**Solution:**
```bash
# Fix directory permissions
chmod -R 755 data/
chmod -R 755 logs/

# Or recreate directories
rm -rf data/ logs/
mkdir -p data/{papers,videos,podcasts,processed} logs/
```

#### 6. Out of Memory Errors

**Error:**
```
MemoryError: Unable to allocate array
```

**Solutions:**

a) **Reduce batch size in configuration**
b) **Use smaller embedding model**
c) **Increase system swap space**
d) **Process fewer documents at once**

#### 7. Gradio Not Accessible

**Error:**
Cannot access http://localhost:7860

**Solutions:**

a) **Check if application is running:**
```bash
ps aux | grep python
```

b) **Check if port is listening:**
```bash
netstat -an | grep 7860
lsof -i :7860
```

c) **Try different server name:**
```python
# In main.py
app.launch(
    server_name="127.0.0.1",  # Instead of 0.0.0.0
    server_port=7860,
    share=False
)
```

d) **Check firewall:**
```bash
# macOS
sudo pfctl -d  # Disable firewall temporarily

# Linux
sudo ufw status
sudo ufw allow 7860
```

#### 8. Slow Performance

**Symptoms:**
- Slow search queries
- UI freezing
- Long processing times

**Solutions:**

a) **Check OpenSearch health:**
```bash
curl http://localhost:9200/_cluster/health?pretty
```

b) **Monitor resource usage:**
```bash
# CPU and memory
top
htop

# Docker resources
docker stats opensearch-node1
```

c) **Optimize OpenSearch:**
```bash
# Increase heap size
docker run -d \
  --name opensearch-node1 \
  -p 9200:9200 \
  -e "discovery.type=single-node" \
  -e "OPENSEARCH_JAVA_OPTS=-Xms2g -Xmx2g" \
  opensearchproject/opensearch:latest
```

d) **Clear old data:**
```bash
# Delete old indices
curl -X DELETE "http://localhost:9200/old_index_name"

# Clear cache
curl -X POST "http://localhost:9200/_cache/clear"
```

#### 9. SSL Certificate Errors

**Error:**
```
SSLError: certificate verify failed
```

**Solution:**
```bash
# In .env file
OPENSEARCH_USE_SSL=false
OPENSEARCH_VERIFY_CERTS=false
```

#### 10. Application Crashes on Startup

**Solutions:**

a) **Check logs:**
```bash
tail -100 logs/research_assistant.log
```

b) **Verify Python version:**
```bash
python --version  # Should be 3.9+
```

c) **Clean reinstall:**
```bash
# Remove virtual environment
rm -rf venv/

# Recreate
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

d) **Check for conflicting processes:**
```bash
# Kill all python processes
pkill -f python

# Restart clean
python main.py
```

### Getting Help

If issues persist:

1. **Check logs:** `logs/research_assistant.log`
2. **Enable debug logging:** Set `LOG_LEVEL=DEBUG` in `.env`
3. **Check GitHub issues:** Search for similar problems
4. **Stack traces:** Include full error messages when reporting issues

### Useful Commands Reference

```bash
# Check application status
ps aux | grep "python main.py"

# Monitor logs in real-time
tail -f logs/research_assistant.log

# Check OpenSearch status
curl http://localhost:9200/_cat/health?v

# List all indices
curl http://localhost:9200/_cat/indices?v

# Check index document count
curl http://localhost:9200/research_assistant/_count

# Monitor system resources
top -o cpu  # Sort by CPU
top -o mem  # Sort by memory

# Test Gemini API connection
curl -H "Content-Type: application/json" \
  -d '{"contents":[{"parts":[{"text":"Hello"}]}]}' \
  "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key=YOUR_API_KEY"
```

## Next Steps

- Review [Docker Deployment](docker.md) for containerized setup
- See [OpenSearch Setup](opensearch.md) for advanced configuration
- Check [Production Considerations](production.md) before deploying to production
