import os
from pathlib import Path
from loguru import logger
import sys

# --- Directories ---
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
VECTOR_STORE_PATH = DATA_DIR / "vector_store"
DOCUMENTS_DIR = DATA_DIR / "documents"
PROCESSED_DIR = DATA_DIR / "processed"

# --- File Watching ---
WATCH_DIRECTORY = str(DOCUMENTS_DIR)
SUPPORTED_EXTENSIONS = [".pdf", ".docx", ".txt", ".md", ".html", ".csv", ".json"]
RECURSIVE_WATCH = True
PROCESSING_DELAY_MS = 500
MAX_RETRY_ATTEMPTS = 3

# --- Document Processing ---
CHUNK_SIZE = 512
CHUNK_OVERLAP = 51
MAX_FILE_SIZE_MB = 100

# --- Vector Store ---
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
COLLECTION_NAME = "documents"
COLLECTION_STRATEGY = "single"  # or "per_type"

# --- MCP Server ---
MCP_HOST = "localhost"
MCP_PORT = 8000
API_KEY = os.getenv("API_KEY", None)  # Optional authentication

# --- Logging ---
LOG_LEVEL = "INFO"
LOG_FILE = LOGS_DIR / "rag_system.log"
LOG_MAX_SIZE = "10 MB"
LOG_BACKUP_COUNT = 5
LOG_ROTATION = "size"  # "size", "time", or "both"

# --- Performance ---
BATCH_SIZE = 10
WORKER_THREADS = 4
CHUNK_CACHE_SIZE = 1000

def setup_logging():
    """Configures loguru for console and file logging."""
    logger.remove()
    logger.add(
        sys.stdout,
        level=LOG_LEVEL,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )
    logger.add(
        LOG_FILE,
        level=LOG_LEVEL,
        rotation=LOG_MAX_SIZE,
        retention=f"{LOG_BACKUP_COUNT} days",
        compression="zip",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
    )

def ensure_directories_exist():
    """Ensure all necessary directories exist."""
    for dir_path in [DATA_DIR, DOCUMENTS_DIR, PROCESSED_DIR, VECTOR_STORE_PATH, LOGS_DIR]:
        dir_path.mkdir(parents=True, exist_ok=True)
