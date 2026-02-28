import time
import asyncio
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent
from loguru import logger

from src import config
from src.document_processor import DocumentProcessor
from src.vector_store import VectorStore


class DocumentEventHandler(FileSystemEventHandler):
    """
    Handles file system events for the document directory.

    This class responds to file creation, modification, and deletion events,
    triggering document processing and vector store updates.

    Attributes:
        vector_store (VectorStore): An instance of the vector store for database operations.
        document_processor (DocumentProcessor): An instance of the document processor.
    """

    def __init__(self, vector_store: VectorStore, document_processor: DocumentProcessor):
        """
        Initializes the DocumentEventHandler.

        Args:
            vector_store (VectorStore): The vector store to interact with.
            document_processor (DocumentProcessor): The document processor to use.
        """
        self.vector_store = vector_store
        self.document_processor = document_processor
        self.is_processing = False
        self.cooldown_period = 2  # seconds

    def on_created(self, event: FileSystemEvent) -> None:
        """
        Handles file creation events.

        Args:
            event (FileSystemEvent): The event object for the created file.
        """
        if not event.is_directory:
            self._handle_event(event.src_path, "created")

    def on_modified(self, event: FileSystemEvent) -> None:
        """
        Handles file modification events.

        Args:
            event (FileSystemEvent): The event object for the modified file.
        """
        if not event.is_directory:
            self._handle_event(event.src_path, "modified")

    def on_deleted(self, event: FileSystemEvent) -> None:
        """
        Handles file deletion events.

        Args:
            event (FileSystemEvent): The event object for the deleted file.
        """
        if not event.is_directory:
            self._handle_event(event.src_path, "deleted")

    def _handle_event(self, src_path: str, event_type: str) -> None:
        """
        Generic event handler for processing file events.

        Args:
            src_path (str): The path to the file that triggered the event.
            event_type (str): The type of event (e.g., "created", "modified", "deleted").
        """
        if self.is_processing:
            logger.warning(f"Skipping event {event_type} for {src_path}, already processing.")
            return

        self.is_processing = True
        try:
            file_path = Path(src_path)
            if file_path.suffix.lower() not in config.SUPPORTED_EXTENSIONS:
                return

            logger.info(f"File {event_type}: {file_path}")
            if event_type == "created" or event_type == "modified":
                # The document processor handles adding/updating and marking state
                asyncio.run(self.document_processor.process_file_batch([str(file_path)]))

            elif event_type == "deleted":
                # For deletion, we need to remove from vector store and state manager
                asyncio.run(self.vector_store.remove_document(str(file_path)))
                self.document_processor.state_manager.remove_file_from_state(str(file_path))

        except Exception as e:
            logger.error(f"Failed to handle {event_type} for {src_path}: {e}", exc_info=True)
        finally:
            time.sleep(self.cooldown_period)
            self.is_processing = False


def process_existing_documents(vector_store: VectorStore, document_processor: DocumentProcessor) -> None:
    """
    Scans the watch directory and processes any existing documents.
    
    DEPRECATED: This function's logic is now handled by the StartupManager
    and DocumentProcessor during the initial startup sequence. It is kept
    for reference but the core logic has been deactivated to prevent bugs.
    """
    logger.info("Skipping process_existing_documents in FileWatcher.")
    logger.info("This task is now handled by the StartupManager on initialization.")
    # The logic below is commented out as it is redundant and contained a critical bug.
    # The StartupManager now correctly handles processing of existing files on startup.
    #
    # logger.info(f"Scanning for existing documents in {config.WATCH_DIRECTORY}...")
    # for file_path in Path(config.WATCH_DIRECTORY).rglob('*'):
    #     if file_path.is_file() and file_path.suffix.lower() in config.SUPPORTED_EXTENSIONS:
    #         logger.info(f"Found existing document: {file_path}")
    #         try:
    #             # BUGGY and REDUNDANT LOGIC WAS HERE
    #             # chunks, metadatas = document_processor.process_document(file_path)
    #             # if chunks:
    #             #     ids = [f"{file_path}_{i}" for i in range(len(chunks))]
    #             #     # CRITICAL BUG: Called non-existent method `add_documents`
    #             #     vector_store.add_documents(chunks, metadatas, ids)
    #             pass
    #         except Exception as e:
    #             logger.error(f"Failed to process existing document {file_path}: {e}")

class FileWatcher:
    """
    Monitors a directory for file changes and triggers document processing.

    This class sets up a watchdog observer to watch for file creation,
    modification, and deletion events in the specified directory. It uses
    a DocumentEventHandler to dispatch events to the appropriate handlers.

    Attributes:
        vector_store (VectorStore): An instance of the vector store for database operations.
        document_processor (DocumentProcessor): An instance of the document processor for handling files.
        observer (Observer): The watchdog observer instance that monitors the file system.
    """

    def __init__(self, vector_store: VectorStore, document_processor: DocumentProcessor):
        """
        Initializes the FileWatcher.

        Args:
            vector_store (VectorStore): The vector store to interact with.
            document_processor (DocumentProcessor): The document processor to use.
        
        Raises:
            ValueError: If vector_store or document_processor is not provided.
        """
        if not vector_store:
            raise ValueError("VectorStore is required.")
        if not document_processor:
            raise ValueError("DocumentProcessor is required.")
            
        self.vector_store = vector_store
        self.document_processor = document_processor
        self.observer = Observer()

    def start(self) -> None:
        """
        Starts the file watcher.
        """
        event_handler = DocumentEventHandler(self.vector_store, self.document_processor)
        self.observer.schedule(event_handler, config.WATCH_DIRECTORY, recursive=config.RECURSIVE_WATCH)
        self.observer.start()
        logger.info(f"Started watching directory: {config.WATCH_DIRECTORY}")

    def stop(self) -> None:
        """
        Stops the file watcher.
        """
        self.observer.stop()
        self.observer.join()
        logger.info("Stopped watching directory.")
