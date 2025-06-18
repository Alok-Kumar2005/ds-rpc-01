import sys
import os
from pathlib import Path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.Storage.keyword_ret import KeywordRetrieverManager
from app.Storage.vectors import VectorDatabaseManager
from app.dataloader.Database import VectorDB
from langchain.retrievers import BM25Retriever, EnsembleRetriever



# 1. Initialize both managers
vector_manager = VectorDatabaseManager()
keyword_manager = KeywordRetrieverManager()

# 2. Get the vector retriever (from your vector database)
vector_db = VectorDB("path/to/engineering_master_doc.md", "eng_db")
vector_retriever = vector_db.load_existing_db().as_retriever(search_kwargs={"k": 2})

# 3. Get the keyword retriever
keyword_retriever = keyword_manager.get_retriever("eng_keyword")

print("+"*100)

print(keyword_retriever.invoke("What is the engineering Microservices"))

# 4. Create ensemble retriever
ensemble = EnsembleRetriever(
    retrievers=[vector_retriever, keyword_retriever],
    weights=[0.7, 0.3]  # 70% vector, 30% keyword
)
print("+"*100)
print(ensemble.invoke("What is the engineering Microservices"))