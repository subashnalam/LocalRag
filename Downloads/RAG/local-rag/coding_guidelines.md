# Local RAG System - Coding Guidelines

## Overview
This document establishes strict coding standards and architectural patterns for the Local RAG System project. These guidelines ensure consistency, maintainability, and high-quality code across all development phases. Adherence to these standards is mandatory.

## 0. Guiding Principles

### 0.1 AI Assistant Autonomy
The AI assistant must not make significant architectural or technical decisions without explicit user approval. This includes, but is not limited to:
- Changing core libraries or frameworks (e.g., switching a database, web framework).
- Substantially altering the project's architecture as defined in `local_rag_architecture.md`.
- Introducing new services or components that are not outlined in the initial plan.

If a technical roadblock is encountered, the assistant must present the problem, propose solutions, and wait for user direction before implementing a change.

## 1. Project Architecture Standards

### 1.1 Directory Structure (MANDATORY)
The project must follow the architecture defined in `local_rag_architecture.md`.

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
└── .env                    # Environment variables
```

### 1.2 File Naming Conventions
- **Modules**: `snake_case.py` (e.g., `document_processor.py`)
- **Classes**: `PascalCase` (e.g., `FileWatcher`)
- **Functions**: `snake_case` (e.g., `extract_pdf_text`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `SUPPORTED_EXTENSIONS`)
- **Test Files**: `test_module_name.py` (e.g., `test_vector_store.py`)

## 2. Code Structure Standards

### 2.1 Class Definition Pattern (MANDATORY)
Classes must be well-documented, use type hinting, and follow a logical structure.

```python
from typing import Dict, Any

class MyService:
    """
    A brief description of the class purpose.

    Attributes:
        dependency (Any): Description of the dependency.
        config (Dict[str, Any]): Configuration dictionary.
    """

    def __init__(self, dependency: Any, config: Dict[str, Any]):
        """
        Initializes the MyService instance.

        Args:
            dependency (Any): An injected dependency.
            config (Dict[str, Any]): A dictionary of configuration options.
        
        Raises:
            ValueError: If a required config option is missing.
        """
        if not dependency:
            raise ValueError("Dependency is required.")
        
        self.dependency = dependency
        self.config = config
        self._validate_config()

    def _validate_config(self) -> None:
        """Validate the provided configuration."""
        required_keys = ['key1', 'key2']
        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"Missing required config key: {key}")

    def public_method(self, data: str) -> bool:
        """
        Description of the public method.

        Args:
            data (str): Input data for the method.

        Returns:
            bool: True on success, False otherwise.
        """
        self._private_helper(data)
        return True

    def _private_helper(self, data: str) -> None:
        """A private helper method (indicated by a leading underscore)."""
        print(f"Processing data: {data}")

```

### 2.2 Function Definition Standards
Functions must include type hints and a comprehensive docstring.

```python
from typing import List, Optional

def process_documents(file_paths: List[str], chunk_size: int = 512) -> Optional[List[str]]:
    """
    Processes a list of documents, extracts text, and chunks it.

    Args:
        file_paths (List[str]): A list of paths to the documents.
        chunk_size (int): The desired size for text chunks.

    Returns:
        Optional[List[str]]: A list of text chunks, or None if an error occurs.
    
    Raises:
        FileNotFoundError: If a file in file_paths does not exist.
    """
    try:
        # Implementation here
        chunks = []
        for path in file_paths:
            # ... processing logic ...
            pass
        return chunks
    except FileNotFoundError as e:
        # Log the error
        raise e
    except Exception as e:
        # Log the error
        return None
```

## 3. Data Models and Types (Pydantic)

Data models must be defined using `Pydantic` for automatic validation, serialization, and clear schema definition.

### 3.1 Document Metadata Model
```python
# src/models.py
from pydantic import BaseModel, FilePath
from datetime import datetime

class DocumentMetadata(BaseModel):
    """Data model for a processed document's metadata."""
    file_path: FilePath
    file_name: str
    file_size: int
    modified_time: datetime
    content_type: str
    chunk_count: int
    processing_time: datetime
    content_signature: str
```

### 3.2 MCP Tool Schemas
MCP tool schemas must be defined using Pydantic to ensure requests are validated against the specification in `local_rag_architecture.md`.

```python
# src/mcp_server.py
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class SearchDocumentsParams(BaseModel):
    """Input schema for the search_documents tool."""
    query: str
    top_k: int = Field(5, ge=1, le=50)
    filter: Optional[Dict[str, Any]] = None
