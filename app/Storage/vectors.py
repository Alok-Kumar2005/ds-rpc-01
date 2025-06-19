import sys
import os
from pathlib import Path

# Add the app directory to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.logger import logging
from app.dataloader.Database import VectorDB


class VectorDatabaseManager:
    """Manages creation of multiple vector databases for different departments."""
    
    def __init__(self, base_resources_path="resources/data"):
        self.base_path = Path(base_resources_path)
        self.databases_config = self._get_databases_config()
    
    def _get_databases_config(self):
        """Configuration for all databases to be created."""
        return [
            {
                "name": "Engineering",
                "file_path": self.base_path / "engineering" / "engineering_master_doc.md",
                "db_name": "eng_db",
                "type": "markdown"
            },
            {
                "name": "Finance Summary",
                "file_path": self.base_path / "finance" / "financial_summary.md",
                "db_name": "fin_db1",
                "type": "markdown"
            },
            {
                "name": "Quarterly Financial Report",
                "file_path": self.base_path / "finance" / "quarterly_financial_report.md",
                "db_name": "fin_db2",
                "type": "markdown"
            },
            {
                "name": "Employee Handbook",
                "file_path": self.base_path / "general" / "employee_handbook.md",
                "db_name": "gen_db",
                "type": "markdown"
            },
            {
                "name": "HR Data",
                "file_path": self.base_path / "hr" / "hr_data.csv",
                "db_name": "hr_db",
                "type": "csv"
            },
            {
                "name": "Marketing Report",
                "file_path": self.base_path / "marketing" / "market_report_q4_2024.md",
                "db_name": "mark_db",
                "type": "markdown"
            },
            {
                "name": "Marketing Report",
                "file_path": self.base_path / "marketing" / "marketing_report_2024.md",
                "db_name": "mark2_db",
                "type": "markdown"
            }
            # {
            #     "name": "Marketing Report",
            #     "file_path": self.base_path / "marketing" / "market_report_q4_2024.md",
            #     "db_name": "mark_db",
            #     "type": "markdown"
            # },
            # {
            #     "name": "Marketing Report",
            #     "file_path": self.base_path / "marketing" / "market_report_q4_2024.md",
            #     "db_name": "mark_db",
            #     "type": "markdown"
            # }
        ]
    
    def create_single_database(self, config):
        """Create a single vector database based on configuration."""
        try:
            logging.info(f"Starting creation of {config['name']} database...")
            
            # Check if file exists
            if not config['file_path'].exists():
                logging.error(f"File not found: {config['file_path']}")
                print(f"❌ Error: File not found for {config['name']}")
                return False
            
            # Create VectorDB instance
            vector_db = VectorDB(str(config['file_path']), config['db_name'])
            
            # Create database based on type
            if config['type'] == 'csv':
                db = vector_db.create_csv_vector_db()
            else:  # markdown
                db = vector_db.create_vector_db()
            
            logging.info(f"{config['name']} Database Completed Successfully")
            print(f"✅ {config['name']} Database Completed")
            return True
            
        except Exception as e:
            logging.error(f"Error creating {config['name']} database: {str(e)}")
            print(f"❌ Error creating {config['name']} database: {str(e)}")
            return False
    
    def create_all_databases(self):
        """Create all vector databases."""
        print("🚀 Starting Vector Database Creation Process...")
        print("=" * 60)
        
        successful = 0
        failed = 0
        
        for config in self.databases_config:
            if self.create_single_database(config):
                successful += 1
            else:
                failed += 1
            print("-" * 40)
        
        # Summary
        print("=" * 60)
        print(f"📊 Vector Database Creation Summary:")
        print(f"   ✅ Successful: {successful}")
        print(f"   ❌ Failed: {failed}")
        print(f"   📁 Total: {len(self.databases_config)}")
        
        if failed == 0:
            print("🎉 All vector databases created successfully!")
            logging.info("All vector databases created successfully")
        else:
            print(f"⚠️  {failed} database(s) failed to create. Check logs for details.")
            logging.warning(f"{failed} database(s) failed to create")
    
    def create_specific_database(self, database_name):
        """Create a specific database by name."""
        config = next((db for db in self.databases_config 
                      if db['name'].lower() == database_name.lower()), None)
        
        if config:
            return self.create_single_database(config)
        else:
            available_names = [db['name'] for db in self.databases_config]
            print(f"❌ Database '{database_name}' not found.")
            print(f"Available databases: {', '.join(available_names)}")
            return False


def main():
    """Main function to execute vector database creation."""
    try:
        # Initialize the manager
        manager = VectorDatabaseManager()
        
        # Create all databases
        manager.create_all_databases()
        
    except Exception as e:
        logging.error(f"Critical error in main execution: {str(e)}")
        print(f"❌ Critical error: {str(e)}")


if __name__ == "__main__":
    main()