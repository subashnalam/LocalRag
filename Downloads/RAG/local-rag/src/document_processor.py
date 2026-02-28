"""
V2: Only processes new/changed files
CRITICAL: This prevents 1GB datasets from reprocessing on every startup
"""
import logging
from typing import List, Dict
from datetime import datetime
import os
from src import config
import fitz  # PyMuPDF
import docx
from langchain_text_splitters import RecursiveCharacterTextSplitter

class DocumentProcessor:
    def __init__(self, vector_store, state_manager):
        """V2: Accepts a shared StateManager instance"""
        self.vector_store = vector_store
        self.state_manager = state_manager
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1024,
            chunk_overlap=128,
            length_function=len,
            separators=["\n\n", "\n", ". ", ", ", " ", ""],
        )
        
    async def process_changed_files_only(self):
        """MAIN METHOD: Only process files that actually changed"""
        
        files_to_process = self.state_manager.get_files_to_process(str(config.DOCUMENTS_DIR))
        
        if not files_to_process:
            logging.info("No new or changed files found - skipping processing")
            return
            
        logging.info(f"Found {len(files_to_process)} files to process")
        
        # Process in batches for performance
        batch_size = 5
        file_list = list(files_to_process)
        for i in range(0, len(file_list), batch_size):
            batch = file_list[i:i + batch_size]
            await self.process_file_batch(batch)
            
        # Save state after processing all batches
        await self.state_manager.save_state()
        
    async def process_file_batch(self, file_paths: list):
        """Process multiple files efficiently"""
        
        for file_path in file_paths:
            try:
                # Get current signature before processing
                signature = self.state_manager.get_content_signature(file_path)
                
                # Extract and process content
                content = self.extract_text(file_path)
                if not content:
                    logging.warning(f"No content extracted from {file_path}, skipping.")
                    continue

                chunks = self.chunk_content(content, file_path)
                
                # Add to vector store
                await self.vector_store.add_document_chunks(file_path, chunks)
                
                # Mark as processed with its signature
                self.state_manager.mark_file_processed(file_path, signature)
                
                logging.info(f"Processed: {file_path} ({len(chunks)} chunks)")
                
            except Exception as e:
                logging.error(f"Failed to process {file_path}: {e}", exc_info=True)
                
    def extract_text(self, file_path: str) -> str:
        """Extract text from various file formats"""
        extension = os.path.splitext(file_path)[1].lower()
        text = ""
        try:
            if extension == ".pdf":
                doc = fitz.open(file_path)
                text = "".join(page.get_text() for page in doc)
                doc.close()
            elif extension == ".docx":
                doc = docx.Document(file_path)
                text = "\n".join([para.text for para in doc.paragraphs])
            elif extension in [".txt", ".md"]:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
        except Exception as e:
            logging.error(f"Error extracting text from {file_path}: {e}")
        return text
        
    def chunk_content(self, content: str, file_path: str) -> List[Dict]:
        """Create chunks with metadata"""
        raw_chunks = self.text_splitter.split_text(content)
        chunks = []
        
        for i, chunk_content in enumerate(raw_chunks):
            chunks.append({
                'content': chunk_content,
                'metadata': {
                    'source': file_path,
                    'chunk_index': i,
                    'total_chunks': len(raw_chunks),
                    'processing_time': datetime.now().isoformat()
                }
            })
        return chunks
