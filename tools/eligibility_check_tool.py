"""Updated eligibility check tool using SQLite engine"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.unified_search import eligibility_check_tool as unified_check


def eligibility_check_tool(user_profile: dict) -> list[dict]:
    """Return list of schemes the user is eligible for using SQLite."""
    return unified_check(user_profile)
