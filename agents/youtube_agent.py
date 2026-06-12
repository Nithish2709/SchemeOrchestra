from tools.youtube_tool import youtube_tool
from tools.scheme_lookup_tool import scheme_lookup_tool


def get_youtube_recommendations(query: str, lang: str = "en") -> str:
    """Get YouTube video recommendations for schemes.
    Query can be a scheme name or general topic.
    """
    
    # Try to find matching scheme first
    schemes = scheme_lookup_tool(query)
    
    search_query = query
    context = ""
    
    if schemes:
        # Use the scheme's predefined YouTube keywords
        scheme = schemes[0]
        scheme_name = scheme.get(f"name_{lang}") or scheme.get("name_en")
        youtube_keywords = scheme.get("youtube_keywords", [])
        
        # Build context about what we're searching for
        context = f"Searching for: {scheme_name}\n\n"
        
        # Use best keyword or construct one
        if youtube_keywords:
            # Prefer language-specific keyword
            search_query = youtube_keywords[1] if lang == "ta" and len(youtube_keywords) > 1 else youtube_keywords[0]
        else:
            # Construct specific search query
            search_query = f"{scheme_name} how to apply documents required" if lang == "en" else f"{scheme_name} விண்ணப்பிக்கும் முறை"
    else:
        # Generic search - make it more specific
        if lang == "en":
            search_query = f"{query} Tamil Nadu government scheme application process"
        else:
            search_query = f"{query} தமிழ்நாடு அரசு திட்டம் விளக்கம்"
    
    results = youtube_tool(search_query, lang)
    
    if not results:
        return "No videos found." if lang == "en" else "காணொளிகள் கிடைக்கவில்லை."
    
    if "error" in results[0]:
        return f"YouTube error: {results[0]['error']}"
    
    header = "🎥 Recommended Videos:" if lang == "en" else "🎥 பரிந்துரைக்கப்பட்ட காணொளிகள்:"
    lines = [context + header, ""]
    
    for i, v in enumerate(results, 1):
        lines.append(f"{i}. {v['title']}")
        lines.append(f"   Channel: {v['channel']}")
        if v.get('description'):
            lines.append(f"   Preview: {v['description'][:100]}...")
        lines.append(f"   Link: {v['url']}")
        lines.append("")
    
    return "\n".join(lines)
