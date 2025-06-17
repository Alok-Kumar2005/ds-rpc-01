from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List, Any
from logger import logging
from llm_config import chunk_overlap, chunk_size

import sys
import os
from pathlib import Path

# Add the app directory to Python path
app_dir = Path(__file__).parent.parent
sys.path.append(str(app_dir))
from exception import CustomException

class TextSplitter:
    def __init__(self, chunk_size: int = chunk_size, chunk_overlap: int = chunk_overlap):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap
        )
        logging.info(f"TextSplitter initialized with chunk_size={self.chunk_size} and chunk_overlap={self.chunk_overlap}")

    def split_text(self, documents: List[Any]) -> List[Any]:
        """Split text into smaller chunks."""
        try:
            logging.info("Starting text splitting process.")
            split_docs = self.text_splitter.split_documents(documents)
            logging.info(f"Text splitting completed. Number of chunks created: {len(split_docs)}")
            return split_docs
        except Exception as e:
            logging.error(f"Error occurred while splitting text: {str(e)}")
            raise CustomException(e, sys) from e