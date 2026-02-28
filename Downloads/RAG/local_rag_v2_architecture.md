# Local RAG System V2 Architecture & Implementation Guide

## System Overview

This V2 guide addresses critical issues from V1: **state persistence**, **intelligent file processing**, and **single-command startup**. The system now maintains state between runs, processes only changed files, and starts everything in one command.

### Core V2 Improvements
- ✅ **Persistent State Management** - ChromaDB state maintained between restarts
- ✅ **Smart File Processing** - Only process new/changed files using content signatures
- ✅ **Single Command Startup** - `python main.py` does everything
- ✅ **Background Initialization** - Load existing data while starting services
- ✅ **Performance Optimized** - Handle large datasets (1GB+) efficiently
- ✅ **Automatic Cleanup** - Detects and removes deleted files from the database

### Core Components Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Local RAG System V2                      │
├─────────────────────────────────────────────────────────────┤
│  Startup Manager  │  State Manager    │  Smart Processor   │
│  ──────────────   │  ────────────     │  ──────────────    │
│  • Single entry   │  • Load existing  │  • Content sigs    │
│  • Service coord  │  • State persist  │  • Skip unchanged  │
│  • Health checks  │  • Metadata sync  │  • Batch process   │
├─────────────────────────────────────────────────────────────┤
│  File Watcher     │  Document Processor  │  Vector Store   │
│  ─────────────    │  ─────────────────    │  ───────────   │
│  • Watch folder   │  • Text extraction   │  • ChromaDB     │
│  • Auto-detect    │  • Smart chunking    │  • Persistent   │
│  • File events    │  • Signature cache   │  • Fast search  │
├─────────────────────────────────────────────────────────────┤
│                    MCP Server Layer                         │
│  ─────────────────────────────────────────────────────────  │
│  • FastAPI endpoints  • Real-time status  • Health checks  │
│  • Search interface   • Document mgmt     • Performance    │
└─────────────────────────────────────────────────────────────┘
```

## 1. System Foundation V2

### Directory Structure (REQUIRED)
```
local-rag/
├── data/
│   ├── documents/          # Auto-watched folder for files
│   ├── processed/          # Document metadata cache (NEW)
│   │   ├── signatures.json # Content signatures cache
│   │   └── processing.log  # Processing history
│   └── vector_store/       # ChromaDB persistent storage
│       ├── chroma.sqlite3  # ChromaDB database
│       └── [collection_id]/ # Vector data files
├── src/
│   ├── startup_manager.py  # NEW: Single startup coordinator
│   ├── state_manager.py    # NEW: State persistence logic
│   ├── file_watcher.py     # File monitoring service
│   ├── document_processor.py # Smart text processing
│   ├── vector_store.py     # ChromaDB with persistence
│   ├── mcp_server.py       # FastAPI + MCP server
│   ├── models.py           # UPDATED: Complete data models
│   └── config.py           # Configuration management
├── logs/
│   ├── startup.log         # Startup process logs
│   ├── processing.log      # Document processing logs
│   └── rag_system.log      # General system logs
├── main.py                 # SINGLE ENTRY POINT
├── requirements.txt        
├── .env                    
└── README.md              # Setup instructions
```

### Core Technologies Stack (EXACT VERSIONS)
```
# Core Dependencies
watchdog==3.0.0
chromadb==1.0.13
sentence-transformers==2.7.0
fastapi==0.111.0
uvicorn==0.29.0

# Document Processing
unstructured==0.14.5
pymupdf==1.24.5
python-docx==1.1.2
langchain-text-splitters==0.3.8

# System & Utils
pydantic==2.11.7
loguru==0.7.2
python-dotenv==0.21.0
python-magic-win64==0.4.13  # Windows only

# Optional (for testing)
requests==2.31.0
```

## 2. NEW: Startup Manager Component

### Single Entry Point (`main.py`)
```python
"""
CRITICAL: This is the ONLY script users run
Command: python main.py
Does: Everything needed to start the system
"""

