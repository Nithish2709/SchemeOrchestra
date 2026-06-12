DISCLAIMER_EN = (
    "\n\n⚠️ _This bot provides informational guidance only. "
    "Always verify eligibility with the official government website. "
    "SchemeOrchestra is not affiliated with the Government of Tamil Nadu or Government of India._"
)
DISCLAIMER_TA = (
    "\n\n⚠️ _இந்த தகவல் வழிகாட்டுதல் மட்டுமே. "
    "அதிகாரப்பூர்வ அரசு இணையதளத்தில் தகுதியை உறுதிப்படுத்தவும். "
    "SchemeOrchestra அரசாங்கத்துடன் தொடர்புடையது அல்ல._"
)


def format_scheme(scheme: dict, lang: str = "en") -> str:
    try:
        name = scheme.get(f"name_{lang}") or scheme.get("name_en", "Unknown Scheme")
        desc = scheme.get(f"description_{lang}") or scheme.get("description_en", "")
        benefit_obj = scheme.get("benefits", {})
        benefit = benefit_obj.get("value", "N/A") if isinstance(benefit_obj, dict) else str(benefit_obj)
        url = scheme.get("apply_url", "")
        return f"🎓 {name}\n{desc}\n💰 {benefit}\n🔗 {url}"
    except Exception as e:
        from loguru import logger
        logger.exception(f"Error formatting scheme: {e}")
        return f"🎓 Scheme: {scheme.get('scheme_id', 'Unknown')}"


def format_scheme_detailed(scheme: dict, lang: str = "en") -> str:
    """Format scheme with complete details: eligibility, documents, benefits, how to apply."""
    try:
        name = scheme.get(f"name_{lang}") or scheme.get("name_en", "Unknown Scheme")
        desc = scheme.get(f"description_{lang}") or scheme.get("description_en", "")
        category = scheme.get("category", "").title()
        scheme_type = scheme.get("type", "").upper()
        
        lines = []
        lines.append(f"{'='*50}")
        lines.append(f"📋 {name}")
        lines.append(f"Type: {scheme_type} | Category: {category}")
        lines.append(f"{'='*50}")
        lines.append("")
        
        # Description
        lines.append("📖 ABOUT:" if lang == "en" else "📖 பற்றி:")
        lines.append(desc)
        lines.append("")
        
        # Eligibility Criteria
        eligibility = scheme.get("eligibility", {})
        if eligibility:
            lines.append("✅ ELIGIBILITY CRITERIA:" if lang == "en" else "✅ தகுதி விதிமுறைகள்:")
            
            if eligibility.get("target_group"):
                target = ", ".join(eligibility["target_group"])
                lines.append(f"  • Target Group: {target}")
            
            if eligibility.get("education_level"):
                edu = ", ".join(eligibility["education_level"])
                lines.append(f"  • Education: {edu}")
            
            if eligibility.get("class_range"):
                class_range = eligibility["class_range"]
                lines.append(f"  • Class: {class_range[0]} to {class_range[1]}")
            
            if eligibility.get("caste") and eligibility["caste"] != "all":
                caste = eligibility["caste"] if isinstance(eligibility["caste"], str) else ", ".join(eligibility["caste"])
                lines.append(f"  • Caste: {caste}")
            
            if eligibility.get("gender") and eligibility["gender"] != "all":
                lines.append(f"  • Gender: {eligibility['gender']}")
            
            if eligibility.get("age_min") or eligibility.get("age_max"):
                age_str = f"  • Age: "
                if eligibility.get("age_min"):
                    age_str += f"{eligibility['age_min']}+"
                if eligibility.get("age_max"):
                    age_str += f" (max {eligibility['age_max']})"
                lines.append(age_str)
            
            if eligibility.get("income_limit_annual"):
                income = eligibility["income_limit_annual"]
                lines.append(f"  • Annual Income: Below ₹{income:,}")
            
            if eligibility.get("state_resident"):
                lines.append(f"  • Must be Tamil Nadu resident")
            
            if eligibility.get("first_graduate"):
                lines.append(f"  • First generation college student")
                
            lines.append("")
        
        # Benefits
        benefits = scheme.get("benefits", {})
        if benefits:
            lines.append("💰 BENEFITS:" if lang == "en" else "💰 நன்மைகள்:")
            if isinstance(benefits, dict):
                benefit_type = benefits.get("type", "")
                benefit_value = benefits.get("value", "")
                frequency = benefits.get("frequency", "")
                lines.append(f"  • Type: {benefit_type}")
                lines.append(f"  • Value: {benefit_value}")
                if frequency:
                    lines.append(f"  • Frequency: {frequency}")
            else:
                lines.append(f"  • {benefits}")
            lines.append("")
        
        # Required Documents
        documents = scheme.get("documents_required", [])
        if documents:
            lines.append("📄 DOCUMENTS REQUIRED:" if lang == "en" else "📄 தேவையான ஆவணங்கள்:")
            for doc in documents:
                lines.append(f"  • {doc}")
            lines.append("")
        
        # How to Apply
        lines.append("🔗 HOW TO APPLY:" if lang == "en" else "🔗 விண்ணப்பிக்கும் முறை:")
        apply_url = scheme.get("apply_url", "")
        official_source = scheme.get("official_source", "")
        
        if apply_url:
            lines.append(f"  • Application Link: {apply_url}")
        if official_source and official_source != apply_url:
            lines.append(f"  • Official Info: {official_source}")
        
        last_updated = scheme.get("last_updated", "")
        if last_updated:
            lines.append(f"  • Last Updated: {last_updated}")
        
        lines.append("")
        lines.append(f"{'='*50}")
        
        # Add YouTube suggestion
        lines.append("")
        lines.append("💡 Tip: Type 'youtube {name}' for video guides!" if lang == "en" else f"💡 குறிப்பு: வீடியோ வழிகாட்டிகளுக்கு 'youtube {name}' என தட்டச்சு செய்யவும்!")
        
        return "\n".join(lines)
        
    except Exception as e:
        from loguru import logger
        logger.exception(f"Error formatting detailed scheme: {e}")
        return format_scheme(scheme, lang)  # Fallback to simple format


def format_eligible_schemes(schemes: list, lang: str = "en", detailed: bool = False) -> str:
    if not schemes:
        msg = "No matching schemes found for your profile." if lang == "en" else "உங்கள் சுயவிவரத்திற்கு திட்டங்கள் கிடைக்கவில்லை."
        return msg

    if detailed and len(schemes) == 1:
        # If only one scheme and detailed view requested, show full details
        return format_scheme_detailed(schemes[0], lang)
    
    header = "Here are the schemes you may be eligible for:" if lang == "en" else "நீங்கள் தகுதியான திட்டங்கள்:"
    lines = [header, ""]
    for i, s in enumerate(schemes[:5], 1):  # Limit to first 5 schemes
        lines.append(f"{i}. {format_scheme(s, lang)}")
        lines.append("")  # Empty line between schemes

    if len(schemes) > 5:
        more_msg = f"\n...and {len(schemes) - 5} more schemes." if lang == "en" else f"\n...மற்றும் {len(schemes) - 5} திட்டங்கள்."
        lines.append(more_msg)
    
    # Add instructions
    lines.append("")
    lines.append("💡 To see detailed info for a scheme, type: 'details [scheme name]'" if lang == "en" else "💡 திட்டத்தின் முழு விவரங்களுக்கு: 'details [திட்டம் பெயர்]'")

    disclaimer = DISCLAIMER_EN if lang == "en" else DISCLAIMER_TA
    return "\n".join(lines) + disclaimer
