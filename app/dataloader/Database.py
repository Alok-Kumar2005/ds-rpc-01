# from dataloader import DataLoader, TextSplitter
from dataload import DataLoader
from splitter import TextSplitter
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings
from llm_config import embeddings_model, huggingface_embeddings_model
from dotenv import load_dotenv
from langchain.schema import Document

import sys
import os
import time
import json
from pathlib import Path

app_dir = Path(__file__).parent.parent
sys.path.append(str(app_dir))
from logger import logging
from exception import CustomException

load_dotenv()

os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")
huggingface_api = os.getenv("HUGGINGFACE_API_KEY")


class VectorDB:
    def __init__(self, file_path: str, persist_directory: str = "db"):
        self.file_path = file_path
        self.persist_directory = persist_directory
        self.data_loader = DataLoader(file_path)
        self.text_splitter = TextSplitter()
        # self.embeddings = GoogleGenerativeAIEmbeddings(model=embeddings_model)
        self.embeddings = HuggingFaceInferenceAPIEmbeddings(
            model_name=huggingface_embeddings_model,
            api_key=huggingface_api
        )
        logging.info(f"VectorDB initialized with file_path: {self.file_path} and persist_directory: {self.persist_directory}")

    def create_vector_db(self):
        """Create a vector database from the loaded documents."""
        try:
            logging.info("Creating vector database from markdown files.")
            documents = self.data_loader.load_markdown()
            split_docs = self.text_splitter.split_text(documents)
            vector_db = Chroma.from_documents(
                split_docs,
                self.embeddings,
                persist_directory=self.persist_directory
            )
            return vector_db
        except Exception as e:
            logging.error(f"Error creating vector database: {str(e)}")
            raise CustomException(e, sys) from e

    def load_existing_db(self):
        """Load an existing vector database."""
        try:
            logging.info(f"Loading existing vector database from {self.persist_directory}")
            return Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
        except Exception as e:
            logging.error(f"Error loading existing vector database: {str(e)}")
            raise CustomException(e, sys) from e

    def add_documents(self, new_file_path: str):
        """Add new documents to existing vector database."""
        vector_db = self.load_existing_db()
        new_data_loader = DataLoader(new_file_path)
        new_documents = new_data_loader.load_markdown()
        new_split_docs = self.text_splitter.split_text(new_documents)
        vector_db.add_documents(new_split_docs)
        return vector_db

    def create_embeddings_for_text(self, text: str):
        """Create embeddings for a single text string."""
        return self.embeddings.embed_query(text)

    def create_embeddings_for_documents(self, texts: list):
        """Create embeddings for multiple text documents."""
        return self.embeddings.embed_documents(texts)

    def similarity_search(self, query: str, k: int = 4):
        """Search for similar documents in the vector database."""
        vector_db = self.load_existing_db()
        return vector_db.similarity_search(query, k=k)

    def similarity_search_with_scores(self, query: str, k: int = 4):
        """Search for similar documents with similarity scores."""
        vector_db = self.load_existing_db()
        return vector_db.similarity_search_with_score(query, k=k)

    def _validate_and_clean_documents(self, documents):
        """Validate and clean document content."""
        cleaned_docs = []
        
        for i, doc in enumerate(documents):
            try:
                # Ensure document has required attributes
                if not hasattr(doc, 'page_content'):
                    logging.warning(f"Document {i} missing page_content, skipping")
                    continue
                
                # Clean and validate content
                content = str(doc.page_content).strip()
                
                # Skip empty documents
                if not content:
                    logging.warning(f"Document {i} has empty content, skipping")
                    continue
                
                # Remove any problematic characters that might cause JSON issues
                content = content.replace('\x00', '')  # Remove null bytes
                content = content.replace('\r\n', '\n')  # Normalize line endings
                
                # Ensure content is not too long (some embeddings have limits)
                if len(content) > 8000:  # Adjust based on your model's limits
                    content = content[:8000] + "..."
                    logging.info(f"Truncated document {i} content to 8000 characters")
                
                # Create cleaned document
                cleaned_doc = Document(
                    page_content=content,
                    metadata=doc.metadata if hasattr(doc, 'metadata') else {}
                )
                cleaned_docs.append(cleaned_doc)
                
            except Exception as e:
                logging.error(f"Error processing document {i}: {str(e)}")
                continue
        
        logging.info(f"Cleaned documents: {len(cleaned_docs)} out of {len(documents)}")
        return cleaned_docs

    def _test_embeddings(self, sample_docs, max_retries=3):
        """Test embeddings with a small sample to identify issues."""
        for attempt in range(max_retries):
            try:
                logging.info(f"Testing embeddings (attempt {attempt + 1}/{max_retries})")
                
                # Test with first document
                test_doc = sample_docs[0]
                logging.info(f"Testing with document content length: {len(test_doc.page_content)}")
                
                # Test embedding creation
                embedding = self.embeddings.embed_query(test_doc.page_content[:500])  # Test with first 500 chars
                logging.info(f"Embedding test successful, dimension: {len(embedding)}")
                return True
                
            except Exception as e:
                logging.error(f"Embedding test failed (attempt {attempt + 1}): {str(e)}")
                if "rate limit" in str(e).lower() or "quota" in str(e).lower():
                    wait_time = 2 ** attempt  # Exponential backoff
                    logging.info(f"Rate limit detected, waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logging.error(f"Non-rate-limit error: {e}")
                    break
        
        return False

    def create_csv_vector_db(self):
        """Create a vector database from CSV files."""
        try:
            logging.info("Creating vector database from CSV files.")

            # File checks
            if not os.path.exists(self.file_path):
                raise FileNotFoundError(f"CSV file not found: {self.file_path}")
            if os.path.getsize(self.file_path) == 0:
                raise ValueError(f"CSV file is empty: {self.file_path}")

            # Load and inspect
            documents = self.data_loader.load_csv()
            logging.info(f"Loaded {len(documents)} documents from CSV")
            if not documents:
                raise ValueError("No documents loaded from CSV file")

            # Split
            split_docs = self.text_splitter.split_text(documents)
            logging.info(f"Split into {len(split_docs)} document chunks")
            if not split_docs:
                raise ValueError("No document chunks after splitting")

            # Persist directory for CSV
            csv_persist_dir = f"{self.persist_directory}_csv"
            os.makedirs(csv_persist_dir, exist_ok=True)

            # Create vector store
            vector_db = Chroma.from_documents(
                split_docs,
                self.embeddings,
                persist_directory=csv_persist_dir
            )
            logging.info("Vector database created successfully")
            return vector_db

        except Exception as e:
            logging.error(f"Error creating vector database from CSV: {e}")
            logging.error(f"Error type: {type(e).__name__}")
            logging.error(f"File path: {self.file_path}")
            logging.error(f"File exists: {os.path.exists(self.file_path)}")
            raise CustomException(e, sys) from e

    def load_existing_db(self):
        try:
            logging.info(f"Loading vector database from {self.persist_directory}")
            return Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
        except Exception as e:
            logging.error(f"Error loading existing vector database: {e}")
            raise CustomException(e, sys) from e

    # … include other methods (similarity_search, add_documents, etc.) unchanged …

if __name__ == "__main__":
    file_path = r"resources\data\engineering\engineering_master_doc.md"
    if not os.path.exists(file_path):
        print(f"Error: File does not exist at path: {file_path}")
        print(f"Current working directory: {os.getcwd()}")
        sys.exit(1)

    try:
        vdb = VectorDB(file_path)
        db = vdb.create_vector_db()
        print("Vector database created successfully.")
        # Example query
        results = vdb.load_existing_db().similarity_search("Tell me about company overview?", k=4)
        print("Search results:", results)
    except Exception as e:
        print(f"Error occurred: {e}")
