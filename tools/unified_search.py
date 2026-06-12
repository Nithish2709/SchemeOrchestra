"""
Unified Search Interface
Routes between SQLite (eligibility) and ChromaDB (free-text RAG)
"""
from typing import List, Dict
from data.eligibility_rules.sqlite_engine import check_eligibility as sql_check, get_scheme_by_id, get_all_schemes
from data.chroma_rag import search_schemes_rag


def search_schemes_unified(query: str = None, user_profile: dict = None, top_k: int = 5) -> List[Dict]:
    """
    Unified search interface
    
    Routes to:
    - SQLite: When user_profile is provided (eligibility-based)
    - ChromaDB RAG: When query is provided (free-text search)
    
    Args:
        query: Free-text search query (Tamil or English)
        user_profile: User profile dict with eligibility criteria
        top_k: Number of results for RAG search
    
    Returns:
        List of scheme dictionaries
    """
    
    # Route 1: Eligibility-based search (SQLite)
    if user_profile and len(user_profile) >= 3:
        schemes = sql_check(user_profile)
        
        # If query provided, filter results by query relevance
        if query:
            scheme_ids_from_rag = search_schemes_rag(query, top_k=15)
            # Filter eligible schemes to those matching query
            schemes = [s for s in schemes if s['scheme_id'] in scheme_ids_from_rag]
        
        return schemes
    
    # Route 2: Free-text RAG search (ChromaDB)
    elif query:
        # Get top matching scheme IDs from RAG
        scheme_ids = search_schemes_rag(query, top_k=top_k)
        
        # Fetch full details from SQLite
        schemes = []
        for scheme_id in scheme_ids:
            scheme = get_scheme_by_id(scheme_id)
            if scheme:
                schemes.append(scheme)
        
        return schemes
    
    # Route 3: No filter - return all schemes
    else:
        return get_all_schemes()


def search_schemes_by_profile(user_profile: dict) -> List[Dict]:
    """
    Search schemes based on user eligibility profile
    Uses SQLite eligibility engine
    """
    return sql_check(user_profile)


def search_schemes_by_query(query: str, user_profile: dict = None, top_k: int = 5) -> List[Dict]:
    """
    Search schemes using free-text query with optional profile filtering
    
    Args:
        query: Search query (Tamil or English)
        user_profile: Optional profile to filter by eligibility
        top_k: Number of results
    
    Returns:
        List of schemes matching query (and profile if provided)
    """
    return search_schemes_unified(query=query, user_profile=user_profile, top_k=top_k)


def get_scheme_details(scheme_id: str) -> Dict:
    """Get detailed information for a specific scheme"""
    return get_scheme_by_id(scheme_id)


def list_all_schemes() -> List[Dict]:
    """Get all active schemes"""
    return get_all_schemes()


# Backward compatibility aliases
def scheme_lookup_tool(query: str) -> List[Dict]:
    """
    Backward compatible with old fuzzy search
    Uses ChromaDB RAG instead
    """
    if not query or query.strip() == "":
        return get_all_schemes()
    return search_schemes_by_query(query, top_k=10)


def eligibility_check_tool(user_profile: dict) -> List[Dict]:
    """
    Backward compatible with old eligibility checker
    Uses SQLite engine instead
    """
    return search_schemes_by_profile(user_profile)