```

## 4. Service Layer Standards

Services should encapsulate specific business logic (e.g., file processing, vector storage) and be designed for dependency injection.

### 4.1 Vector Store Service Pattern
```python
# src/vector_store.py
import chromadb
from sentence_transformers import SentenceTransformer

class VectorStore:
    """Manages vector embeddings and similarity search."""

    def __init__(self, config):
        self.client = chromadb.PersistentClient(path=config.VECTOR_STORE_PATH)
        self.collection = self.client.get_or_create_collection(name=config.COLLECTION_NAME)
        self.encoder = SentenceTransformer(config.EMBEDDING_MODEL)

    def add_documents(self, documents, metadatas, ids):
        """Adds documents to the vector store."""
        embeddings = self.encoder.encode(documents)
        self.collection.add(
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

    def search(self, query_text, top_k=5):
        """Searches for similar documents."""
        query_embedding = self.encoder.encode([query_text])
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=top_k
        )
        return results
```

## 5. Error Handling and Logging

Use `loguru` for logging. Implement a centralized setup in `config.py` or a dedicated logging module.

### 5.1 Logging Setup (`loguru`)
```python
# src/config.py
from loguru import logger
import sys

def setup_logging(config):
    """Configures loguru for console and file logging."""
    logger.remove()
    logger.add(
        sys.stdout,
        level=config.LOG_LEVEL
    )
    logger.add(
        config.LOG_FILE,
        level=config.LOG_LEVEL,
        rotation=config.LOG_MAX_SIZE,
        retention="10 days",
        compression="zip"
    )
```

### 5.2 Error Handling in Practice
```python
from loguru import logger

def process_file(file_path):
    try:
        # ... file processing logic ...
        logger.info(f"Successfully processed {file_path}")
    except Exception as e:
        logger.error(f"Failed to process {file_path}: {e}")
        # Optionally, re-raise or handle the exception
```

## 6. Code Quality Standards

### 6.1 Linting and Formatting
- **Formatter**: `black` for uncompromising code formatting.
- **Linter**: `flake8` with plugins (`flake8-bugbear`, `flake8-comprehensions`).
- Configuration for these tools should be in `pyproject.toml`.

### 6.2 Pre-commit Hooks
Use `pre-commit` to automatically run `black` and `flake8` before each commit to enforce standards.

```yaml
# .pre-commit-config.yaml
repos:
-   repo: https://github.com/psf/black
    rev: 23.11.0
    hooks:
    -   id: black
-   repo: https://github.com/pycqa/flake8
    rev: 6.1.0
    hooks:
    -   id: flake8
```

## 7. Testing Standards (`pytest`)

- All major functions and class methods must have corresponding unit tests.
- Use `pytest` as the testing framework.
- Employ mocking (`unittest.mock` or `pytest-mock`) to isolate units.

### 7.1 Unit Test Template
```python
# tests/test_document_processor.py
import pytest
from src.document_processor import extract_pdf_text

def test_extract_pdf_text_success(mocker):
    """Tests successful text extraction from a PDF."""
    # Arrange
    mock_fitz_open = mocker.patch('fitz.open')
    mock_doc = mocker.MagicMock()
    mock_page = mocker.MagicMock()
    mock_page.get_text.return_value = "Hello world"
    mock_doc.__iter__.return_value = [mock_page]
    mock_fitz_open.return_value = mock_doc
    
    # Act
    text, _ = extract_pdf_text("dummy.pdf")
    
    # Assert
    assert text == "Hello world"
    mock_fitz_open.assert_called_once_with("dummy.pdf")

def test_extract_pdf_text_file_not_found(mocker):
    """Tests behavior when the file does not exist."""
    # Arrange
    mocker.patch('fitz.open', side_effect=FileNotFoundError("File not found"))
    
    # Act & Assert
    with pytest.raises(FileNotFoundError):
        extract_pdf_text("nonexistent.pdf")
```

## 8. Security Standards

### 8.1 Input Sanitization
- Sanitize all inputs from external sources, including file paths and MCP requests.
- Be cautious with file system operations; validate paths to prevent directory traversal attacks.

### 8.2 API Key Management
- Load sensitive information (like API keys) from environment variables (`.env` file) using a library like `python-dotenv`.
- Never hardcode secrets in the source code.
- Add `.env` to `.gitignore`.

## 9. Documentation Standards

### 9.1 Code Documentation
- **Docstrings**: All modules, classes, and functions must have Google-style docstrings.
- **Type Hinting**: Use Python's `typing` module for all function signatures and variable annotations.

### 9.2 Project Documentation
- **README.md**: The main `README.md` should provide a project overview, setup instructions, and usage examples.
- **architecture.md**: The `local_rag_architecture.md` document is the source of truth for the system's design and must be kept up-to-date.
