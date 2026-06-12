import requests
from config.settings import YOUTUBE_API_KEY


def youtube_tool(query: str, lang: str = "en") -> list[dict]:
    """Search YouTube for scheme explainer videos with better filtering."""
    url = "https://www.googleapis.com/youtube/v3/search"
    
    # Enhanced query for better results
    enhanced_query = query
    if "tamil nadu" not in query.lower() and "தமிழ்நாடு" not in query:
        enhanced_query += " Tamil Nadu government scheme" if lang == "en" else " தமிழ்நாடு அரசு திட்டம்"
    
    params = {
        "key": YOUTUBE_API_KEY,
        "q": enhanced_query,
        "part": "snippet",
        "type": "video",
        "maxResults": 5,  # Get more to filter
        "relevanceLanguage": "ta" if lang == "ta" else "en",
        "order": "relevance",  # Most relevant first
        "videoDefinition": "any",
    }
    
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        items = resp.json().get("items", [])
        
        results = []
        for i in items:
            title = i["snippet"]["title"]
            # Filter out clearly irrelevant videos
            title_lower = title.lower()
            if any(word in title_lower for word in ['song', 'music', 'movie', 'trailer', 'entertainment', 'comedy']):
                continue
                
            results.append({
                "title": title,
                "url": f"https://youtube.com/watch?v={i['id']['videoId']}",
                "channel": i["snippet"]["channelTitle"],
                "description": i["snippet"]["description"][:200],  # First 200 chars
            })
            
            if len(results) >= 3:
                break
        
        return results if results else [{"error": "No relevant videos found"}]
    except Exception as e:
        return [{"error": str(e)}]
