import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import pytest
import os
from pathlib import Path
from src.state_manager import StateManager
from src import config

# A more robust fixture using pytest's built-in tools
@pytest.fixture
def manager_with_temp_env(tmp_path, monkeypatch):
    """
    A fixture that provides a StateManager instance configured to use
    a temporary, isolated directory structure.
    """
    # 1. Create a realistic but temporary directory structure
    docs_dir = tmp_path / "documents"
    docs_dir.mkdir()
    processed_dir = tmp_path / "processed"
    processed_dir.mkdir()

    # 2. Safely override the config for the duration of the test
    monkeypatch.setattr(config, 'PROCESSED_DIR', processed_dir)

    # 3. Create a manager instance
    manager = StateManager()
    
    # 4. Yield the manager and the paths for the test to use
    yield manager, docs_dir

# --- Individual, focused tests ---

@pytest.mark.asyncio
async def test_detects_new_file(manager_with_temp_env):
    """Verify that a newly created file is identified for processing."""
    manager, docs_dir = manager_with_temp_env
    (docs_dir / "new_file.txt").write_text("some content")

    await manager.load_existing_state()
    files_to_process = manager.get_files_to_process(str(docs_dir))

    assert len(files_to_process) == 1
    assert str(docs_dir / "new_file.txt") in files_to_process

@pytest.mark.asyncio
async def test_ignores_unchanged_file_after_processing(manager_with_temp_env):
    """Verify that a processed file is not re-processed on a subsequent run."""
    manager, docs_dir = manager_with_temp_env
    file_path_str = str(docs_dir / "file1.txt")
    (docs_dir / "file1.txt").write_text("content")

    # First run: process the file
    signature = manager.get_content_signature(file_path_str)
    manager.mark_file_processed(file_path_str, signature)
    await manager.save_state()

    # Second run: create a new manager to simulate app restart
    new_manager = StateManager()
    await new_manager.load_existing_state() # Should load from the temp dir
    files_to_process = new_manager.get_files_to_process(str(docs_dir))

    assert not files_to_process # The set should be empty

@pytest.mark.asyncio
async def test_detects_modified_file(manager_with_temp_env):
    """Verify that a file with changed content is re-processed."""
    manager, docs_dir = manager_with_temp_env
    file_path = docs_dir / "file_to_modify.txt"
    file_path.write_text("original content")

    # First run
    signature = manager.get_content_signature(str(file_path))
    manager.mark_file_processed(str(file_path), signature)
    await manager.save_state()

    # Modify the file
    file_path.write_text("UPDATED content")

    # Second run
    new_manager = StateManager()
    await new_manager.load_existing_state()
    files_to_process = new_manager.get_files_to_process(str(docs_dir))

    assert str(file_path) in files_to_process

@pytest.mark.asyncio
async def test_detects_deleted_file(manager_with_temp_env):
    """Verify that sync correctly identifies a deleted file."""
    manager, docs_dir = manager_with_temp_env
    file_to_delete = docs_dir / "file_to_delete.txt"
    file_to_delete.write_text("i will be deleted")

    # Process and save state
    signature = manager.get_content_signature(str(file_to_delete))
    manager.mark_file_processed(str(file_to_delete), signature)
    await manager.save_state()

    # Now, delete the file from the disk
    os.remove(file_to_delete)

    # Sync and check for deleted files
    new_manager = StateManager()
    await new_manager.load_existing_state()
    deleted_files = new_manager.sync_and_get_deleted_files(str(docs_dir))

    assert str(file_to_delete) in deleted_files
