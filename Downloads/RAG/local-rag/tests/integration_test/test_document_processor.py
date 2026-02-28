import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import pytest
import os
from pathlib import Path
from src.document_processor import DocumentProcessor
from src.state_manager import StateManager
from src.vector_store import VectorStore
from src import config

@pytest.fixture
def processor_with_real_dependencies(tmp_path, monkeypatch):
    """
    A fixture that sets up a full, isolated integration environment for the
    DocumentProcessor, including a real StateManager and a real VectorStore
    operating on temporary directories.
    """
    # 1. Create temporary directories for all components
    docs_dir = tmp_path / "documents"
    docs_dir.mkdir()
    processed_dir = tmp_path / "processed"
    processed_dir.mkdir()
    vector_store_dir = tmp_path / "vector_store"
    vector_store_dir.mkdir()

    # 2. Monkeypatch the config to use these temporary directories
    monkeypatch.setattr(config, 'DOCUMENTS_DIR', docs_dir)
    monkeypatch.setattr(config, 'PROCESSED_DIR', processed_dir)
    monkeypatch.setattr(config, 'VECTOR_STORE_PATH', vector_store_dir)

    # 3. Initialize the real dependencies
    state_manager = StateManager()
    
    vector_store = VectorStore(persist_directory=str(vector_store_dir))

    # 4. Initialize the DocumentProcessor with the real dependencies
    processor = DocumentProcessor(vector_store, state_manager)

    yield processor, state_manager, vector_store, docs_dir

@pytest.mark.asyncio
async def test_process_new_file(processor_with_real_dependencies):
    """Verify that a new file is processed, chunked, and added to the vector store."""
    processor, state_manager, vector_store, docs_dir = processor_with_real_dependencies
    await state_manager.load_existing_state()
    await vector_store.initialize()
    
    # Create a new document
    file_path = docs_dir / "new_doc.txt"
    file_path.write_text("This is a test document with some content.")

    # Run the processor
    await processor.process_changed_files_only()

    # Verify state was updated
    assert str(file_path) in state_manager.known_files
    
    # Verify content was added to the vector store
    stats = vector_store.get_collection_stats()
    assert stats['total_documents'] > 0
    
    search_results = await vector_store.search("test document")
    assert len(search_results) > 0
    assert search_results[0]['metadata']['source'] == str(file_path)

@pytest.mark.asyncio
async def test_skip_unchanged_file(processor_with_real_dependencies):
    """Verify that a previously processed, unchanged file is skipped."""
    processor, state_manager, vector_store, docs_dir = processor_with_real_dependencies
    await state_manager.load_existing_state()
    await vector_store.initialize()
    
    # 1. First run: process a new file
    file_path = docs_dir / "stable_doc.txt"
    file_path.write_text("This content will not change.")
    await processor.process_changed_files_only()
    
    # Get the state after the first run
    initial_doc_count = vector_store.get_collection_stats()['total_documents']
    assert initial_doc_count > 0

    # 2. Second run: process again without any changes
    # We need a new processor instance to simulate a new application run
    new_processor = DocumentProcessor(vector_store, state_manager)
    await new_processor.process_changed_files_only()

    # Verify that no new documents were added
    final_doc_count = vector_store.get_collection_stats()['total_documents']
    assert final_doc_count == initial_doc_count

@pytest.mark.asyncio
async def test_process_modified_file(processor_with_real_dependencies):
    """Verify that a modified file is re-processed and updated in the vector store."""
    processor, state_manager, vector_store, docs_dir = processor_with_real_dependencies
    await state_manager.load_existing_state()
    await vector_store.initialize()
    
    # 1. First run with original content
    file_path = docs_dir / "modified_doc.txt"
    file_path.write_text("Original version of the document.")
    await processor.process_changed_files_only()
    
    # Verify original content is searchable
    results1 = await vector_store.search("Original version")
    assert len(results1) == 1

    # 2. Second run after modifying the file
    file_path.write_text("Updated version of the document.")
    
    # Use a new processor to simulate a new run
    new_processor = DocumentProcessor(vector_store, state_manager)
    await new_processor.process_changed_files_only()

    # Verify updated content is searchable
    results2 = await vector_store.search("Updated version")
    assert len(results2) == 1
    
    # Verify old content is gone
    results3 = await vector_store.search("Original version")
    assert all("Original version" not in r["content"] for r in results3)
