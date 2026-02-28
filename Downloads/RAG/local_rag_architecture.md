# Local RAG System Architecture & Implementation Guide

## System Overview

This guide outlines building a simple, local RAG (Retrieval-Augmented Generation) system with automatic file ingestion, MCP (Model Context Protocol) connectivity, and seamless file management.

### Core Components Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Local RAG System                         │
├─────────────────────────────────────────────────────────────┤
│  File Watcher     │  Document Processor  │  Vector Store   │
│  ─────────────    │  ─────────────────    │  ───────────   │
│  • Watch folder   │  • Text extraction   │  • Embeddings  │
│  • Auto-detect    │  • Chunking          │  • Similarity   │
│  • File events    │  • Metadata          │  • Storage      │
├─────────────────────────────────────────────────────────────┤
│                    MCP Server Layer                         │
│  ─────────────────────────────────────────────────────────  │
│  • Query interface     • File management                    │
│  • Search endpoints    • Status monitoring                  │
├─────────────────────────────────────────────────────────────┤
│              External MCP Clients                           │
│  ───────────────────────────────────────────────────────   │
│  Cline    │    Custom Chatbot    │    Other MCP Tools      │
└─────────────────────────────────────────────────────────────┘
```

## 1. System Foundation

### Directory Structure
```
local-rag/
├── data/
│   ├── documents/          # Auto-watched folder for files
│   ├── processed/          # Processed document cache
│   └── vector_store/       # Vector database files
├── src/
│   ├── file_watcher.py     # File monitoring service
│   ├── document_processor.py # Text extraction & chunking
│   ├── vector_store.py     # Embedding & search logic
│   ├── mcp_server.py       # MCP protocol implementation
│   └── config.py           # Configuration management
├── logs/                   # System logs
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables
└── docker-compose.yml      # Optional containerization
```

### Core Technologies Stack & Versions
**Recommended Python Environment**: `venv` (simpler, lighter, better for single-purpose projects)
```bash
python -m venv rag-env
source rag-env/bin/activate  # Linux/Mac
# or rag-env\Scripts\activate  # Windows
```

**Exact Version Requirements** (`requirements.txt`):
```
watchdog==3.0.0
unstructured==0.14.5
chromadb==1.0.13
sentence-transformers==2.7.0
langchain-text-splitters==0.3.8
pymupdf==1.24.5
python-docx==1.1.2
python-magic-win64==0.4.13
fastapi==0.111.0
uvicorn==0.29.0
pydantic==2.11.7
loguru==0.7.2
python-dotenv==0.21.0
```

## 2. File Watcher Component
(This section remains unchanged)

...

## 4. Vector Store Component

### Local Vector Database Setup
1. **ChromaDB Configuration**:
   - Persistent storage in `data/vector_store/`
   - **Single collection by default** (simpler management, easier cross-document search)
   - **Configurable option** for collection per document type if needed
   - Automatic backup and recovery
2.  **Embedding Model**: Use `all-MiniLM-L6-v2` for balance of speed and quality.
3.  **Vector Dimensions**: 384 (matches embedding model).

### Content Change Detection
**Recommended**: Hybrid approach using file hash + timestamp
```python
import hashlib
import os

def get_content_signature(file_path):
    """
    Hybrid approach because:
    - File timestamps can be unreliable (copied files, git operations)
    - Content hashing is definitive but slower
    - Combination provides speed + reliability
    """
    stat = os.stat(file_path)
    mtime = stat.st_mtime
    size = stat.st_size
    
    # For small files (<1MB), compute full hash
    if size < 1024 * 1024:
        with open(file_path, 'rb') as f:
            content_hash = hashlib.sha256(f.read()).hexdigest()
    else:
        # For large files, use mtime + size + partial hash
        with open(file_path, 'rb') as f:
            # Hash first 64KB + last 64KB
            first_chunk = f.read(65536)
            f.seek(-65536, 2)
            last_chunk = f.read(65536)
            content_hash = hashlib.sha256(first_chunk + last_chunk).hexdigest()
    
    return f"{mtime}_{size}_{content_hash}"
```

### Storage Operations
- **Add Documents**: Generate embeddings, add them to the FAISS index, and append metadata to the JSON file.
- **Update Documents**: Remove all vectors and metadata associated with the file path and then re-add the document.
- **Delete Documents**: Remove vectors and clean up references
- **Search**: Cosine similarity search with configurable top-k results

### Performance Optimizations
- Batch processing for multiple documents
- **Embedding caching**: Cache based on content signature (see above)
- Incremental updates rather than full re-processing
- Memory-mapped storage for large collections

... (rest of the document remains the same, with the exception of section 10)

## 10. Performance Considerations

### Scalability Limits
- **Document Count**: ChromaDB handles 100K+ documents efficiently
- **File Size**: Recommend <100MB per file for optimal processing.
- **Concurrent Operations**: Queue system for batch processing
- **Memory Usage**: Monitor embedding cache size

... (rest of the document remains the same)
