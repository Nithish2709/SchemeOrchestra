"""Updated scheme lookup tool using ChromaDB RAG"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.unified_search import scheme_lookup_tool as unified_lookup


def scheme_lookup_tool(query: str) -> list[dict]:
    """
    Search schemes by keyword using ChromaDB RAG.
    If query is empty, return all schemes.
    """
    return unified_lookup(query)
