import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, AsyncMock

from src.mcp_server import MCPServer
from src.state_manager import StateManager
from src.vector_store import VectorStore

@pytest.fixture
def mock_dependencies():
    """Mocks the StateManager and VectorStore dependencies for the server."""
    mock_state_manager = MagicMock(spec=StateManager)
    mock_state_manager.known_files = {"doc1.txt": "sig1"}
    mock_state_manager.last_processed_time = "2023-10-27T10:00:00Z"

    mock_vector_store = MagicMock(spec=VectorStore)
    mock_vector_store.search = AsyncMock(return_value=[
        {"content": "search result", "metadata": {"source": "doc1.txt"}, "score": 0.9}
    ])
    mock_vector_store.get_collection_stats = MagicMock(return_value={"total_documents": 1})
    mock_vector_store.remove_document = AsyncMock()

    return mock_state_manager, mock_vector_store

@pytest.fixture
def client(mock_dependencies):
    """Provides a TestClient instance for the MCPServer with mocked dependencies."""
    mock_state_manager, mock_vector_store = mock_dependencies
    
    # We pass the mocked dependencies to the server
    server = MCPServer(vector_store=mock_vector_store, state_manager=mock_state_manager)
    
    # The TestClient wraps the FastAPI app
    with TestClient(server.app) as test_client:
        yield test_client

def test_health_check(client):
    """Test the /health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["total_documents"] == 1
    assert "uptime_seconds" in data

def test_search_documents(client):
    """Test the /search endpoint."""
    response = client.post("/search", json={"query": "test query", "limit": 5})
    assert response.status_code == 200
    data = response.json()
    assert data["total_found"] == 1
    assert data["results"][0]["content"] == "search result"

def test_list_documents(client):
    """Test the /documents endpoint."""
    response = client.get("/documents")
    assert response.status_code == 200
    data = response.json()
    assert data["total_documents"] == 1

def test_delete_document(client, mock_dependencies):
    """Test the /documents/{file_path} endpoint."""
    _, mock_vector_store = mock_dependencies
    file_path = "path/to/my/doc.txt"
    
    response = client.delete(f"/documents/{file_path}")
    
    assert response.status_code == 200
    assert response.json() == {"message": f"Document {file_path} removed successfully"}
    
    # Verify that the underlying method on the mock was called
    mock_vector_store.remove_document.assert_awaited_once_with(file_path)

def test_mcp_handler(client):
    """Test the /mcp endpoint."""
    request_data = {
        "tool_name": "example_tool",
        "arguments": {"param1": "value1"}
    }
    response = client.post("/mcp", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "result" in data
