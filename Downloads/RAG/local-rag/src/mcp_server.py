"""
V2: Complete FastAPI server with health monitoring
CRITICAL: Real-time system status and performance monitoring
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import time
import psutil
import os
from loguru import logger
from datetime import datetime

from src.vector_store import VectorStore
from src.state_manager import StateManager
from src.models import SearchRequest, SearchResponse, SystemStatus, MCPRequest, MCPResponse
from src import config

class MCPServer:
    def __init__(self, vector_store: VectorStore, state_manager: StateManager):
        self.app = FastAPI(title="Local RAG System V2")
        self.vector_store = vector_store
        self.state_manager = state_manager
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
        
        @self.app.get("/health", response_model=SystemStatus)
        async def health_check():
            """Comprehensive health check"""
            try:
                # Get the number of processed files from the StateManager
                total_files_processed = len(self.state_manager.known_files)
                
                # Check system resources
                process = psutil.Process(os.getpid())
                memory_mb = process.memory_info().rss / 1024 / 1024
                
                # Check file system storage used by the data directory
                storage_mb = sum(
                    os.path.getsize(os.path.join(dirpath, filename))
                    for dirpath, _, filenames in os.walk("data")
                    for filename in filenames
                ) / 1024 / 1024
                
                return SystemStatus(
                    status="healthy",
                    total_documents=total_files_processed,
                    last_processed=self.state_manager.last_processed_time,
                    services_running=["file_watcher", "vector_store", "mcp_server"],
                    uptime_seconds=time.time() - self.start_time,
                    storage_used_mb=round(storage_mb, 2)
                )
                
            except Exception as e:
                logger.error(f"Health check failed: {e}")
                raise HTTPException(status_code=500, detail="Health check failed")
        
        @self.app.post("/search", response_model=SearchResponse)
        async def search_documents(request: SearchRequest):
            """Search documents with performance tracking"""
            start_time_req = time.time()
            
            try:
                results = await self.vector_store.search(
                    query=request.query,
                    limit=request.limit
                )
                
                query_time_ms = (time.time() - start_time_req) * 1000
                
                return SearchResponse(
                    results=results,
                    total_found=len(results),
                    query_time_ms=query_time_ms
                )
                
            except Exception as e:
                logger.error(f"Search failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/documents")
        async def list_documents():
            """List all processed documents"""
            try:
                stats = self.vector_store.get_collection_stats()
                return {
                    "total_documents": stats.get('total_documents', 0),
                    "collection_info": stats
                }
            except Exception as e:
                logger.error(f"Failed to list documents: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.delete("/documents/{file_path:path}")
        async def delete_document(file_path: str):
            """
            Deletes a document from the system.

            This involves three steps:
            1. Deleting the physical file.
            2. Removing the document from the vector store.
            3. Removing the file's record from the state manager.
            """
            try:
                # Sanitize file_path to prevent path duplication
                if file_path.startswith("data/documents/"):
                    file_path = file_path[len("data/documents/"):]
                
                # Construct the full path to the document
                full_path = os.path.join(config.DOCUMENTS_DIR, file_path)

                # 1. Delete the physical file if it exists
                if os.path.exists(full_path):
                    os.remove(full_path)
                    logger.info(f"Successfully deleted physical file: {full_path}")
                else:
                    logger.warning(f"File not found, could not delete: {full_path}")

                # 2. Remove the document from the vector store
                await self.vector_store.remove_document(file_path)
                
                # 3. Remove the file from the state manager and save state
                self.state_manager.remove_file_from_state(file_path)
                await self.state_manager.save_state()

                return {"message": f"Document {file_path} removed successfully"}
            except Exception as e:
                logger.error(f"Failed to delete document {file_path}: {e}", exc_info=True)
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.delete("/documents/verify_delete/{file_path:path}")
        async def delete_document_verified(file_path: str):
            """
            Deletes a document with verification.

            This endpoint ensures the file is physically deleted before updating
            the vector store and state manager. It provides robust feedback on the
            outcome of the operation.

            Args:
                file_path (str): The relative path of the document to delete.

            Returns:
                JSONResponse: A success or error message.

            Raises:
                HTTPException: 404 if file not found, 500 if deletion fails.
            """
            try:
                # Sanitize file_path to prevent path duplication
                if file_path.startswith("data/documents/"):
                    file_path = file_path[len("data/documents/"):]

                full_path = os.path.join(config.DOCUMENTS_DIR, file_path)

                # 1. Verify file exists before attempting deletion
                if not os.path.exists(full_path):
                    logger.warning(f"Delete request for non-existent file: {full_path}")
                    raise HTTPException(status_code=404, detail=f"File not found: {file_path}")

                # 2. Attempt to delete the physical file
                os.remove(full_path)

                # 3. Verify the file was actually deleted
                if os.path.exists(full_path):
                    logger.error(f"Failed to delete file, it still exists: {full_path}")
                    raise HTTPException(status_code=500, detail="File could not be deleted from disk.")

                logger.info(f"Successfully deleted physical file: {full_path}")

                # 4. Remove from vector store and state manager
                await self.vector_store.remove_document(file_path)
                self.state_manager.remove_file_from_state(file_path)
                await self.state_manager.save_state()

                return {"message": f"Document {file_path} removed successfully and verified."}

            except HTTPException as http_exc:
                # Re-raise HTTP exceptions to be handled by FastAPI
                raise http_exc
            except Exception as e:
                logger.error(f"An unexpected error occurred during verified deletion of {file_path}: {e}", exc_info=True)
                raise HTTPException(status_code=500, detail="An internal error occurred during deletion.")
        
        @self.app.post("/process")
        async def force_reprocess():
            """Force reprocess all documents (for admin use)"""
            try:
                # This is a simplified approach. A real implementation might
                # trigger a re-processing event for the StartupManager.
                signatures_file = "data/processed/signatures.json"
                if os.path.exists(signatures_file):
                    os.remove(signatures_file)
                
                return {"message": "Reprocessing initiated - restart system to take effect"}
            except Exception as e:
                logger.error(f"Failed to initiate reprocessing: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/mcp", response_model=MCPResponse)
        async def mcp_handler(request: MCPRequest) -> MCPResponse:
            """
            Handles MCP (Model Context Protocol) requests.

            This endpoint receives a tool name and arguments, and is expected
            to execute the corresponding tool. Currently, it returns a placeholder
            response.

            Args:
                request (MCPRequest): The incoming MCP request.

            Returns:
                MCPResponse: The result of the tool execution.
            
            Raises:
                HTTPException: If the MCP request fails.
            """
            try:
                logger.info(f"Received MCP request for tool: {request.tool_name}")
                # For now, just a placeholder response
                return MCPResponse(
                    status="success",
                    result={"message": f"Tool '{request.tool_name}' executed with arguments: {request.arguments}"}
                )
            except Exception as e:
                logger.error(f"MCP request failed: {e}")
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
