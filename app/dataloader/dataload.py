from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_community.document_loaders import CSVLoader

import sys
import os
from pathlib import Path

# Add the app directory to Python path
app_dir = Path(__file__).parent.parent
sys.path.append(str(app_dir))
from logger import logging
from exception import CustomException

class DataLoader:
    def __init__(self, file_path: str):
        self.file_path = file_path
        logging.info(f"DataLoader initialized with file_path: {self.file_path}")

    def load_markdown(self):
        """Load markdown files via unstructured."""
        try:
            logging.info(f"Loading markdown file: {self.file_path}")
            loader = UnstructuredMarkdownLoader(self.file_path)
            return loader.load()
        except Exception as e:
            logging.error(f"Error loading markdown file: {e}")
            raise CustomException(e, sys) from e

    def load_csv(self):
        """Load CSV files via unstructured (pandas under the hood)."""
        try:
            logging.info(f"Loading CSV file: {self.file_path}")
            loader = CSVLoader(self.file_path)
            return loader.load()
        except Exception as e:
            logging.error(f"Error loading CSV file: {e}")
            raise CustomException(e, sys) from e