from typing import Optional, List
from utils.logger import logger
import json
import os
from datetime import datetime
import uuid


class VectorStore:
    """Simple in-memory vector store for document storage and retrieval"""
    
    def __init__(self):
        self.documents = {}  # Store document text by document_id
        self.summaries = {}  # Store summaries by document_id
        self.metadata = {}   # Store metadata by document_id
        self.conversations = {}  # Store conversations by document_id
    
    def store_document(self, document_id: str, text: str, summary: dict, 
                      metadata: dict) -> bool:
        """Store document text, summary, and metadata"""
        try:
            self.documents[document_id] = text
            self.summaries[document_id] = summary
            self.metadata[document_id] = {
                **metadata,
                "stored_at": datetime.now().isoformat(),
                "document_id": document_id
            }
            self.conversations[document_id] = []
            
            logger.info(f"Document stored: {document_id}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to store document: {str(e)}", exc_info=True)
            return False
    
    def get_document(self, document_id: str) -> Optional[dict]:
        """Retrieve document with its summary and metadata"""
        try:
            if document_id not in self.documents:
                logger.warning(f"Document not found: {document_id}")
                return None
            
            return {
                "document_id": document_id,
                "text": self.documents[document_id],
                "summary": self.summaries.get(document_id),
                "metadata": self.metadata.get(document_id)
            }
        
        except Exception as e:
            logger.error(f"Failed to retrieve document: {str(e)}", exc_info=True)
            return None
    
    def search_documents(self, query: str, top_k: int = 3) -> List[dict]:
        """Simple keyword-based search"""
        try:
            results = []
            query_terms = query.lower().split()
            
            for doc_id, text in self.documents.items():
                # Simple relevance scoring based on keyword matches
                score = 0
                text_lower = text.lower()
                for term in query_terms:
                    score += text_lower.count(term)
                
                if score > 0:
                    results.append({
                        "document_id": doc_id,
                        "score": score,
                        "snippet": text[:200]
                    })
            
            # Sort by score and return top_k
            results.sort(key=lambda x: x["score"], reverse=True)
            return results[:top_k]
        
        except Exception as e:
            logger.error(f"Search failed: {str(e)}", exc_info=True)
            return []
    
    def add_conversation_message(self, document_id: str, role: str, 
                                content: str) -> Optional[str]:
        """Add a message to conversation history"""
        try:
            if document_id not in self.conversations:
                self.conversations[document_id] = []
            
            message = {
                "role": role,
                "content": content,
                "timestamp": datetime.now().isoformat()
            }
            
            self.conversations[document_id].append(message)
            logger.info(f"Message added to conversation: {document_id}")
            return message["timestamp"]
        
        except Exception as e:
            logger.error(f"Failed to add message: {str(e)}", exc_info=True)
            return None
    
    def get_conversation_history(self, document_id: str) -> List[dict]:
        """Get conversation history for a document"""
        try:
            return self.conversations.get(document_id, [])
        
        except Exception as e:
            logger.error(f"Failed to retrieve conversation: {str(e)}", exc_info=True)
            return []
    
    def delete_document(self, document_id: str) -> bool:
        """Delete a document and its conversation history"""
        try:
            if document_id in self.documents:
                del self.documents[document_id]
            if document_id in self.summaries:
                del self.summaries[document_id]
            if document_id in self.metadata:
                del self.metadata[document_id]
            if document_id in self.conversations:
                del self.conversations[document_id]
            
            logger.info(f"Document deleted: {document_id}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to delete document: {str(e)}", exc_info=True)
            return False
    
    def list_documents(self) -> List[dict]:
        """List all stored documents with metadata"""
        try:
            documents = []
            for doc_id in self.documents.keys():
                documents.append(self.metadata.get(doc_id, {"document_id": doc_id}))
            
            return documents
        
        except Exception as e:
            logger.error(f"Failed to list documents: {str(e)}", exc_info=True)
            return []
    
    def get_document_text(self, document_id: str) -> Optional[str]:
        """Get raw document text"""
        return self.documents.get(document_id)
    
    def get_document_summary(self, document_id: str) -> Optional[dict]:
        """Get document summary"""
        return self.summaries.get(document_id)


# Global vector store instance
vector_store = VectorStore()
