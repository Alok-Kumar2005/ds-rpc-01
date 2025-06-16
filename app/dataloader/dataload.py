from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_community.document_loaders import CSVLoader

class DataLoader:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def load_markdown(self):
        """Load markdown files."""
        loader = UnstructuredMarkdownLoader(self.file_path)
        return loader.load()

    def load_csv(self):
        """Load CSV files."""
        loader = CSVLoader(self.file_path)
        return loader.load()