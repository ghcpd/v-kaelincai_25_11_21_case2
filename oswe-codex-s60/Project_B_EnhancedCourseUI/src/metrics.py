from typing import Any, Dict
try:
    from .utils import estimate_height
except ImportError:
    from utils import estimate_height  # type: ignore

EXPECTED_EDGE_FLAGS = {
    "auto_repaired",
    "unsafe_url_sanitized",
    "ambiguous_section_title",
}


def compute_metrics(result: Dict[str, Any]) -> Dict[str, Any]:
    layout = result.get("layout") or {}
    metadata = result.get("metadata", {})
    return {
        "hierarchy_clarity": compute_hierarchy_clarity(layout, metadata),
        "scroll_length": compute_scroll_length(layout),
        "misop_risk": compute_misop_risk(layout, metadata),
        "edge_coverage": compute_edge_coverage(result),
    }


def compute_hierarchy_clarity(layout: Dict[str, Any], metadata: Dict[str, Any]) -> float:
    base = 0.5
    anchors = layout.get("anchors", []) if isinstance(layout, dict) else []
    anchor_bonus = 0.1 if anchors else 0
    pinned_bonus = 0.15 if metadata.get("pinned_info_card") else 0
    collapsible_bonus = 0.15 if metadata.get("collapsibles") else 0
    # hero height penalty (if present in main children)
    hero = None
    for child in layout.get("main", []) or []:
        if isinstance(child, dict) and child.get("type") == "hero":
            hero = child
            break
    hero_height = 480
    if hero:
        meta = hero.get("meta", {}) if isinstance(hero.get("meta"), dict) else {}
        hero_height = meta.get("height", hero_height)
    hero_penalty = max(0, (hero_height - 480) / 1200) if isinstance(hero_height, (int, float)) else 0.1
    clarity = base + anchor_bonus + pinned_bonus + collapsible_bonus - hero_penalty
    return max(0.0, min(1.0, clarity))


def compute_scroll_length(layout: Dict[str, Any]) -> int:
    total = 0

    def visible_height(node):
        if not isinstance(node, dict):
            return 0
        meta = node.get("meta", {}) if isinstance(node.get("meta"), dict) else {}
        collapsed = bool(meta.get("collapsible") and not meta.get("default_expanded", False))
        h = estimate_height(node, collapsed=collapsed)
        if collapsed:
            return h
        for ch in node.get("children", []) or []:
            h += visible_height(ch)
        return h

    for child in layout.get("main", []) or []:
        total += visible_height(child)
    return total


def compute_misop_risk(layout: Dict[str, Any], metadata: Dict[str, Any]) -> float:
    requires_conf = metadata.get("requires_confirmation", False)
    if requires_conf:
        return 0.25
    # Fallback conservative risk
    return 0.5


def compute_edge_coverage(result: Dict[str, Any]) -> float:
    edge_flags = set(result.get("edge_case_flags", []) or [])
    if not edge_flags:
        return 0.0
    coverage = len(edge_flags & EXPECTED_EDGE_FLAGS) / len(EXPECTED_EDGE_FLAGS)
    return round(min(1.0, coverage), 3)
