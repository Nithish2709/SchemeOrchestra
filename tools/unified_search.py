"""
Unified Search Interface
Routes between SQLite (eligibility) and ChromaDB (free-text RAG)
"""
from typing import List, Dict
from data.eligibility_rules.sqlite_engine import check_eligibility as sql_check, get_scheme_by_id, get_all_schemes
from data.chroma_rag import search_schemes_rag


def _hybrid_search(query: str, base_schemes: List[Dict], top_k: int) -> List[Dict]:
    query_lower = query.lower().strip()
    
    scored_schemes = []
    for s in base_schemes:
        score = 0
        name_en = (s.get('name_en') or '').lower()
        name_ta = (s.get('name_ta') or '').lower()
        desc_en = (s.get('description_en') or '').lower()
        desc_ta = (s.get('description_ta') or '').lower()
        
        if query_lower == name_en or query_lower == name_ta:
            score += 100
        elif query_lower in name_en or query_lower in name_ta:
            score += 50
            
        query_words = set(query_lower.split())
        stop_words = {"the", "a", "an", "for", "to", "in", "of", "and", "scheme", "yojana", "திட்டம்"}
        query_words = query_words - stop_words
        
        for word in query_words:
            if len(word) < 3: continue
            if word in name_en or word in name_ta:
                score += 10
            elif word in desc_en or word in desc_ta:
                score += 3
                
        scored_schemes.append((score, s))
        
    scored_schemes.sort(key=lambda x: x[0], reverse=True)
    
    # Add strong keyword matches first
    final_schemes = []
    seen_ids = set()
    
    # Check if the user is asking for a specific scheme by name
    is_specific_query = any(word in query_lower for word in ['scheme', 'yojana', 'thittam', 'திட்டம்'])
    
    strong_matches = [s for score, s in scored_schemes if score >= 50]
    
    if is_specific_query and not strong_matches:
        # The user is asking for a specific scheme, but we don't have it in our database.
        # Return an empty list so the orchestrator falls back to web search.
        import logging
        logging.info(f"Specific scheme not found locally for query: {query}. Triggering web search fallback.")
        return []

    for s in strong_matches:
        final_schemes.append(s)
        seen_ids.add(s['scheme_id'])
        
    # Add RAG results
    try:
        rag_scheme_ids = search_schemes_rag(query, top_k=top_k*2)
        base_ids = {s['scheme_id'] for s in base_schemes}
        for sid in rag_scheme_ids:
            if sid in base_ids and sid not in seen_ids:
                s = next((x for x in base_schemes if x['scheme_id'] == sid), None)
                if s:
                    final_schemes.append(s)
                    seen_ids.add(sid)
    except Exception as e:
        import logging
        logging.error(f"RAG search failed: {e}")
                
    # Add weak keyword matches
    weak_matches = [s for score, s in scored_schemes if 0 < score < 50]
    for s in weak_matches:
        if s['scheme_id'] not in seen_ids:
            final_schemes.append(s)
            seen_ids.add(s['scheme_id'])
            
    return final_schemes[:top_k]


def search_schemes_unified(query: str = None, user_profile: dict = None, top_k: int = 5) -> List[Dict]:
    """
    Unified search interface
    """
    
    if user_profile and len(user_profile) >= 3:
        schemes = sql_check(user_profile)
        if query:
            return _hybrid_search(query, schemes, top_k)
        return schemes
    
    elif query:
        all_schemes = get_all_schemes()
        return _hybrid_search(query, all_schemes, top_k)
    
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