import asyncio
import logging
from src.startup_manager import StartupManager

async def main():
    """Single entry point for entire RAG system"""
    startup_manager = StartupManager()
    
    try:
        # This handles everything:
        # 1. Load existing state
        # 2. Start services
        # 3. Process new files
        # 4. Monitor continuously
        await startup_manager.initialize_and_run()
    except KeyboardInterrupt:
        logging.info("Shutting down gracefully...")
        await startup_manager.shutdown()
    except Exception as e:
        logging.error(f"System startup failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
```

### Startup Manager (`src/startup_manager.py`)
```python
"""
Coordinates entire system startup and manages all services
RESPONSIBILITY: Make the system "just work" with one command
"""

class StartupManager:
    def __init__(self):
        self.state_manager = StateManager()
        self.file_watcher = None
        self.mcp_server = None
        self.vector_store = None
        
    async def initialize_and_run(self):
        """Complete system initialization and startup"""
        
        # Phase 1: Load existing state (FAST)
        logging.info("Loading existing system state...")
        await self.state_manager.load_existing_state()
        
        # Phase 2: Initialize core services (Vector Store)
        logging.info("Initializing services...")
        self.vector_store = VectorStore(persist_directory="data/vector_store")
        await self.vector_store.initialize()

        # Phase 3: Sync file state and clean up deleted files (NEW)
        logging.info("Checking for deleted files...")
        await self.cleanup_deleted_files()
        
        # Phase 4: Check for new/changed files (SMART)
        logging.info("Checking for new/changed files...")
        await self.process_file_changes()
        
        # Phase 5: Start background services
        logging.info("Starting background services...")
        await self.start_services()
        
        # Phase 6: Run continuously
        logging.info("System ready - monitoring for changes...")
        await self.run_forever()
        
    async def cleanup_deleted_files(self):
        """Remove data for files that have been deleted from the source folder"""
        deleted_files = self.state_manager.sync_and_get_deleted_files("data/documents")
        if deleted_files:
            logging.info(f"Found {len(deleted_files)} deleted files to remove.")
            for file_path in deleted_files:
                await self.vector_store.remove_document(file_path)
                self.state_manager.remove_file_from_state(file_path)
            await self.state_manager.save_state() # Persist the removal
        else:
            logging.info("No deleted files found.")

    async def process_file_changes(self):
        """Only process files that are new or changed"""
        # Pass the shared state_manager instance
        processor = DocumentProcessor(self.vector_store, self.state_manager)
        await processor.process_changed_files_only()
        
    async def start_services(self):
        """Start file watcher and MCP server"""
        # Start file watcher in background
        self.file_watcher = FileWatcher(self.vector_store)
        asyncio.create_task(self.file_watcher.start())
        
        # Start MCP server
        self.mcp_server = MCPServer(self.vector_store)
        asyncio.create_task(self.mcp_server.start())
        
    async def run_forever(self):
        """Keep system running until interrupted"""
        try:
            while True:
                await asyncio.sleep(1)
                # Optional: periodic health checks
                await self.health_check()
        except KeyboardInterrupt:
            await self.shutdown()
```

## 3. NEW: State Manager Component

### State Persistence (`src/state_manager.py`)
```python
"""
Manages persistent state between system restarts
CRITICAL: This prevents reprocessing unchanged files
"""

import json
import os
from pathlib import Path
from typing import Dict, Set
from datetime import datetime

class StateManager:
    def __init__(self):
        self.signatures_file = "data/processed/signatures.json"
        self.processing_log = "data/processed/processing.log"
        self.known_files: Dict[str, str] = {}  # file_path -> content_signature
        
    async def load_existing_state(self):
        """Load known files and their signatures from previous runs"""
        
        # Ensure processed directory exists
        os.makedirs("data/processed", exist_ok=True)
        
        # Load known file signatures
        if os.path.exists(self.signatures_file):
            with open(self.signatures_file, 'r') as f:
                self.known_files = json.load(f)
            logging.info(f"Loaded {len(self.known_files)} known files from cache")
        else:
            self.known_files = {}
            logging.info("No existing file cache found - will process all files")
            
    async def save_state(self):
        """Persist current state to disk"""
        with open(self.signatures_file, 'w') as f:
            json.dump(self.known_files, f, indent=2)
            
    def is_file_changed(self, file_path: str, current_signature: str) -> bool:
        """Check if file has changed since last processing"""
        if file_path not in self.known_files:
            return True  # New file
        return self.known_files[file_path] != current_signature
        
    def mark_file_processed(self, file_path: str, signature: str):
        """Mark file as processed with its signature"""
        self.known_files[file_path] = signature
        
        # Log processing event
        with open(self.processing_log, 'a') as f:
            f.write(f"{datetime.now().isoformat()} - Processed: {file_path}\n")
            
    def remove_file_from_state(self, file_path: str):
        """Remove a file from the state cache"""
        if file_path in self.known_files:
            del self.known_files[file_path]
            logging.info(f"Removed {file_path} from state cache.")
            
    def get_files_to_process(self, documents_dir: str) -> Set[str]:
        """Return only files that need processing"""
        files_to_process = set()
        
        for root, dirs, files in os.walk(documents_dir):
            for file in files:
                if file.startswith('.'):
                    continue
                    
                file_path = os.path.join(root, file)
                current_sig = self.get_content_signature(file_path)
                
                if self.is_file_changed(file_path, current_sig):
                    files_to_process.add(file_path)
                    
        return files_to_process
        
    def sync_and_get_deleted_files(self, documents_dir: str) -> Set[str]:
        """
        Compares cached files with disk; returns deleted file paths.
        CRITICAL: This keeps the DB in sync with the file system.
        """
        cached_files = set(self.known_files.keys())
        
        current_files = set()
        for root, _, files in os.walk(documents_dir):
            for file in files:
                if file.startswith('.'):
                    continue
                current_files.add(os.path.join(root, file))
                
        deleted_files = cached_files - current_files
        return deleted_files
        
    def get_content_signature(self, file_path: str) -> str:
        """
        HYBRID APPROACH: Fast and reliable content change detection
        - Small files (<1MB): Full content hash
        - Large files: mtime + size + partial hash (first/last 64KB)
        """
        import hashlib
        
        stat = os.stat(file_path)
        mtime = stat.st_mtime
        size = stat.st_size
        
        if size < 1024 * 1024:  # Small files: full hash
            with open(file_path, 'rb') as f:
                content_hash = hashlib.sha256(f.read()).hexdigest()
        else:  # Large files: partial hash
            with open(file_path, 'rb') as f:
                # Hash first 64KB
                first_chunk = f.read(65536)
                # Hash last 64KB
                f.seek(-65536, 2)
                last_chunk = f.read(65536)
                content_hash = hashlib.sha256(first_chunk + last_chunk).hexdigest()
        
        return f"{mtime}_{size}_{content_hash}"
```

## 4. UPDATED: Document Processor Component

### Smart Processing (`src/document_processor.py`)
```python
"""
V2: Only processes new/changed files
CRITICAL: This prevents 1GB datasets from reprocessing on every startup
"""

class DocumentProcessor:
    def __init__(self, vector_store, state_manager):
        """V2: Accepts a shared StateManager instance"""
        self.vector_store = vector_store
        self.state_manager = state_manager
        
    async def process_changed_files_only(self):
        """MAIN METHOD: Only process files that actually changed"""
        
        documents_dir = "data/documents"
        files_to_process = self.state_manager.get_files_to_process(documents_dir)
        
        if not files_to_process:
            logging.info("No new or changed files found - skipping processing")
            return
            
        logging.info(f"Found {len(files_to_process)} files to process")
        
        # Process in batches for performance
        batch_size = 5
        for i in range(0, len(files_to_process), batch_size):
            batch = list(files_to_process)[i:i + batch_size]
            await self.process_file_batch(batch)
            
        # Save state after processing
        await self.state_manager.save_state()
        
    async def process_file_batch(self, file_paths: list):
        """Process multiple files efficiently"""
        
        for file_path in file_paths:
            try:
                # Get current signature
                signature = self.state_manager.get_content_signature(file_path)
                
                # Extract and process content
                content = self.extract_text(file_path)
                chunks = self.chunk_content(content, file_path)
                
                # Add to vector store
                await self.vector_store.add_document_chunks(file_path, chunks)
                
                # Mark as processed
                self.state_manager.mark_file_processed(file_path, signature)
                
                logging.info(f"Processed: {file_path} ({len(chunks)} chunks)")
                
            except Exception as e:
                logging.error(f"Failed to process {file_path}: {e}")
                
    def extract_text(self, file_path: str) -> str:
        """Extract text from various file formats"""
        # Implementation same as V1
        pass
        
    def chunk_content(self, content: str, file_path: str) -> List[Dict]:
        """Create chunks with metadata"""
        # Implementation same as V1 but add processing_time
        chunks = []
        # ... chunking logic ...
        
        for chunk in raw_chunks:
            chunks.append({
                'content': chunk,
                'metadata': {
                    'source': file_path,
                    'chunk_index': len(chunks),
                    'processing_time': datetime.now().isoformat()
                }
            })
        return chunks
```

## 5. UPDATED: Vector Store Component

### Persistent ChromaDB (`src/vector_store.py`)
```python
"""
V2: Proper state persistence and fast startup
CRITICAL: Load existing data instead of rebuilding everything
"""

import chromadb
from chromadb.config import Settings

class VectorStore:
    def __init__(self, persist_directory: str = "data/vector_store"):
        self.persist_directory = persist_directory
        self.client = None
        self.collection = None
        self.collection_name = "rag_documents"
        
    async def initialize(self):
        """Initialize ChromaDB with persistence"""
        
        # Ensure directory exists
        os.makedirs(self.persist_directory, exist_ok=True)
        
        # Create persistent client
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=False
            )
        )
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection(self.collection_name)
            existing_count = self.collection.count()
            logging.info(f"Loaded existing collection with {existing_count} documents")
            
        except Exception:
            # Collection doesn't exist, create new one
            self.collection = self.client.create_collection(
                name=self.collection_name,
                embedding_function=self.get_embedding_function()
            )
            logging.info("Created new document collection")
            
    def get_embedding_function(self):
        """Get sentence transformer embedding function"""
        from chromadb.utils import embedding_functions
        return embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
    async def add_document_chunks(self, file_path: str, chunks: List[Dict]):
        """Add document chunks to vector store"""
        
        # Remove existing chunks for this file (for updates)
        await self.remove_document(file_path)
        
        # Prepare data for ChromaDB
        documents = []
        metadatas = []
        ids = []
        
        for i, chunk in enumerate(chunks):
            chunk_id = f"{file_path}_{i}"
            documents.append(chunk['content'])
            metadatas.append(chunk['metadata'])
            ids.append(chunk_id)
            
        # Add to collection
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        logging.info(f"Added {len(chunks)} chunks for {file_path}")
        
    async def remove_document(self, file_path: str):
        """Remove all chunks for a specific document"""
        try:
            # Query for existing chunks from this file
            results = self.collection.get(
                where={"source": file_path}
            )
            
            if results['ids']:
                self.collection.delete(ids=results['ids'])
                logging.info(f"Removed {len(results['ids'])} existing chunks for {file_path}")
                
        except Exception as e:
            logging.warning(f"Could not remove existing chunks for {file_path}: {e}")
            
    async def search(self, query: str, limit: int = 10) -> List[Dict]:
        """Search documents by similarity"""
        
        results = self.collection.query(
            query_texts=[query],
            n_results=limit,
            include=['documents', 'metadatas', 'distances']
        )
        
        # Format results
        search_results = []
        for i in range(len(results['documents'][0])):
            search_results.append({
                'content': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'score': 1 - results['distances'][0][i]  # Convert distance to similarity
            })
            
        return search_results
        
    def get_collection_stats(self) -> Dict:
        """Get collection statistics"""
        return {
            'total_documents': self.collection.count(),
            'collection_name': self.collection_name,
            'persist_directory': self.persist_directory
        }
