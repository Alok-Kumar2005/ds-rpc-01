import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import chromadb
from chromadb.config import Settings
import uuid
from datetime import datetime
from typing import List, Dict
import os
from app.logger import logging
from app.exception import CustomException

class LongTermMemory:
    def __init__(self, persist_directory: str = "./chroma_db"):
        try:
            self.client = chromadb.PersistentClient(
                path=persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            logging.info("ChromaDB client initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize ChromaDB: {str(e)}")
            raise CustomException(e, sys)
    
    def get_or_create_collection(self, user_email: str):
        """Get or create collection for a specific user"""
        try:
            # Sanitize email for collection name (replace @ and . with _)
            collection_name = user_email.replace("@", "_").replace(".", "_")
            collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"user_email": user_email}
            )
            return collection
        except Exception as e:
            logging.error(f"Failed to get/create collection for {user_email}: {str(e)}")
            raise CustomException(e, sys)
    
    def store_conversation(self, user_email: str, question: str, response: str, category: str = "general"):
        """Store user question and response in long-term memory"""
        try:
            collection = self.get_or_create_collection(user_email)
            
            conversation_id = str(uuid.uuid4())
            timestamp = datetime.now().isoformat()
            
            # Store the conversation
            collection.add(
                documents=[f"Question: {question}\nResponse: {response}"],
                metadatas=[{
                    "user_email": user_email,
                    "question": question,
                    "response": response,
                    "category": category,
                    "timestamp": timestamp,
                    "conversation_id": conversation_id
                }],
                ids=[conversation_id]
            )
            
            logging.info(f"Stored conversation for user {user_email}")
            return conversation_id
            
        except Exception as e:
            logging.error(f"Failed to store conversation: {str(e)}")
            raise CustomException(e, sys)
    
    def get_user_history(self, user_email: str, limit: int = 10) -> List[Dict]:
        """Retrieve user's conversation history"""
        try:
            collection = self.get_or_create_collection(user_email)
            
            results = collection.get(
                limit=limit,
                include=["metadatas", "documents"]
            )
            
            history = []
            if results['metadatas']:
                for i, metadata in enumerate(results['metadatas']):
                    history.append({
                        "question": metadata.get("question", ""),
                        "response": metadata.get("response", ""),
                        "category": metadata.get("category", "general"),
                        "timestamp": metadata.get("timestamp", ""),
                        "conversation_id": metadata.get("conversation_id", "")
                    })
            
            # Sort by timestamp (most recent first)
            history.sort(key=lambda x: x['timestamp'], reverse=True)
            return history
            
        except Exception as e:
            logging.error(f"Failed to retrieve history for {user_email}: {str(e)}")
            return []
    
    def search_user_conversations(self, user_email: str, query: str, n_results: int = 5) -> List[Dict]:
        """Search user's past conversations"""
        try:
            collection = self.get_or_create_collection(user_email)
            
            results = collection.query(
                query_texts=[query],
                n_results=n_results,
                include=["metadatas", "documents", "distances"]
            )
            
            conversations = []
            if results['metadatas'] and results['metadatas'][0]:
                for i, metadata in enumerate(results['metadatas'][0]):
                    conversations.append({
                        "question": metadata.get("question", ""),
                        "response": metadata.get("response", ""),
                        "category": metadata.get("category", "general"),
                        "timestamp": metadata.get("timestamp", ""),
                        "similarity_score": 1 - results['distances'][0][i] if results['distances'] else 0
                    })
            
            return conversations
            
        except Exception as e:
            logging.error(f"Failed to search conversations for {user_email}: {str(e)}")
            return []



longterm_memory = LongTermMemory()