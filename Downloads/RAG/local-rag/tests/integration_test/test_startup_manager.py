import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import pytest
import os
from pathlib import Path
from unittest.mock import AsyncMock

from src.startup_manager import StartupManager
from src.state_manager import StateManager
from src.vector_store import VectorStore
from src import config

@pytest.fixture
def setup_full_environment(tmp_path, monkeypatch):
    """
    Sets up a complete, isolated environment for testing the StartupManager.
    This includes directories for documents, processed state, and the vector store.
    """
    # 1. Create temporary directories
    docs_dir = tmp_path / "documents"
    docs_dir.mkdir()
    processed_dir = tmp_path / "processed"
    processed_dir.mkdir()
    vector_store_dir = tmp_path / "vector_store"
    vector_store_dir.mkdir()

    # 2. Monkeypatch the config to use these directories
    monkeypatch.setattr(config, 'DOCUMENTS_DIR', docs_dir)
    monkeypatch.setattr(config, 'PROCESSED_DIR', processed_dir)
    monkeypatch.setattr(config, 'VECTOR_STORE_PATH', vector_store_dir)
    
    # 3. Override the VectorStore's persist directory in the StartupManager's init
    # This ensures the manager uses the temp dir from the start.
    monkeypatch.setattr(
        'src.startup_manager.VectorStore', 
        lambda persist_directory: VectorStore(str(vector_store_dir))
    )

    return docs_dir, processed_dir, vector_store_dir

@pytest.mark.asyncio
async def test_startup_processes_new_and_cleans_deleted_files(setup_full_environment, monkeypatch):
    """
    Verify the main startup sequence:
    - Processes new files.
    - Removes deleted files from the state and vector store.
    """
    docs_dir, processed_dir, vector_store_dir = setup_full_environment

    # --- Setup the scenario ---
    
    # 1. A file that was processed in a "previous run" but is now deleted.
    # To simulate this, we manually create its state.
    deleted_file_path = str(docs_dir / "deleted_doc.txt")
    initial_state = {deleted_file_path: "some_old_signature"}
    with open(processed_dir / "signatures.json", 'w') as f:
        import json
        json.dump(initial_state, f)

    # 2. A new file that exists on disk and needs to be processed.
    new_file_path = docs_dir / "new_doc.txt"
    new_file_path.write_text("This is a brand new document.")

    # --- Mock long-running services ---
    # We don't want to actually start the server or watcher in a test.
    monkeypatch.setattr(StartupManager, 'start_services', AsyncMock())

    # --- Run the StartupManager ---
    manager = StartupManager()
    await manager.initialize_and_run()

    # --- Assert the results ---

    # 1. Assert that the new file was processed.
    # Check the state manager
    assert str(new_file_path) in manager.state_manager.known_files
    # Check the vector store
    search_results = await manager.vector_store.search("new document")
    assert len(search_results) == 1
    assert search_results[0]['metadata']['source'] == str(new_file_path)

    # 2. Assert that the deleted file was cleaned up.
    # Check the state manager
    assert deleted_file_path not in manager.state_manager.known_files
    # Check the vector store (should have only the new file's chunks)
    stats = manager.vector_store.get_collection_stats()
    assert stats['total_documents'] == 1