```

## 6. UPDATED: Data Models

### Complete Models (`src/models.py`)
```python
"""
V2: Complete data models with all required fields
CRITICAL: Include processing_time and all metadata
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any

class DocumentMetadata(BaseModel):
    """Complete document metadata model"""
    source: str
    chunk_index: int
    total_chunks: int
    file_size: int
    file_type: str
    processing_time: datetime  # REQUIRED: Was missing in V1
    content_signature: str
    created_at: datetime
    updated_at: Optional[datetime] = None

class SearchRequest(BaseModel):
    """Search request model"""
    query: str
    limit: int = 10
    filter_source: Optional[str] = None

class SearchResult(BaseModel):
    """Individual search result"""
    content: str
    metadata: DocumentMetadata
    score: float

class SearchResponse(BaseModel):
    """Complete search response"""
    results: List[SearchResult]
    total_found: int
    query_time_ms: float

class SystemStatus(BaseModel):
    """System health status"""
    status: str  # "healthy", "starting", "error"
    total_documents: int
    last_processed: Optional[datetime]
    services_running: List[str]
    uptime_seconds: float
    storage_used_mb: float
```

## 7. UPDATED: MCP Server

### FastAPI + Health Endpoints (`src/mcp_server.py`)
```python
"""
V2: Complete FastAPI server with health monitoring
CRITICAL: Real-time system status and performance monitoring
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import time
import psutil
import os

