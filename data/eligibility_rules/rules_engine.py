import json
from pathlib import Path

RULES_PATH = Path(__file__).parent / "rules.json"
SCHEMES_DIR = Path(__file__).parent.parent / "schemes"


def load_rules() -> dict:
    with open(RULES_PATH, encoding="utf-8") as f:
        return json.load(f)


def load_all_schemes() -> list:
    schemes = []
    try:
        for fp in SCHEMES_DIR.glob("*.json"):
            if "template" in fp.name:
                continue
            with open(fp, encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    schemes.extend(data)
                else:
                    schemes.append(data)
    except Exception as e:
        from loguru import logger
        logger.exception(f"Error loading schemes: {e}")
        raise
    return schemes


def check_eligibility(user_profile: dict) -> list[dict]:
    rules = load_rules()
    all_schemes = load_all_schemes()
    scheme_map = {s["scheme_id"]: s for s in all_schemes}
    eligible = []

    for scheme_id, rule in rules.items():
        if not _matches(user_profile, rule):
            continue
        if scheme_id in scheme_map:
            eligible.append(scheme_map[scheme_id])

    return eligible


def _matches(profile: dict, rule: dict) -> bool:
    age = profile.get("age", 0)
    income = profile.get("income_annual", 0)
    caste = profile.get("caste", "").upper()
    gender = profile.get("gender", "").lower()
    education = profile.get("education_level", "")
    state_resident = profile.get("state_resident", True)
    first_graduate = profile.get("first_graduate", False)
    parent_ex_serviceman = profile.get("parent_ex_serviceman", False)
    current_class = profile.get("class_number", 0)

    if rule.get("state_resident") and not state_resident:
        return False
    if "age_min" in rule and age < rule["age_min"]:
        return False
    if "age_max" in rule and age > rule["age_max"]:
        return False
    if "income_limit_annual" in rule and rule["income_limit_annual"] is not None:
        if income > rule["income_limit_annual"]:
            return False
    if "gender" in rule and rule["gender"] != "all":
        if gender != rule["gender"]:
            return False
    if "caste" in rule and rule["caste"] != "all":
        allowed = [c.upper() for c in rule["caste"]]
        if caste not in allowed and "MINORITY" not in allowed:
            if not (caste in ["MINORITY", "MUSLIM", "CHRISTIAN", "SIKH", "BUDDHIST", "JAIN", "PARSI"]
                    and "MINORITY" in allowed):
                return False
    if "education_level" in rule:
        if education not in rule["education_level"]:
            return False
    if "first_graduate" in rule and rule["first_graduate"]:
        if not first_graduate:
            return False
    if "parent_ex_serviceman" in rule and rule["parent_ex_serviceman"]:
        if not parent_ex_serviceman:
            return False
    if "class_range" in rule and current_class:
        low, high = rule["class_range"]
        if not (low <= current_class <= high):
            return False

    return True
