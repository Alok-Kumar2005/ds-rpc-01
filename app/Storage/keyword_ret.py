import sys
import os
import pickle
from pathlib import Path
from typing import Dict, List, Optional

# Add the app directory to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from langchain.retrievers import BM25Retriever, EnsembleRetriever
from app.dataloader.splitter import TextSplitter
from app.dataloader.dataload import DataLoader
from app.logger import logging


class KeywordRetrieverManager:
    """Manages creation and storage of BM25 keyword retrievers for different departments."""
    
    def __init__(self, base_resources_path="resources/data", retrievers_storage_path="retrievers"):
        self.base_path = Path(base_resources_path)
        self.storage_path = Path(retrievers_storage_path)
        self.storage_path.mkdir(exist_ok=True)
        
        self.data_loader = None
        self.text_splitter = TextSplitter()
        self.retrievers = {}
        
        self.retrievers_config = self._get_retrievers_config()
    
    def _get_retrievers_config(self):
        """Configuration for all keyword retrievers to be created."""
        return [
            {
                "name": "Engineering",
                "file_path": self.base_path / "engineering" / "engineering_master_doc.md",
                "retriever_name": "eng_keyword",
                "type": "markdown",
                "k": 2
            },
            {
                "name": "Finance Summary",
                "file_path": self.base_path / "finance" / "financial_summary.md",
                "retriever_name": "fin_summary_keyword",
                "type": "markdown",
                "k": 2
            },
            {
                "name": "Quarterly Financial Report",
                "file_path": self.base_path / "finance" / "quarterly_financial_report.md",
                "retriever_name": "fin_quarterly_keyword",
                "type": "markdown",
                "k": 2
            },
            {
                "name": "Employee Handbook",
                "file_path": self.base_path / "general" / "employee_handbook.md",
                "retriever_name": "general_keyword",
                "type": "markdown",
                "k": 2
            },
            {
                "name": "HR Data",
                "file_path": self.base_path / "hr" / "hr_data.csv",
                "retriever_name": "hr_keyword",
                "type": "csv",
                "k": 2
            },
            {
                "name": "Marketing Report",
                "file_path": self.base_path / "marketing" / "market_report_q4_2024.md",
                "retriever_name": "marketing_keyword",
                "type": "markdown",
                "k": 2
            }
        ]
    
    def create_single_retriever(self, config):
        """Create a single BM25 keyword retriever based on configuration."""
        try:
            logging.info(f"Starting creation of {config['name']} keyword retriever...")
            
            # Check if file exists
            if not config['file_path'].exists():
                logging.error(f"File not found: {config['file_path']}")
                print(f"❌ Error: File not found for {config['name']}")
                return None
            
            # Load data based on file type
            self.data_loader = DataLoader(str(config['file_path']))
            
            if config['type'] == 'csv':
                documents = self.data_loader.load_csv()
            else:  # markdown
                documents = self.data_loader.load_markdown()
            
            # Split text into chunks
            chunks = self.text_splitter.split_text(documents)
            
            # Create BM25 retriever
            retriever = BM25Retriever.from_documents(
                chunks, 
                k=config['k']
            )
            
            # Store retriever
            self.retrievers[config['retriever_name']] = retriever
            
            # Save retriever to disk
            self._save_retriever(retriever, config['retriever_name'])
            
            logging.info(f"{config['name']} Keyword Retriever Created Successfully")
            print(f"✅ {config['name']} Keyword Retriever Created")
            
            return retriever
            
        except Exception as e:
            logging.error(f"Error creating {config['name']} keyword retriever: {str(e)}")
            print(f"❌ Error creating {config['name']} keyword retriever: {str(e)}")
            return None
    
    def create_all_retrievers(self):
        """Create all keyword retrievers."""
        print("🔍 Starting Keyword Retriever Creation Process...")
        print("=" * 60)
        
        successful = 0
        failed = 0
        
        for config in self.retrievers_config:
            retriever = self.create_single_retriever(config)
            if retriever is not None:
                successful += 1
            else:
                failed += 1
            print("-" * 40)
        
        # Summary
        print("=" * 60)
        print(f"📊 Keyword Retriever Creation Summary:")
        print(f"   ✅ Successful: {successful}")
        print(f"   ❌ Failed: {failed}")
        print(f"   🔍 Total: {len(self.retrievers_config)}")
        
        if failed == 0:
            print("🎉 All keyword retrievers created successfully!")
            logging.info("All keyword retrievers created successfully")
        else:
            print(f"⚠️  {failed} retriever(s) failed to create. Check logs for details.")
            logging.warning(f"{failed} retriever(s) failed to create")
        
        return self.retrievers
    
    def create_specific_retriever(self, retriever_name):
        """Create a specific retriever by name."""
        config = next((ret for ret in self.retrievers_config 
                      if ret['name'].lower() == retriever_name.lower()), None)
        
        if config:
            return self.create_single_retriever(config)
        else:
            available_names = [ret['name'] for ret in self.retrievers_config]
            print(f"❌ Retriever '{retriever_name}' not found.")
            print(f"Available retrievers: {', '.join(available_names)}")
            return None
    
    def _save_retriever(self, retriever, name):
        """Save retriever to disk for later use."""
        try:
            file_path = self.storage_path / f"{name}.pkl"
            with open(file_path, 'wb') as f:
                pickle.dump(retriever, f)
            logging.info(f"Retriever {name} saved to {file_path}")
        except Exception as e:
            logging.error(f"Error saving retriever {name}: {str(e)}")
    
    def load_retriever(self, name):
        """Load a saved retriever from disk."""
        try:
            file_path = self.storage_path / f"{name}.pkl"
            if file_path.exists():
                with open(file_path, 'rb') as f:
                    retriever = pickle.load(f)
                logging.info(f"Retriever {name} loaded from {file_path}")
                return retriever
            else:
                logging.warning(f"Retriever file {file_path} not found")
                return None
        except Exception as e:
            logging.error(f"Error loading retriever {name}: {str(e)}")
            return None
    
    def get_retriever(self, name):
        """Get retriever by name (from memory or disk)."""
        # First check if it's in memory
        if name in self.retrievers:
            return self.retrievers[name]
        
        # Try to load from disk
        retriever = self.load_retriever(name)
        if retriever:
            self.retrievers[name] = retriever
            return retriever
        
        # If not found, suggest available retrievers
        available = list(self.retrievers.keys())
        print(f"❌ Retriever '{name}' not found.")
        if available:
            print(f"Available retrievers in memory: {', '.join(available)}")
        
        return None
    
    def create_ensemble_retriever(self, vector_retriever, keyword_retriever_name, weights=[0.5, 0.5]):
        """Create an ensemble retriever combining vector and keyword retrievers."""
        try:
            keyword_retriever = self.get_retriever(keyword_retriever_name)
            if keyword_retriever is None:
                logging.error(f"Keyword retriever {keyword_retriever_name} not found")
                return None
            
            ensemble = EnsembleRetriever(
                retrievers=[vector_retriever, keyword_retriever],
                weights=weights
            )
            
            logging.info(f"Ensemble retriever created with {keyword_retriever_name}")
            return ensemble
            
        except Exception as e:
            logging.error(f"Error creating ensemble retriever: {str(e)}")
            return None
    
    def list_available_retrievers(self):
        """List all available retrievers."""
        print("📋 Available Keyword Retrievers:")
        print("-" * 40)
        
        for config in self.retrievers_config:
            status = "✅ In Memory" if config['retriever_name'] in self.retrievers else "💾 On Disk"
            file_exists = "📁 File Exists" if config['file_path'].exists() else "❌ File Missing"
            
            print(f"• {config['name']}")
            print(f"  Retriever: {config['retriever_name']}")
            print(f"  Status: {status}")
            print(f"  File: {file_exists}")
            print(f"  Path: {config['file_path']}")
            print("-" * 40)


def main():
    """Main function to execute keyword retriever creation."""
    try:
        # Initialize the manager
        manager = KeywordRetrieverManager()
        
        # Create all retrievers
        retrievers = manager.create_all_retrievers()
        
        # Example usage
        print("\n🔍 Example Usage:")
        print("-" * 30)
        
        # Test a retriever
        eng_retriever = manager.get_retriever("eng_keyword")
        if eng_retriever:
            print("✅ Engineering retriever ready for use")
            # Example search (uncomment to test)
            # results = eng_retriever.get_relevant_documents("data layer")
            # print(f"Found {len(results)} relevant documents")
        
        # List all available retrievers
        print("\n")
        manager.list_available_retrievers()
        
    except Exception as e:
        logging.error(f"Critical error in main execution: {str(e)}")
        print(f"❌ Critical error: {str(e)}")


if __name__ == "__main__":
    main()