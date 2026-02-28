"""
Manages persistent state between system restarts
CRITICAL: This prevents reprocessing unchanged files
"""

import json
import os
import logging
from pathlib import Path
from typing import Dict, Set, Optional
from datetime import datetime
from src import config

class StateManager:
    def __init__(self):
        self.signatures_file = config.PROCESSED_DIR / "signatures.json"
        self.processing_log = config.PROCESSED_DIR / "processing.log"
        self.known_files: Dict[str, str] = {}  # file_path -> content_signature
        self.last_processed_time: Optional[datetime] = None
        
    async def load_existing_state(self):
        """Load known files and their signatures from previous runs"""
        
        # Ensure processed directory exists
        config.PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
        
        # Load known file signatures
        if os.path.exists(self.signatures_file):
            with open(self.signatures_file, 'r') as f:
                self.known_files = json.load(f)
            logging.info(f"Loaded {len(self.known_files)} known files from cache")
        else:
            self.known_files = {}
            logging.info("No existing file cache found - will process all files")
            
    async def save_state(self):
        """Persist current state to disk"""
        with open(self.signatures_file, 'w') as f:
            json.dump(self.known_files, f, indent=2)
            
    def is_file_changed(self, file_path: str, current_signature: str) -> bool:
        """Check if file has changed since last processing"""
        if file_path not in self.known_files:
            return True  # New file
        return self.known_files[file_path] != current_signature
        
    def mark_file_processed(self, file_path: str, signature: str):
        """Mark file as processed with its signature"""
        self.known_files[file_path] = signature
        self.last_processed_time = datetime.now()
        
        # Log processing event
        with open(self.processing_log, 'a') as f:
            f.write(f"{self.last_processed_time.isoformat()} - Processed: {file_path}\n")
            
    def remove_file_from_state(self, file_path: str):
        """Remove a file from the state cache"""
        if file_path in self.known_files:
            del self.known_files[file_path]
            self.last_processed_time = datetime.now()
            logging.info(f"Removed {file_path} from state cache.")
            
    def get_files_to_process(self, documents_dir: str) -> Set[str]:
        """Return only files that need processing"""
        files_to_process = set()
        
        for root, dirs, files in os.walk(documents_dir):
            for file in files:
                if file.startswith('.'):
                    continue
                    
                file_path = os.path.join(root, file)
                current_sig = self.get_content_signature(file_path)
                
                if self.is_file_changed(file_path, current_sig):
                    files_to_process.add(file_path)
                    
        return files_to_process
        
    def sync_and_get_deleted_files(self, documents_dir: str) -> Set[str]:
        """
        Compares cached files with disk; returns deleted file paths.
        CRITICAL: This keeps the DB in sync with the file system.
        """
        cached_files = set(self.known_files.keys())
        
        current_files = set()
        for root, _, files in os.walk(documents_dir):
            for file in files:
                if file.startswith('.'):
                    continue
                current_files.add(os.path.join(root, file))
                
        deleted_files = cached_files - current_files
        return deleted_files
        
    def get_content_signature(self, file_path: str) -> str:
        """
        HYBRID APPROACH: Fast and reliable content change detection
        - Small files (<1MB): Full content hash
        - Large files: mtime + size + partial hash (first/last 64KB)
        """
        import hashlib
        
        stat = os.stat(file_path)
        mtime = stat.st_mtime
        size = stat.st_size
        
        if size < 1024 * 1024:  # Small files: full hash
            with open(file_path, 'rb') as f:
                content_hash = hashlib.sha256(f.read()).hexdigest()
        else:  # Large files: partial hash
            with open(file_path, 'rb') as f:
                # Hash first 64KB
                first_chunk = f.read(65536)
                # Hash last 64KB
                f.seek(-65536, 2)
                last_chunk = f.read(65536)
                content_hash = hashlib.sha256(first_chunk + last_chunk).hexdigest()
        
        return f"{mtime}_{size}_{content_hash}"
