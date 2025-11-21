from typing import Any, Dict
try:
    from .utils import estimate_height, flatten_layout
except ImportError:
    from utils import estimate_height, flatten_layout  # type: ignore


def compute_metrics(result: Dict[str, Any]) -> Dict[str, Any]:
    layout = result.get("layout") or {}
    metrics = {
      "hierarchy_clarity": compute_hierarchy_clarity(layout, result.get("metadata", {})),
      "scroll_length": compute_scroll_length(layout),
      "misop_risk": compute_misop_risk(layout, result.get("metadata", {})),
      "edge_coverage": compute_edge_coverage(result),
    }
    return metrics


def compute_hierarchy_clarity(layout: Dict[str, Any], metadata: Dict[str, Any]) -> float:
    if not layout:
        return 0.2
    children = layout.get("children", []) if isinstance(layout, dict) else []
    hero = next((c for c in children if isinstance(c, dict) and c.get("type") == "hero"), None)
    info_card_idx = next((i for i, c in enumerate(children) if isinstance(c, dict) and c.get("type") == "info_card"), None)
    hero_height = 600
    if hero:
        hero_height_meta = hero.get("meta", {}) if isinstance(hero.get("meta"), dict) else {}
        hero_height = hero_height_meta.get("height", hero_height)
    base = 0.3
    hero_penalty = max(0, (hero_height - 500) / 1000) if isinstance(hero_height, (int, float)) else 0.2
    info_bonus = 0.05 if info_card_idx is not None and info_card_idx <= 2 else 0
    collapsible_bonus = 0.0  # baseline has none
    pinned_bonus = 0.0
    clarity = base + info_bonus + collapsible_bonus + pinned_bonus - hero_penalty
    return max(0.0, min(1.0, clarity))


def compute_scroll_length(layout: Dict[str, Any]) -> int:
    if not layout:
        return 0
    total = 0
    for child in layout.get("children", []) or []:
        if not isinstance(child, dict):
            continue
        total += estimate_height(child)
        # baseline shows all nested content expanded
        for sub in flatten_layout(child)[1:]:
            if isinstance(sub, dict):
                total += estimate_height(sub)
    return total


def compute_misop_risk(layout: Dict[str, Any], metadata: Dict[str, Any]) -> float:
    flat = flatten_layout(layout)
    actions = [n for n in flat if isinstance(n, dict) and n.get("type") in ("action", "info_card")]
    if not actions:
        return 0.2
    dangerous = [a for a in actions if isinstance(a.get("meta"), dict) and a.get("meta", {}).get("dangerous_action")]
    confirmations = metadata.get("requires_confirmation", False)
    if dangerous and not confirmations:
        return 0.8
    if actions and not confirmations:
        return 0.6
    return 0.3


def compute_edge_coverage(result: Dict[str, Any]) -> float:
    # Baseline does not actively handle edge cases beyond minimal normalization
    return 0.0
