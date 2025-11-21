import copy
from urllib.parse import urlparse
try:
    import bleach  # type: ignore
except ImportError:  # minimal fallback
    import re

    class _FallbackBleach:
        @staticmethod
        def clean(text, tags=None, attributes=None, strip=True):
            if not isinstance(text, str):
                return text
            # Remove simple HTML tags
            return re.sub(r"<[^>]+>", "", text)

        class sanitizer:
            ALLOWED_TAGS = []

    bleach = _FallbackBleach()

DEFAULT_HEIGHTS = {
    "hero": 480,
    "info_card": 260,
    "section": 320,
    "reviews": 360,
    "attachment": 80,
    "attachment_list": 160,
    "notes": 200,
    "action": 70,
    "related_courses": 300,
}
COLLAPSED_HEADER_HEIGHT = 80
ALLOWED_TAGS = list(getattr(getattr(bleach, "sanitizer", bleach), "ALLOWED_TAGS", [])) + ["p", "br", "strong", "em", "ul", "ol", "li"]
ALLOWED_ATTRS = {"a": ["href", "title", "target"], "img": ["src", "alt"]}


def sanitize_content(value):
    if isinstance(value, str):
        return bleach.clean(value, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS, strip=True)
    return value


def sanitize_url(url: str):
    if not isinstance(url, str):
        return ""
    parsed = urlparse(url)
    if parsed.scheme == "https":
        return url
    # treat non-https as unsafe
    return ""


def estimate_height(node: dict, collapsed: bool = False) -> int:
    meta = node.get("meta", {}) if isinstance(node, dict) else {}
    if collapsed and meta.get("collapsible") and not meta.get("default_expanded", False):
        return COLLAPSED_HEADER_HEIGHT
    if isinstance(meta, dict) and isinstance(meta.get("height"), (int, float)):
        return int(meta["height"])
    return DEFAULT_HEIGHTS.get(node.get("type", "section"), 300)


def apply_collapsible_defaults(node: dict):
    ntype = node.get("type")
    meta = node.setdefault("meta", {}) if isinstance(node, dict) else {}
    if not isinstance(meta, dict):
        meta = {}
        node["meta"] = meta
    if ntype in ("syllabus", "section", "reviews", "related_courses", "attachment_list"):
        meta.setdefault("collapsible", True)
        meta.setdefault("default_expanded", False)
    return node


def normalize_node(node, warnings, edge_flags, path="root"):
    if not isinstance(node, dict):
        warnings.append(f"non_object_node@{path}")
        edge_flags.append("malformed_nodes_detected")
        return None
    n = copy.deepcopy(node)
    if "id" not in n or not n.get("id"):
        warnings.append(f"missing_id@{path}")
        n["id"] = f"auto_{path.replace('/', '_')}"
        edge_flags.append("auto_repaired")
    if "type" not in n or not isinstance(n.get("type"), str):
        warnings.append(f"missing_type@{path}")
        n["type"] = "section"
        edge_flags.append("auto_repaired")
    # sanitize content
    if "content" in n:
        if isinstance(n["content"], dict):
            n["content"] = {k: sanitize_url(v) if k == "url" else sanitize_content(v) for k, v in n["content"].items()}
        else:
            n["content"] = sanitize_content(n["content"])
    if n.get("type") == "attachment":
        content = n.get("content", {}) if isinstance(n.get("content"), dict) else {}
        if "url" in content:
            safe = sanitize_url(content.get("url", ""))
            if safe != content.get("url"):
                warnings.append("unsafe_url_sanitized")
                edge_flags.append("unsafe_url_sanitized")
            content["url"] = safe
            n["content"] = content
    if n.get("type") == "section" and not n.get("title"):
        warnings.append("ambiguous_section_title")
        edge_flags.append("ambiguous_section_title")
    # apply collapsible defaults
    n = apply_collapsible_defaults(n)
    # children
    children = n.get("children", []) if isinstance(n.get("children", []), list) else []
    norm_children = []
    for idx, ch in enumerate(children):
        norm = normalize_node(ch, warnings, edge_flags, path=f"{path}/{n['id']}[{idx}]")
        if norm is not None:
            norm_children.append(norm)
    n["children"] = norm_children
    return n


def flatten_layout(node):
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
