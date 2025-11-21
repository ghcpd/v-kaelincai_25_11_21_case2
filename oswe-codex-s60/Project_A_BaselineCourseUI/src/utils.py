import copy

DEFAULT_HEIGHTS = {
    "hero": 600,
    "info_card": 300,
    "section": 400,
    "reviews": 500,
    "attachment": 120,
    "attachment_list": 200,
    "notes": 200,
    "action": 80,
}


def estimate_height(node: dict) -> int:
    meta = node.get("meta", {}) if isinstance(node, dict) else {}
    if isinstance(meta, dict) and isinstance(meta.get("height"), (int, float)):
        return int(meta["height"])
    return DEFAULT_HEIGHTS.get(node.get("type", "section"), 350)


def normalize_node(node, warnings, edge_flags, path="root"):
    """Minimal normalization for baseline to avoid crashes. Does not sanitize content deeply."""
    if not isinstance(node, dict):
        warnings.append(f"non_object_node@{path}")
        return None
    n = copy.deepcopy(node)
    if "id" not in n:
        warnings.append(f"missing_id@{path}")
        n["id"] = f"auto_{path.replace('/', '_')}"
        edge_flags.append("auto_repaired")
    if "type" not in n or not isinstance(n.get("type"), str):
        warnings.append(f"missing_type@{path}")
        n["type"] = "section"
        edge_flags.append("auto_repaired")
    children = n.get("children", []) if isinstance(n.get("children", []), list) else []
    norm_children = []
    for idx, ch in enumerate(children):
        norm = normalize_node(ch, warnings, edge_flags, path=f"{path}/{n['id']}[{idx}]")
        if norm is not None:
            norm_children.append(norm)
    n["children"] = norm_children
    if n.get("type") == "section" and not n.get("title"):
        warnings.append("ambiguous_section_title")
    return n


def flatten_layout(node):
    """Flatten layout into list of nodes for linear presentation."""
    flat = []
    if not node:
        return flat
    stack = [node]
    while stack:
        current = stack.pop(0)
        flat.append(current)
        if isinstance(current, dict) and current.get("children"):
            stack.extend(current["children"])
    return flat
