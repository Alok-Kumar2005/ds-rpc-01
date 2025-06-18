from dataloader import DataLoader, TextSplitter
# from dataload import DataLoader
# from splitter import TextSplitter
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings
from llm_config import embeddings_model, huggingface_embeddings_model, no_k
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
        self.embeddings = GoogleGenerativeAIEmbeddings(model=embeddings_model, google_api_key=os.getenv("GOOGLE_API_KEY"))
        # self.embeddings = HuggingFaceInferenceAPIEmbeddings(
        #     model_name=huggingface_embeddings_model,
        #     api_key=huggingface_api
        # )
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
            logging.info(f"Vector database created successfully with {len(split_docs)} documents.")
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

    def similarity_search_with_scores(self, query: str, k: int = no_k):
        """Search for similar documents with similarity scores."""
        vector_db = self.load_existing_db()
        return vector_db.similarity_search_with_score(query, k=k)

    def create_csv_vector_db(self):
        """Create a vector database from CSV files."""
        try:
            logging.info("Creating vector database from CSV files.")
            documents = self.data_loader.load_csv()
            split_docs = self.text_splitter.split_text(documents)
            vector_db = Chroma.from_documents(
                split_docs,
                self.embeddings,
                persist_directory=self.persist_directory + "_csv"
            )
            return vector_db
        except Exception as e:
            logging.error(f"Error creating vector database from CSV: {str(e)}")
            raise CustomException(e, sys) from e
    

if __name__ == "__main__":
    file_path = r"resources\data\engineering\engineering_master_doc.md"
    vector_db = VectorDB(file_path, "db")
    db = vector_db.create_vector_db()
    print("Vector database created successfully.")
    
    # Example usage
    query = "What is  Data Layer"
    print("="* 50)
    results = vector_db.similarity_search(query)
    print("Search results:", results)
