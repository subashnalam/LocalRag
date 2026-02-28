"""
Coordinates entire system startup and manages all services
RESPONSIBILITY: Make the system "just work" with one command
"""
import asyncio
import logging
from src.state_manager import StateManager
from src.vector_store import VectorStore
from src.document_processor import DocumentProcessor
from src.file_watcher import FileWatcher
from src.mcp_server import MCPServer
from src import config

class StartupManager:
    def __init__(self):
        """Initializes the StartupManager, which orchestrates all services."""
        self.state_manager = StateManager()
        self.vector_store = VectorStore(persist_directory=str(config.VECTOR_STORE_PATH))
        # Pass managers to processor
        self.document_processor = DocumentProcessor(self.vector_store, self.state_manager)
        # Pass services to server
        self.mcp_server = MCPServer(self.vector_store, self.state_manager)
        # Pass processor to watcher
        self.file_watcher = FileWatcher(self.vector_store, self.document_processor)
        
        self.tasks = []

    async def initialize_and_run(self):
        """Complete system initialization and startup."""
        
        logging.info("Phase 1: Loading existing system state...")
        await self.state_manager.load_existing_state()
        
        logging.info("Phase 2: Initializing services (Vector Store)...")
        await self.vector_store.initialize()

        logging.info("Phase 3: Syncing file state and cleaning up deleted files...")
        await self.cleanup_deleted_files()
        
        logging.info("Phase 4: Processing new and changed files...")
        await self.document_processor.process_changed_files_only()
        
        logging.info("Phase 5: Starting background services (MCP Server and File Watcher)...")
        await self.start_services()
        
        logging.info("System is fully initialized and running. Monitoring for changes.")
        # The main event loop will keep the process alive.
        # We just need to ensure the background tasks are running.
        await asyncio.gather(*self.tasks)
        
    async def cleanup_deleted_files(self):
        """Remove data for files that have been deleted from the source folder."""
        deleted_files = self.state_manager.sync_and_get_deleted_files(str(config.DOCUMENTS_DIR))
        if deleted_files:
            logging.info(f"Found {len(deleted_files)} deleted files to remove.")
            for file_path in deleted_files:
                await self.vector_store.remove_document(file_path)
                self.state_manager.remove_file_from_state(file_path)
            await self.state_manager.save_state()
        else:
            logging.info("No deleted files found.")
        
    async def start_services(self):
        """Start file watcher and MCP server as concurrent tasks."""
        # The mcp_server.start() method is blocking, so it needs to be run in a task.
        mcp_task = asyncio.create_task(self.mcp_server.start())
        self.tasks.append(mcp_task)
        
        # The file_watcher.start() method is blocking, so it also needs to be run in a task.
        watcher_task = asyncio.create_task(asyncio.to_thread(self.file_watcher.start))
        self.tasks.append(watcher_task)
        

    async def shutdown(self):
        """Gracefully shutdown the system."""
        logging.info("Shutting down services...")
        if self.file_watcher:
            self.file_watcher.stop()
        
        for task in self.tasks:
            if not task.done():
                task.cancel()
        
        await asyncio.gather(*self.tasks, return_exceptions=True)
        logging.info("All services have been shut down.")
