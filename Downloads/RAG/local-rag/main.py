"""
CRITICAL: This is the ONLY script users run
Command: python main.py
Does: Everything needed to start the system
"""

import asyncio
import logging
from src.startup_manager import StartupManager
from src import config

async def main():
    """Single entry point for the entire RAG system."""
    # Setup centralized logging
    config.setup_logging()
    
    # The StartupManager will now manage all services.
    # We no longer need to pass shared_state as it will own the state.
    startup_manager = StartupManager()
    
    try:
        # This single call handles everything:
        # 1. Loading existing state.
        # 2. Initializing services.
        # 3. Processing initial documents.
        # 4. Starting background monitoring (FileWatcher and MCPServer).
        await startup_manager.initialize_and_run()
    except KeyboardInterrupt:
        logging.info("System shutting down gracefully...")
        await startup_manager.shutdown()
    except Exception as e:
        logging.error(f"A critical error occurred: {e}", exc_info=True)
        # In a real production scenario, you might want to attempt a restart.
        # For now, we will just exit.
        raise

if __name__ == "__main__":
    asyncio.run(main())
