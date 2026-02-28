# Local RAG System with MCP Server

<div align="center">

**A Production-Grade Retrieval Augmented Generation (RAG) System for Intelligent Document Management**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-green)](https://fastapi.tiangolo.com/)

[Features](#features) • [Installation](#installation) • [Quick Start](#quick-start) • [API Usage](#api-usage) • [Architecture](#architecture) • [Contributing](#contributing)

</div>

---

## 🎯 What This Does

Drop documents into a monitored folder. The system **automatically** detects, chunks, embeds, and stores them in a searchable vector database. Query your entire knowledge base in natural language via REST API or integrate with AI agents through the Model Context Protocol (MCP).

**Perfect for:**
- Internal knowledge base systems
- Documentation search engines
- RAG-powered AI assistants
- Developer tool integration
- Intelligent document analysis

---

## ✨ Features

### Core Capabilities
- 🔄 **Real-Time Document Ingestion** - FileWatcher automatically detects and processes new/updated documents
- 🧠 **Semantic Search** - Find relevant content by meaning, not just keywords
- 💾 **Persistent Storage** - ChromaDB ensures no data loss between restarts
- ⚡ **Incremental Processing** - Only processes changed files (efficient for large datasets)
- 🔌 **Multiple Interfaces** - REST API, MCP protocol, and direct Python integration
- 📊 **System Monitoring** - Real-time health checks and performance metrics
- 📝 **Structured Logging** - Detailed audit trails and debugging information

### Advanced Features
- Multi-format support (`.txt`, `.pdf`, `.docx`)
- Smart document chunking with overlap (prevents context loss)
- Content signature tracking (prevents duplicate processing)
- Graceful state management and recovery
- CORS-enabled REST API
- MCP (Model Context Protocol) integration for AI agents

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   INGESTION PIPELINE                         │
├─────────────────────────────────────────────────────────────┤
│ File System → FileWatcher → DocumentProcessor → Vector DB   │
│              (Real-time)    (Extract, Chunk,     (Persist)  │
│                            Embed)                            │
└─────────────────────────────────────────────────────────────┘
                            ⬇ (Persistent)
┌─────────────────────────────────────────────────────────────┐
│                    RETRIEVAL PIPELINE                        │
├─────────────────────────────────────────────────────────────┤
│ REST API/MCP → Query Handler → Vector Search → Results      │
│ (FastAPI)      (Query Embedding) (Semantic)   (Ranked)      │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

| Component | Purpose | Technology |
|-----------|---------|-----------|
| **FileWatcher** | Real-time directory monitoring | watchdog |
| **DocumentProcessor** | Extract & chunk documents | PyMUPDF, python-docx, LangChain |
| **VectorStore** | Semantic search & storage | ChromaDB, sentence-transformers |
| **MCPServer** | REST API & MCP protocol | FastAPI, Uvicorn |
| **StateManager** | Persistent state tracking | JSON-based signatures |
| **StartupManager** | System orchestration | Asyncio |

---

## 🚀 Installation

### Prerequisites
- Python 3.9 or higher
- pip (Python package manager)
- 200MB disk space (for ChromaDB and dependencies)

### Step-by-Step Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/subashnalam/LocalRag.git
   cd LocalRag
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate
   
   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r local-rag/requirements.txt
   ```

4. **Configure environment** (optional for basic usage)
   ```bash
   cd local-rag
   echo "OPENAI_API_KEY=your_key_here" > .env
   ```

5. **Run the system**
   ```bash
   python main.py
   ```
   
   Expected output:
   ```
   Phase 1: Loading existing system state...
   Phase 2: Initializing services (Vector Store)...
   Phase 3: Processing new documents...
   Phase 4: Starting background services...
   System is fully initialized and running. Monitoring for changes.
   ```

---

## 🎮 Quick Start

### 1. Add Documents

Copy your documents to the `local-rag/data/documents/` folder:
```bash
cp myfile.pdf local-rag/data/documents/
```

The system automatically:
- ✅ Detects the new file
- ✅ Extracts text content
- ✅ Splits into semantic chunks
- ✅ Generates embeddings
- ✅ Stores in vector database

### 2. Query Documents

**Via REST API:**
```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is machine learning?",
    "limit": 5
  }'
```

**Response:**
```json
{
  "results": [
    {
      "content": "Machine learning is a subset of artificial intelligence...",
      "metadata": {
        "source": "docs/intro.pdf",
        "chunk_index": 2,
        "processing_time": "2024-02-28T10:30:00"
      },
      "score": 0.95
    },
    ...
  ],
  "total_found": 5,
  "query_time_ms": 45
}
```

### 3. Check System Health

```bash
curl "http://localhost:8000/health"
```

Response:
```json
{
  "status": "healthy",
  "total_documents": 3,
  "services_running": ["file_watcher", "vector_store", "mcp_server"],
  "uptime_seconds": 3600,
  "storage_used_mb": 45.2
}
```

---

## 📡 API Documentation

### REST Endpoints

#### 🔍 Search Documents
```
POST /search
Content-Type: application/json

{
  "query": "your search question",
  "limit": 10,
  "filter_source": "optional/path/to/file.pdf"
}
```

**Returns:** Ranked search results with similarity scores

---

#### 📋 List All Documents
```
GET /documents
```

**Returns:** Collection statistics and document count

---

#### ❤️ System Health Check
```
GET /health
```

**Returns:** System status, uptime, resource usage, processing metrics

---

#### 🗑️ Delete Document
```
DELETE /documents/{file_path}
```

**Note:** Removes document from vector store and disk

---

#### 🤖 MCP Protocol Integration
```
POST /mcp
Content-Type: application/json

{
  "tool_name": "search",
  "arguments": {
    "query": "question",
    "limit": 5
  }
}
```

**For AI Agent Integration** - Enables Claude, other AI assistants to query your knowledge base

---

## 🧪 Testing

```bash
# Run functional tests
python functional_tests.py

# Run integration tests
pytest tests/integration_test/

# Run specific test file
pytest tests/integration_test/test_vector_store.py -v
```

---

## 📊 Performance Metrics

| Scenario | Time | Notes |
|----------|------|-------|
| **First run (1GB docs)** | 5-30 min | Initial processing of all documents |
| **Restart (same docs)** | <5 sec | Loads from persistent storage |
| **Add 1 new file** | 1-10 sec | Instant FileWatcher detection + processing |
| **Query 1000 docs** | 30-50ms | Semantic search via ChromaDB |
| **Search time growth** | Sublinear | Optimized vector indexing |

---

## 🏗️ Project Structure

```
local-rag/
├── src/
│   ├── __init__.py
│   ├── main.py                  # Entry point
│   ├── config.py                # Configuration & paths
│   ├── models.py                # Data models (Pydantic)
│   ├── document_processor.py    # Document parsing & chunking
│   ├── file_watcher.py          # Real-time file monitoring
│   ├── vector_store.py          # ChromaDB interface
│   ├── mcp_server.py            # FastAPI server
│   ├── state_manager.py         # Persistent state
│   └── startup_manager.py       # System orchestration
├── tests/
│   └── integration_test/
│       ├── test_document_processor.py
│       ├── test_vector_store.py
│       ├── test_mcp_server.py
│       └── test_state_manager.py
├── data/
│   ├── documents/               # 📥 Drop your files here
│   ├── processed/               # internal state
│   └── vector_store/            # ChromaDB storage
├── requirements.txt
├── functional_tests.py
└── README.md

```

---

## 🔧 Configuration

Edit `src/config.py` to customize:

```python
# Document Processing
CHUNK_SIZE = 1024              # Tokens per chunk
CHUNK_OVERLAP = 128            # Overlap between chunks
SUPPORTED_EXTENSIONS = ['.txt', '.pdf', '.docx']

# API Server
API_HOST = "0.0.0.0"
API_PORT = 8000

# Embedding Model
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Vector Store
COLLECTION_NAME = "rag_documents"
```

---

## 🚨 Troubleshooting

### "ModuleNotFoundError: No module named 'chromadb'"
```bash
pip install chromadb==1.0.13
```

### "No documents found" after adding files
- Ensure files are in `data/documents/` (not subdirectories by default)
- Check `data/processed/processing.log` for errors
- Verify file encoding is UTF-8

### "Connection refused" on http://localhost:8000
- Server may still be starting (wait 3-5 seconds)
- Check if port 8000 is in use: `lsof -i :8000` (Linux/Mac)
- Try a different port in `config.py`

### Memory usage growing
- Large documents (>100MB) may not be ideal
- Consider splitting documents into smaller files
- Monitor with `python -c "import psutil; print(psutil.virtual_memory())"`

---

## 🎓 Use Cases

### 1️⃣ Internal Knowledge Base
Drop internal documentation, policies, and guidelines into `data/documents/`. Teams query via Slack bot integration.

### 2️⃣ Documentation Search
Enable semantic search on your API docs, user guides, and tutorials.

### 3️⃣ RAG-Powered AI Assistants
Integrate with Claude or other AI models via MCP protocol for context-aware responses.

### 4️⃣ Research Tool
Researchers can upload papers and quickly find relevant sections.

---

## 🔐 Security Considerations

⚠️ **Current State:** Designed for trusted environments
- No authentication (use behind VPN/firewall)
- No encryption at rest
- CORS enabled for all origins

**For Production (Future):**
- Add JWT authentication
- Enable HTTPS/TLS
- Implement rate limiting
- Add input validation
- Encrypt sensitive metadata

---

## 🤝 Contributing

We welcome contributions! Here's how:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with clear commit messages
4. Add tests for new functionality
5. Submit a pull request

**Please ensure:**
- Code follows PEP 8 style guide
- All tests pass (`pytest tests/`)
- Documentation is updated
- Commit messages are descriptive

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **ChromaDB** - Vector database
- **FastAPI** - Web framework
- **Sentence Transformers** - Embeddings
- **Watchdog** - File monitoring
- **LangChain** - Text processing

---

## 📞 Support

- 📖 [Documentation](./docs/) - Detailed guides
- 🐛 [Issues](https://github.com/subashnalam/LocalRag/issues) - Report bugs
- 💬 [Discussions](https://github.com/subashnalam/LocalRag/discussions) - Ask questions

---

## 🗺️ Roadmap

- [ ] Support for Azure OpenAI embeddings
- [ ] Web UI dashboard
- [ ] Batch import/export
- [ ] Document versioning
- [ ] Advanced filtering and metadata queries
- [ ] Performance optimization (indexing improvements)
- [ ] Docker containerization
- [ ] Multi-user support with authentication

---

**Built with ❤️ by Subash Nalam**

⭐ If you find this useful, please star the repository!
