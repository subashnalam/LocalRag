"""
V2: Proper state persistence and fast startup
CRITICAL: Load existing data instead of rebuilding everything
"""
import os
import logging
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any
from src import config
from pathlib import Path

class VectorStore:
    def __init__(self, persist_directory: str = None):
        self.persist_directory = persist_directory or str(config.VECTOR_STORE_PATH)
        self.client = None
        self.collection = None
        self.collection_name = "rag_documents"
        
    async def initialize(self):
        """Initialize ChromaDB with persistence"""
        
        # Ensure directory exists
        os.makedirs(self.persist_directory, exist_ok=True)
        
        # Create persistent client
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=False
            )
        )
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection(self.collection_name)
            existing_count = self.collection.count()
            logging.info(f"Loaded existing collection with {existing_count} documents")
            
        except Exception:
            # Collection doesn't exist, create new one
            from chromadb.utils import embedding_functions
            embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="all-MiniLM-L6-v2"
            )
            self.collection = self.client.create_collection(
                name=self.collection_name,
                embedding_function=embedding_function
            )
            logging.info("Created new document collection")
            
    async def add_document_chunks(self, file_path: str, chunks: List[Dict]):
        """Add document chunks to vector store"""
        
        normalized_path = str(Path(file_path).resolve())
        
        # Remove existing chunks for this file (for updates)
        await self.remove_document(normalized_path)
        
        # Prepare data for ChromaDB
        documents = []
        metadatas = []
        ids = []
        
        for i, chunk in enumerate(chunks):
            chunk_id = f"{normalized_path}_{i}"
            documents.append(chunk['content'])
            # Ensure the metadata also uses the normalized path
            metadata = chunk['metadata']
            metadata['source'] = normalized_path
            metadatas.append(metadata)
            ids.append(chunk_id)
        
        # Add to collection
        if documents:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            logging.info(f"Added {len(chunks)} chunks for {file_path}")
        
    async def remove_document(self, file_path: str):
        """Remove all chunks for a specific document"""
        try:
            normalized_path = str(Path(file_path).resolve())
            # Query for existing chunks from this file
            results = self.collection.get(
                where={"source": normalized_path}
            )
            
            if results and results['ids']:
                self.collection.delete(ids=results['ids'])
                logging.info(f"Removed {len(results['ids'])} existing chunks for {normalized_path}")
                
        except Exception as e:
            logging.warning(f"Could not remove existing chunks for {file_path}: {e}")
            
    async def search(self, query: str, limit: int = 10) -> List[Dict]:
        """Search documents by similarity"""
        
        results = self.collection.query(
            query_texts=[query],
            n_results=limit,
            include=['documents', 'metadatas', 'distances']
        )
        
        # Format results
        search_results = []
        if results and results['documents']:
            for i in range(len(results['documents'][0])):
                search_results.append({
                    'content': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'score': 1 - results['distances'][0][i]  # Convert distance to similarity
                })
            
        return search_results
        
    def get_collection_stats(self) -> Dict:
        """Get collection statistics"""
        if not self.collection:
            return {
                'total_documents': 0,
                'collection_name': self.collection_name,
                'persist_directory': self.persist_directory
            }
        return {
            'total_documents': self.collection.count(),
            'collection_name': self.collection_name,
            'persist_directory': self.persist_directory
        }