class MCPServer:
    def __init__(self, vector_store: VectorStore):
        self.app = FastAPI(title="Local RAG System V2")
        self.vector_store = vector_store
        self.start_time = time.time()
        self.setup_routes()
        self.setup_middleware()
        
    def setup_middleware(self):
        """Setup CORS and other middleware"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
    def setup_routes(self):
        """Setup all API routes"""
        
        @self.app.get("/health")
        async def health_check():
            """Comprehensive health check"""
            try:
                # Check vector store
                stats = self.vector_store.get_collection_stats()
                
                # Check system resources
                memory_mb = psutil.Process().memory_info().rss / 1024 / 1024
                
                # Check file system
                storage_mb = sum(
                    os.path.getsize(os.path.join(dirpath, filename))
                    for dirpath, dirnames, filenames in os.walk("data")
                    for filename in filenames
                ) / 1024 / 1024
                
                return SystemStatus(
                    status="healthy",
                    total_documents=stats['total_documents'],
                    last_processed=datetime.now(),
                    services_running=["file_watcher", "vector_store", "mcp_server"],
                    uptime_seconds=time.time() - self.start_time,
                    storage_used_mb=storage_mb
                )
                
            except Exception as e:
                return SystemStatus(
                    status="error",
                    total_documents=0,
                    last_processed=None,
                    services_running=[],
                    uptime_seconds=time.time() - self.start_time,
                    storage_used_mb=0
                )
        
        @self.app.post("/search")
        async def search_documents(request: SearchRequest):
            """Search documents with performance tracking"""
            start_time = time.time()
            
            try:
                results = await self.vector_store.search(
                    query=request.query,
                    limit=request.limit
                )
                
                query_time_ms = (time.time() - start_time) * 1000
                
                return SearchResponse(
                    results=results,
                    total_found=len(results),
                    query_time_ms=query_time_ms
                )
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/documents")
        async def list_documents():
            """List all processed documents"""
            try:
                stats = self.vector_store.get_collection_stats()
                return {
                    "total_documents": stats['total_documents'],
                    "collection_info": stats
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.delete("/documents/{file_path:path}")
        async def delete_document(file_path: str):
            """Remove a document from the vector store"""
            try:
                await self.vector_store.remove_document(file_path)
                return {"message": f"Document {file_path} removed successfully"}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/process")
        async def force_reprocess():
            """Force reprocess all documents (for admin use)"""
            try:
                # Clear signatures cache to force reprocessing
                signatures_file = "data/processed/signatures.json"
                if os.path.exists(signatures_file):
                    os.remove(signatures_file)
                
                return {"message": "Reprocessing initiated - restart system to take effect"}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
    
    async def start(self):
        """Start the FastAPI server"""
        import uvicorn
        config = uvicorn.Config(
            app=self.app,
            host="0.0.0.0",
            port=8000,
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()
```

## 8. Performance & Scalability V2

### Startup Performance Targets
- **Cold Start** (no existing data): < 30 seconds for 1GB dataset
- **Warm Start** (existing data): < 5 seconds regardless of data size
- **File Change Detection**: < 1 second for 10,000 files
- **New File Processing**: < 10 seconds per 100MB file

### Memory Management
- **Embedding Cache**: Max 512MB RAM usage
- **Batch Processing**: Process 5 files simultaneously
- **Memory Cleanup**: Garbage collection after each batch

### Storage Optimization
- **ChromaDB**: Efficient binary storage
- **Metadata Cache**: JSON files for fast lookups
- **Log Rotation**: Prevent log files from growing too large

## 9. Deployment & Usage V2

### Single Command Startup
```bash
# Clone and setup
git clone <repo>
cd local-rag
python -m venv rag-env
source rag-env/bin/activate  # Linux/Mac
pip install -r requirements.txt

# Copy your documents
cp your-documents/* data/documents/

# Start everything (ONE COMMAND)
python main.py
```

### Expected Startup Sequence
```
[INFO] Loading existing system state...
[INFO] Loaded 245 known files from cache
[INFO] Initializing services...
[INFO] Loaded existing collection with 1,543 documents
[INFO] Checking for new/changed files...
[INFO] Found 3 files to process
[INFO] Processed: new_doc.pdf (12 chunks)
[INFO] Starting background services...
[INFO] System ready - monitoring for changes...
[INFO] Server running on http://localhost:8000
```

### Daily Usage
1. **Add new files**: Just drop them in `data/documents/` - auto-processed
2. **Query system**: Use Postman, curl, or integrate with your tools
3. **Monitor health**: Check `/health` endpoint
4. **View logs**: Check `logs/` directory for any issues

## 10. Critical Success Criteria

### ✅ System MUST satisfy these requirements:
1. **Single Command**: `python main.py` starts everything
2. **State Persistence**: Restart without reprocessing unchanged files
3. **Fast Startup**: < 5 seconds with existing data
4. **Smart Processing**: Only process new/changed files
5. **Real-time Monitoring**: `/health` endpoint shows current status
6. **Error Recovery**: System handles file errors gracefully
7. **Large Dataset Support**: Handle 1GB+ efficiently
8. **Automatic Cleanup**: System automatically removes data for files deleted from the source folder.

### 🚫 System MUST NOT:
1. Reprocess unchanged files on startup
2. Take more than 5 seconds to start with existing data
3. Require multiple commands to start
4. Lose processed data between restarts
5. Consume excessive memory (>2GB for 1GB dataset)

---

## Implementation Priority Order

### Phase 1: Critical Infrastructure
1. `src/startup_manager.py` - Single startup coordinator
2. `src/state_manager.py` - State persistence
3. Update `main.py` - Single entry point

### Phase 2: Smart Processing  
1. Update `src/document_processor.py` - Only process changed files
2. Update `src/vector_store.py` - Proper ChromaDB persistence
3. Update `src/models.py` - Complete data models

### Phase 3: Monitoring & API
1. Update `src/mcp_server.py` - Health endpoints
2. Add comprehensive logging
3. Performance optimization

**Follow this V2 architecture as your bible for development. Every component must satisfy the critical success criteria.**
