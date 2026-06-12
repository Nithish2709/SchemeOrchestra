from google import genai
from config.settings import GEMINI_API_KEY
from tools.unified_search import search_schemes_by_query
import json
import re

_client = genai.Client(api_key=GEMINI_API_KEY)


def search_scheme_info(query: str, lang: str = "en", user_profile: dict = None) -> str:
    """Search and recommend schemes based on user query using ChromaDB RAG + LLM.
    If user_profile is provided, filters by eligibility.
    """
    
    # Use unified search (ChromaDB RAG + optional profile filtering)
    matching_schemes = search_schemes_by_query(query, user_profile=user_profile, top_k=10)
    
    # Build context message
    if user_profile and len(user_profile) >= 3:
        query_context = f"Based on your profile and search query '{query}', here are schemes you're eligible for:"
    else:
        query_context = f"Here are schemes matching your query '{query}':"
    
    if not matching_schemes:
        # Fallback to external web search
        from tools.search_tool import search_tool
        web_results = search_tool(query)
        if not web_results or (len(web_results) > 0 and "error" in web_results[0]):
            return "No schemes found matching your query. Please try different keywords." if lang == "en" else "உங்கள் தேடலுக்கு திட்டங்கள் கிடைக்கவில்லை. வேறு வார்த்தைகளை முயற்சிக்கவும்."
        
        web_context = "Web Search Results:\n"
        for res in web_results[:5]:
            web_context += f"- {res.get('title', '')}: {res.get('snippet', '')} (URL: {res.get('link', '')})\n"
            
        fallback_prompt = f"""You are helping students in Tamil Nadu find government schemes and exams.
User Query: {query}
Language: {'English' if lang == 'en' else 'Tamil'}

{web_context}

Task: We couldn't find matching schemes in our local database, but we found these web results. 
Answer the user's query using the web results. Provide a helpful, conversational response.
Recommend they apply or find more info via the provided URLs.
Respond in {'English' if lang == 'en' else 'Tamil'}.
"""
        try:
            kwargs = {
                "model": "gemini-2.5-flash",
                "contents": fallback_prompt
            }
            if lang == "ta":
                from config.prompts import TAMIL_SYSTEM_PROMPT
                from google.genai import types
                kwargs["config"] = types.GenerateContentConfig(system_instruction=TAMIL_SYSTEM_PROMPT)
            else:
                from config.prompts import ENGLISH_SYSTEM_PROMPT
                from google.genai import types
                kwargs["config"] = types.GenerateContentConfig(system_instruction=ENGLISH_SYSTEM_PROMPT)
                
            response = _client.models.generate_content(**kwargs)
            return re.sub(r'\*', '', response.text)
        except Exception:
            return "No schemes found matching your query. Please try different keywords." if lang == "en" else "உங்கள் தேடலுக்கு திட்டங்கள் கிடைக்கவில்லை. வேறு வார்த்தைகளை முயற்சிக்கவும்."
    
    # Prepare scheme data for LLM
    scheme_summaries = []
    for s in matching_schemes[:10]:  # Limit to 10 for context size
        scheme_summaries.append({
            "scheme_id": s.get("scheme_id"),
            "name_en": s.get("name_en"),
            "name_ta": s.get("name_ta"),
            "description_en": s.get("description_en"),
            "description_ta": s.get("description_ta"),
            "category": s.get("category"),
            "benefits": s.get("benefit_value", ""),
            "apply_url": s.get("apply_url"),
        })
    
    # Add user profile context to prompt if available
    profile_context = ""
    if user_profile and len(user_profile) >= 3:
        profile_summary = f"Age: {user_profile.get('age', 'N/A')}, Education: {user_profile.get('education_level', 'N/A')}"
        profile_context = f"\nUser Profile: {profile_summary}\nNote: These schemes are already filtered to match user's eligibility.\n"
    
    # Use LLM to intelligently recommend schemes
    prompt = f"""You are helping students in Tamil Nadu find government schemes.

User Query: {query}
Language: {'English' if lang == 'en' else 'Tamil'}{profile_context}

Available Schemes:
{json.dumps(scheme_summaries, indent=2, ensure_ascii=False)}

Task: {query_context}
Recommend the most relevant 2-3 schemes from the list above.
Provide a natural, conversational response explaining:
1. Which schemes match their needs
2. Brief description of each scheme
3. Benefits they'll get
4. Where to apply (use the apply_url)

Respond in {'English' if lang == 'en' else 'Tamil'}.
Always end with: "Would you like YouTube video explanations for any of these schemes?"
"""
    
    try:
        kwargs = {
            "model": "gemini-2.5-flash",
            "contents": prompt
        }
        if lang == "ta":
            from config.prompts import TAMIL_SYSTEM_PROMPT
            from google.genai import types
            kwargs["config"] = types.GenerateContentConfig(system_instruction=TAMIL_SYSTEM_PROMPT)
        else:
            from config.prompts import ENGLISH_SYSTEM_PROMPT
            from google.genai import types
            kwargs["config"] = types.GenerateContentConfig(system_instruction=ENGLISH_SYSTEM_PROMPT)
            
        response = _client.models.generate_content(**kwargs)
        return re.sub(r'\*', '', response.text)
    except Exception as e:
        # Fallback to simple list
        from utils.formatter import format_eligible_schemes
        return format_eligible_schemes(matching_schemes[:3], lang)
