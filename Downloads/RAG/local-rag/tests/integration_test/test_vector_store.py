import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import pytest
from src.vector_store import VectorStore
from pathlib import Path

@pytest.fixture
def vector_store_with_temp_db(tmp_path):
    """
    A fixture that provides a VectorStore instance initialized with
    a temporary, isolated ChromaDB database.
    """
    # The persist_directory will be a unique temp folder created by pytest
    persist_directory = str(tmp_path / "test_chroma_db")
    
    store = VectorStore(persist_directory=persist_directory)
    
    yield store
    
    # No explicit cleanup needed; tmp_path handles directory removal.

@pytest.mark.asyncio
async def test_add_and_search_document(vector_store_with_temp_db):
    """Verify that document chunks can be added and then found via search."""
    store = vector_store_with_temp_db
    await store.initialize()
    file_path = "test/doc1.txt"
    normalized_path = str(Path(file_path).resolve())
    chunks = [
        {"content": "The sky is blue.", "metadata": {"source": file_path, "chunk": 0}},
        {"content": "The grass is green.", "metadata": {"source": file_path, "chunk": 1}},
    ]

    await store.add_document_chunks(file_path, chunks)

    # Check collection stats
    stats = store.get_collection_stats()
    assert stats['total_documents'] == 2

    # Search for content
    search_results = await store.search("blue sky")
    
    assert len(search_results) > 0
    assert search_results[0]['metadata']['source'] == normalized_path
    assert "The sky is blue" in search_results[0]['content']

@pytest.mark.asyncio
async def test_remove_document(vector_store_with_temp_db):
    """Verify that all chunks for a document are removed correctly."""
    store = vector_store_with_temp_db
    await store.initialize()
    file_path = "test/doc_to_delete.txt"
    chunks = [
        {"content": "This document will be removed.", "metadata": {"source": file_path, "chunk": 0}}
    ]

    await store.add_document_chunks(file_path, chunks)
    assert store.get_collection_stats()['total_documents'] == 1

    await store.remove_document(file_path)
    
    assert store.get_collection_stats()['total_documents'] == 0
    
    # Verify it's gone by searching
    search_results = await store.search("removed")
    assert len(search_results) == 0

@pytest.mark.asyncio
async def test_update_document_by_re_adding(vector_store_with_temp_db):
    """Verify that re-adding chunks for a file path updates the content."""
    store = vector_store_with_temp_db
    await store.initialize()
    file_path = "test/doc_to_update.txt"
    normalized_path = str(Path(file_path).resolve())
    initial_chunks = [
        {"content": "This is the original version.", "metadata": {"source": file_path, "chunk": 0}}
    ]
    updated_chunks = [
        {"content": "This is the updated version.", "metadata": {"source": file_path, "chunk": 0}}
    ]

    # Add initial version
    await store.add_document_chunks(file_path, initial_chunks)
    assert store.get_collection_stats()['total_documents'] == 1

    # Search for original content
    results1 = await store.search("original version")
    assert len(results1) == 1

    # Add updated version (this should replace the old one)
    await store.add_document_chunks(file_path, updated_chunks)
    assert store.get_collection_stats()['total_documents'] == 1 # Count should not increase

    # Search for updated content
    results2 = await store.search("updated version")
    assert len(results2) == 1
    
    # Search for the original content again, it should be gone
    results3 = await store.search("original version")
    assert all("original version" not in r["content"] for r in results3)
    
    # Verify that the metadata contains the normalized path
    results4 = await store.search("updated version")
    assert results4[0]['metadata']['source'] == normalized_path

@pytest.mark.asyncio
async def test_get_collection_stats(vector_store_with_temp_db):
    """Verify that collection stats are reported correctly."""
    store = vector_store_with_temp_db
    await store.initialize()
    
    # Initial state
    stats1 = store.get_collection_stats()
    assert stats1['total_documents'] == 0
    assert stats1['collection_name'] == store.collection_name

    # After adding a document
    file_path = "test/stats_doc.txt"
    chunks = [
        {"content": "Chunk 1", "metadata": {"source": file_path, "chunk": 0}},
        {"content": "Chunk 2", "metadata": {"source": file_path, "chunk": 1}},
    ]
    await store.add_document_chunks(file_path, chunks)
    
    stats2 = store.get_collection_stats()
    assert stats2['total_documents'] == 2
