import sys
import os
from pathlib import Path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.Storage.keyword_ret import KeywordRetrieverManager
from app.Storage.vectors import VectorDatabaseManager
from app.dataloader.Database import VectorDB
from app.llm_config import no_k, vector_weight, keyword_weight
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
from langchain.retrievers.document_compressors import CohereRerank
from langchain.retrievers import ContextualCompressionRetriever
from app.logger import logging

base_path = Path("resources/data")
keyword_manager = KeywordRetrieverManager()

# Initialize reranker
reranker = CohereRerank(
    cohere_api_key=os.getenv("cohere_api_key"),
    model="rerank-v3.5",
    top_n=no_k
)


def create_engineering_reranker():
    """Create reranker for Engineering department."""
    try:
        logging.info("Creating Engineering reranker...")
        vector_db = VectorDB(str(base_path / "engineering" / "engineering_master_doc.md"), "eng_db")
        vector_retriever = vector_db.load_existing_db().as_retriever(search_kwargs={"k": no_k})
        keyword_retriever = keyword_manager.get_retriever("eng_keyword")
        ensemble = EnsembleRetriever(
            retrievers=[vector_retriever, keyword_retriever],
            weights=[vector_weight, keyword_weight]
        )
        engineering_reranker = ContextualCompressionRetriever(
            base_compressor=reranker,
            base_retriever=ensemble
        )
        logging.info("✅ Engineering reranker created successfully")
        return engineering_reranker
    except Exception as e:
        logging.error(f"Error creating engineering reranker: {str(e)}")
        return None


def create_finance_summary_reranker():
    """Create reranker for Finance Summary."""
    try:
        logging.info("Creating Finance Summary reranker...")
        vector_db = VectorDB(str(base_path / "finance" / "financial_summary.md"), "fin_db1")
        vector_retriever = vector_db.load_existing_db().as_retriever(search_kwargs={"k": no_k})
        keyword_retriever = keyword_manager.get_retriever("fin_summary_keyword")
        ensemble = EnsembleRetriever(
            retrievers=[vector_retriever, keyword_retriever],
            weights=[vector_weight, keyword_weight]
        )
        finance_summary_reranker = ContextualCompressionRetriever(
            base_compressor=reranker,
            base_retriever=ensemble
        )
        logging.info("✅ Finance Summary reranker created successfully")
        return finance_summary_reranker
    except Exception as e:
        logging.error(f"Error creating finance summary reranker: {str(e)}")
        return None


def create_finance_quarterly_reranker():
    """Create reranker for Quarterly Financial Report."""
    try:
        logging.info("Creating Quarterly Financial reranker...")
        vector_db = VectorDB(str(base_path / "finance" / "quarterly_financial_report.md"), "fin_db2")
        vector_retriever = vector_db.load_existing_db().as_retriever(search_kwargs={"k": no_k})
        keyword_retriever = keyword_manager.get_retriever("fin_quarterly_keyword")
        ensemble = EnsembleRetriever(
            retrievers=[vector_retriever, keyword_retriever],
            weights=[vector_weight, keyword_weight]
        )
        finance_quarterly_reranker = ContextualCompressionRetriever(
            base_compressor=reranker,
            base_retriever=ensemble
        )      
        logging.info("✅ Quarterly Financial reranker created successfully")
        return finance_quarterly_reranker     
    except Exception as e:
        logging.error(f"Error creating quarterly financial reranker: {str(e)}")
        return None


def create_general_reranker():
    """Create reranker for Employee Handbook (General)."""
    try:
        logging.info("Creating General (Employee Handbook) reranker...")
        vector_db = VectorDB(str(base_path / "general" / "employee_handbook.md"), "gen_db")
        vector_retriever = vector_db.load_existing_db().as_retriever(search_kwargs={"k": no_k})
        keyword_retriever = keyword_manager.get_retriever("general_keyword")
        ensemble = EnsembleRetriever(
            retrievers=[vector_retriever, keyword_retriever],
            weights=[vector_weight, keyword_weight]
        )
        general_reranker = ContextualCompressionRetriever(
            base_compressor=reranker,
            base_retriever=ensemble
        )       
        logging.info("✅ General reranker created successfully")
        return general_reranker      
    except Exception as e:
        logging.error(f"Error creating general reranker: {str(e)}")
        return None


def create_hr_reranker():
    """Create reranker for HR Data."""
    try:
        logging.info("Creating HR reranker...")
        vector_db = VectorDB(str(base_path / "hr" / "hr_data.csv"), "hr_db")
        vector_retriever = vector_db.load_existing_db().as_retriever(search_kwargs={"k": no_k})
        keyword_retriever = keyword_manager.get_retriever("hr_keyword")
        ensemble = EnsembleRetriever(
            retrievers=[vector_retriever, keyword_retriever],
            weights=[vector_weight, keyword_weight]
        )
        hr_reranker = ContextualCompressionRetriever(
            base_compressor=reranker,
            base_retriever=ensemble
        )
        logging.info("✅ HR reranker created successfully")
        return hr_reranker
    except Exception as e:
        logging.error(f"Error creating HR reranker: {str(e)}")
        return None


def create_marketing_reranker():
    """Create reranker for Marketing Report."""
    try:
        logging.info("Creating Marketing reranker...")
        vector_db = VectorDB(str(base_path / "marketing" / "market_report_q4_2024.md"), "mark_db")
        vector_retriever = vector_db.load_existing_db().as_retriever(search_kwargs={"k": no_k})
        keyword_retriever = keyword_manager.get_retriever("marketing_keyword")
        ensemble = EnsembleRetriever(
            retrievers=[vector_retriever, keyword_retriever],
            weights=[vector_weight, keyword_weight]
        )
        marketing_reranker = ContextualCompressionRetriever(
            base_compressor=reranker,
            base_retriever=ensemble
        )
        logging.info("✅ Marketing reranker created successfully")
        return marketing_reranker
    except Exception as e:
        logging.error(f"Error creating marketing reranker: {str(e)}")
        return None



if __name__ == "__main__":

    print("="*150)
    print("="*150)
    engineering_reranker = create_engineering_reranker()
    results = engineering_reranker.invoke("What is microservices architecture?")
    print(results)