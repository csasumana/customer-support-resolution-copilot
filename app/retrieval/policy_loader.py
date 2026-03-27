from pathlib import Path
from typing import List, Dict


BASE_DIR = Path(__file__).resolve().parents[2]
POLICY_DIR = BASE_DIR / "data" / "policies"


def load_policies() -> List[Dict[str, str]]:
    policies = []

    for file_path in POLICY_DIR.glob("*.txt"):
        text = file_path.read_text(encoding="utf-8")
        policies.append(
            {
                "name": file_path.name,
                "text": text,
            }
        )

    return policies