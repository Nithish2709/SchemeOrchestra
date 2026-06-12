"""
Initialize SQLite + ChromaDB RAG System
Run this once to migrate data and build indexes
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from data.migrate_to_sqlite import create_database, migrate_schemes_from_json, verify_migration
from data.chroma_rag import ChromaRAGEngine
from data.eligibility_rules.sqlite_engine import get_all_schemes


def initialize_system():
    """Complete initialization of SQLite + ChromaDB"""
    
    print("="*60)
    print("SchemeOrchestra - Database Initialization")
    print("="*60)
    
    # Step 1: Create SQLite database
    print("\n[1/3] Creating SQLite database...")
    create_database()
    
    # Step 2: Migrate JSON data to SQLite
    print("\n[2/3] Migrating scheme data from JSON...")
    count = migrate_schemes_from_json()
    verify_migration()
    
    # Step 3: Build ChromaDB RAG index
    print("\n[3/3] Building ChromaDB RAG index...")
    engine = ChromaRAGEngine()
    schemes = get_all_schemes()
    engine.index_schemes(schemes)
    
    print("\n" + "="*60)
    print("[OK] Initialization Complete!")
    print("="*60)
    print(f"\nDatabase: {count} schemes migrated")
    print(f"RAG Index: {engine.collection.count()} documents indexed")
    print("\nYou can now run the bot: python main.py")


if __name__ == "__main__":
    initialize_system()
