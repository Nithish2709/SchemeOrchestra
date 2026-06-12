"""
ChromaDB RAG Search Engine
Handles free-text and Tamil search using embeddings
"""
import chromadb
from chromadb.config import Settings
from chromadb import EmbeddingFunction, Documents, Embeddings
from pathlib import Path
from typing import List, Dict
import json
from config.settings import GEMINI_API_KEY
from google import genai

class GeminiEmbeddingFunction(EmbeddingFunction):
    """Custom embedding function using the new google-genai SDK"""
    def __init__(self):
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        
    def __call__(self, input: Documents) -> Embeddings:
        embeddings = []
        for doc in input:
            response = self.client.models.embed_content(
                model='gemini-embedding-2',
                contents=doc
            )
            embeddings.append(response.embeddings[0].values)
        return embeddings

# Paths
CHROMA_PATH = Path(__file__).parent.parent / "data" / "chroma_db"
DB_PATH = Path(__file__).parent.parent / "data" / "schemes.db"

# Use Gemini for embeddings instead of local model
class ChromaRAGEngine:
    """RAG-based search using ChromaDB + Gemini embeddings"""
    
    def __init__(self):
        print("Initializing ChromaDB with Gemini Embeddings...")
        
        # Initialize custom Gemini embedding function
        self.google_ef = GeminiEmbeddingFunction()
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(CHROMA_PATH),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="schemes",
            embedding_function=self.google_ef,
            metadata={"description": "Tamil Nadu government schemes"}
        )
        
        print(f"[OK] ChromaDB initialized at {CHROMA_PATH}")
        print(f"[OK] Collection 'schemes' has {self.collection.count()} documents")
    
    def index_schemes(self, schemes: List[Dict]):
        """
        Index all schemes into ChromaDB
        Creates embeddings from concatenated text fields
        """
        print(f"\nIndexing {len(schemes)} schemes into ChromaDB...")
        
        documents = []
        metadatas = []
        ids = []
        
        for scheme in schemes:
            # Concatenate all searchable text (English + Tamil)
            text_parts = [
                scheme.get('name_en', ''),
                scheme.get('name_ta', ''),
                scheme.get('description_en', ''),
                scheme.get('description_ta', ''),
                scheme.get('category', ''),
                scheme.get('benefit_value', ''),
                scheme.get('type', '')
            ]
            
            # Join non-empty parts
            document_text = ' '.join([p for p in text_parts if p])
            
            documents.append(document_text)
            metadatas.append({
                'scheme_id': scheme['scheme_id'],
                'name_en': scheme.get('name_en') or '',
                'category': scheme.get('category') or '',
                'type': scheme.get('type') or ''
            })
            ids.append(scheme['scheme_id'])
        
        # Generate embeddings and add to ChromaDB
        # ChromaDB automatically uses the Gemini embedding function defined earlier
        print("Uploading to ChromaDB and generating Gemini embeddings...")
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        print(f"[OK] Indexed {len(documents)} schemes")
    
    def search(self, query: str, top_k: int = 5) -> List[str]:
        """
        Search schemes using free-text query (Tamil or English)
        Returns list of scheme IDs ranked by relevance
        """
        # Search in ChromaDB (automatically embeds query via Gemini)
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k
        )
        
        # Extract scheme IDs
        scheme_ids = results['ids'][0] if results['ids'] else []
        
        return scheme_ids
    
    def rebuild_index(self):
        """Rebuild the entire index from SQLite"""
        from data.eligibility_rules.sqlite_engine import get_all_schemes
        
        # Delete existing collection
        try:
            self.client.delete_collection("schemes")
            print("[OK] Deleted old collection")
        except:
            pass
        
        # Recreate collection
        self.collection = self.client.get_or_create_collection(
            name="schemes",
            embedding_function=self.google_ef,
            metadata={"description": "Tamil Nadu government schemes"}
        )
        
        # Get all schemes from SQLite
        schemes = get_all_schemes()
        
        # Index them
        self.index_schemes(schemes)


# Global instance
_rag_engine = None

def get_rag_engine():
    """Get or create RAG engine instance"""
    global _rag_engine
    if _rag_engine is None:
        _rag_engine = ChromaRAGEngine()
    return _rag_engine


def search_schemes_rag(query: str, top_k: int = 5) -> List[str]:
    """
    Main entry point for RAG search
    Returns list of scheme IDs
    """
    engine = get_rag_engine()
    return engine.search(query, top_k)


def rebuild_rag_index():
    """Rebuild RAG index from database"""
    engine = get_rag_engine()
    engine.rebuild_index()


if __name__ == "__main__":
    # Test the RAG engine
    print("Testing ChromaDB RAG Engine\n")
    
    engine = ChromaRAGEngine()
    
    # Test queries
    test_queries = [
        "laptop scheme",
        "scholarship for BC students",
        "மடிக்கணினி திட்டம்",  # Tamil: laptop scheme
        "உதவித்தொகை",  # Tamil: scholarship
        "two wheeler for women"
    ]
    
    print("\nTest Searches:")
    for query in test_queries:
        print(f"\nQuery: {query}")
        results = engine.search(query, top_k=3)
        print(f"Results: {results}")
