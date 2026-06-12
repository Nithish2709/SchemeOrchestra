import json
import sys
from pathlib import Path

REQUIRED_FIELDS = ["scheme_id", "name_en", "type", "category", "eligibility", "benefits", "apply_url", "active"]
SCHEMES_DIR = Path(__file__).parent.parent / "data" / "schemes"


def validate():
    errors = []
    for fp in SCHEMES_DIR.glob("*.json"):
        if "template" in fp.name:
            continue
        with open(fp, encoding="utf-8") as f:
            schemes = json.load(f)
        for s in schemes:
            for field in REQUIRED_FIELDS:
                if field not in s:
                    errors.append(f"{fp.name} | {s.get('scheme_id', '?')} missing field: {field}")

    if errors:
        print("[FAIL] Validation errors:")
        for e in errors:
            print(f"  {e}")
        sys.exit(1)
    else:
        print(f"[OK] All scheme data valid! ({sum(1 for _ in SCHEMES_DIR.glob('*.json'))} files checked)")


if __name__ == "__main__":
    validate()
