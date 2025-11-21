from typing import Any, Dict, List
try:
    from .utils import normalize_node, flatten_layout
except ImportError:
    from utils import normalize_node, flatten_layout  # type: ignore


def transform_layout(layout_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enhanced transformation:
    - Normalizes and sanitizes nodes
    - Pinned info card (sidebar, sticky)
    - Collapsible sections and reviews
    - Anchored navigation
    - Non-blocking attachment previews (side panel)
    - Public vs internal notes separation
    - Confirmation prompts for actions/CTAs
    - Safe fallback for malformed layouts
    """
    warnings: List[str] = []
    edge_flags: List[str] = []
    normalized = normalize_node(layout_data, warnings, edge_flags)
    if normalized is None:
        fallback_layout = {
            "id": "fallback_page",
            "type": "page",
            "title": "Course",
            "anchors": [],
            "main": [],
            "sidebar": [],
            "internal_notes": [],
        }
        edge_flags.append("safe_fallback")
        return {
            "layout": fallback_layout,
            "warnings": warnings,
            "edge_case_flags": edge_flags,
            "metadata": {
                "blocking_preview": False,
                "collapsibles": True,
                "requires_confirmation": False,
                "pinned_info_card": True,
                "safe_fallback": True,
            },
        }

    main_children = []
    sidebar_children = []
    anchors = []
    internal_notes = []

    for child in normalized.get("children", []) or []:
        if not isinstance(child, dict):
            continue
        ntype = child.get("type")
        if ntype == "info_card":
            meta = child.setdefault("meta", {}) if isinstance(child.get("meta"), dict) else {}
            meta["position"] = "sidebar_sticky"
            sidebar_children.append(child)
            continue
        if ntype == "notes" and not (child.get("meta", {}) or {}).get("public", True):
            internal_notes.append(child)
            continue
        if ntype == "attachment":
            content = child.get("content", {}) if isinstance(child.get("content"), dict) else {}
            content["preview_type"] = "side_panel"
            child["content"] = content
        # enforce collapsible defaults
        if ntype in ("section", "syllabus", "reviews", "related_courses"):
            meta = child.setdefault("meta", {}) if isinstance(child.get("meta"), dict) else {}
            meta["collapsible"] = True
            meta["default_expanded"] = False
        # anchors for scannability
        if ntype in ("section", "reviews", "related_courses"):
            anchors.append({
                "id": child.get("id"),
                "label": child.get("title") or ntype.replace("_", " ").title(),
            })
        main_children.append(child)

    transformed_layout = {
        "id": normalized.get("id", "course_page"),
        "type": "page",
        "title": normalized.get("title"),
        "anchors": anchors,
        "main": main_children,
        "sidebar": sidebar_children,
        "internal_notes": internal_notes,
    }

    # Determine confirmations
    flat = flatten_layout(normalized)
    actions = [n for n in flat if isinstance(n, dict) and n.get("type") in ("action", "info_card")]
    requires_confirmation = bool(actions)

    metadata = {
        "blocking_preview": False,
        "collapsibles": True,
        "requires_confirmation": requires_confirmation,
        "pinned_info_card": True,
        "safe_fallback": True,
    }

    return {
        "layout": transformed_layout,
        "warnings": warnings,
        "edge_case_flags": edge_flags,
        "metadata": metadata,
    }
