# Local RAG System with MCP Server

A production-grade Retrieval Augmented Generation (RAG) system 
with Model Context Protocol (MCP) server integration, 
built for intelligent document querying and developer knowledge management.

## What This Does
Drop documents into a watched folder — the system automatically 
ingests, chunks, embeds, and stores them in a vector database. 
Query your entire knowledge base in natural language via REST API 
or MCP protocol.

## Architecture
- **Document Ingestion**: Automated file watcher detects and 
  processes new documents in real time
- **Vector Storage**: ChromaDB for persistent embedding storage 
  and semantic search
- **LLM Integration**: OpenAI API for embedding generation 
  and response synthesis
- **MCP Server**: Model Context Protocol server for AI-native 
  tool integration
- **State Management**: Application state and startup lifecycle 
  management
- **Observability**: Structured logging and processing audit trails

## Tech Stack
- Python
- OpenAI API (embeddings + completions)
- ChromaDB (vector database)
- MCP (Model Context Protocol)
- REST API (tested via Postman/Insomnia)

## Project Structure
local-rag/
├── src/
│   ├── document_processor.py  # Document chunking and embedding
│   ├── file_watcher.py        # Automated document ingestion
│   ├── vector_store.py        # ChromaDB abstraction layer
│   ├── mcp_server.py          # MCP protocol server
│   ├── state_manager.py       # Application state management
│   ├── startup_manager.py     # Lifecycle management
│   └── models.py              # Data models
├── tests/
│   └── integration_test/      # Full integration test suite
├── data/
│   ├── documents/             # Drop documents here
│   └── vector_store/          # ChromaDB persistent storage

## How to Run
# Install dependencies
pip install -r requirements.txt

# Add your OpenAI API key to .env
OPENAI_API_KEY=your_key_here

# Start the system
python main.py

# Query via REST API
POST /query
{"question": "your question here"}

## Testing
python functional_tests.py        # Functional tests
pytest tests/integration_test/    # Integration tests

## Key Features
- Real-time document watching and automatic ingestion
- Persistent vector storage with ChromaDB
- MCP server for AI agent integration
- Comprehensive test coverage
- Structured logging and audit trails
- Document processing state management
```

---

## Your Resume Bullet Points — Copy These

Under a new section called **"GenAI Projects"** or **"Technical Projects":**

> **Local RAG System with MCP Integration** *(Personal Project)*
> - Designed and built a production-grade RAG pipeline with automated document ingestion, ChromaDB vector storage, and OpenAI API integration
> - Implemented Model Context Protocol (MCP) server enabling AI-native tool integration — a standard introduced by Anthropic in 2024
> - Built real-time file watcher for automated document processing with state management and startup lifecycle control
> - Developed comprehensive test suite including unit, functional, and integration tests
> - Exposed as REST API, tested with Postman and Insomnia across multiple test cycles

---

## How to Explain This in 60 Seconds in an Interview

> "I built a local RAG system for developer knowledge management. It automatically watches a folder — when you drop a document in, it processes, chunks, embeds and stores it in ChromaDB automatically. You can then query your entire document base in natural language via REST API. What makes it different is I also built an MCP server on top of it — MCP is Anthropic's Model Context Protocol, a new standard for connecting AI models to external tools. So AI agents can directly query my system as a tool. I wrote integration tests, functional tests, architecture docs, and issue logs throughout the build."

That answer in an interview will make people sit up. Guaranteed.

---

## Immediate Next Steps — Today

**1. Clean before pushing to GitHub**
Remove these before pushing:
- `.env` file — contains your API key, never push this
- Issue log txt files — keep the md ones, remove txt clutter
- `chroma.sqlite3` and binary files in vector_store — add to `.gitignore`

**Add a `.gitignore` with:**
```
.env
*.sqlite3
data/vector_store/
logs/
__pycache__/
*.pyc
