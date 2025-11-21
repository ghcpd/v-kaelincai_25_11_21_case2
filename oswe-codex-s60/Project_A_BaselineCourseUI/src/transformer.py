from typing import Any, Dict, List
try:
    from .utils import normalize_node
except ImportError:
    from utils import normalize_node  # type: ignore


def transform_layout(layout_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Baseline transformation: minimal normalization, preserves original ordering,
    no hierarchy restructuring, no collapsibles.
    """
    warnings: List[str] = []
    edge_flags: List[str] = []
    normalized = normalize_node(layout_data, warnings, edge_flags)
    return {
        "layout": normalized,
        "warnings": warnings,
        "edge_case_flags": edge_flags,
        "metadata": {
            "blocking_preview": True,
            "collapsibles": False,
            "requires_confirmation": False,
            "pinned_info_card": False,
            "safe_fallback": False,
        },
    }
