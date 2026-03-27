from typing import List, Dict, Optional


def log_action(trace: List[Dict], step: str, decision: str, reason: Optional[str] = None) -> List[Dict]:
    trace.append(
        {
            "step": step,
            "decision": decision,
            "reason": reason,
        }
    )
    return trace