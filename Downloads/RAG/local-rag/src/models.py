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
    processing_time: datetime
    # The following fields are examples and can be extended
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    content_signature: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class SearchRequest(BaseModel):
    """Search request model"""
    query: str
    limit: int = 10
    filter_source: Optional[str] = None

class SearchResult(BaseModel):
    """Individual search result"""
    content: str
    metadata: Dict[str, Any] # Keep it flexible for different metadata structures
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
    last_processed: Optional[datetime] = None
    services_running: List[str]
    uptime_seconds: float
    storage_used_mb: float

class MCPRequest(BaseModel):
    """MCP request model"""
    tool_name: str
    arguments: Dict[str, Any]

class MCPResponse(BaseModel):
    """MCP response model"""
    status: str
    result: Dict[str, Any]
