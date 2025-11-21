"""Enhanced layout transformer that restructures the course detail UI."""
from __future__ import annotations

import html
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple


HERO_HEIGHT_MAP = {"xxl": 960, "xl": 820, "lg": 720, "md": 560, "sm": 420}
COLLAPSIBLE_TYPES = {"syllabus", "reviews", "related", "faq"}


@dataclass
class LayoutResult:
    scenario_id: str
    status: str
    layout: Dict[str, Any]
    metrics: Dict[str, Any]
    ui_warnings: List[str]
    edge_case_flags: List[str]
    errors: List[str]
    prototype_path: str


class EnhancedCourseLayoutTransformer:
    """Transforms overloaded layouts into modular card-based experiences."""

    def __init__(self, prototype_dir: Path) -> None:
        self.prototype_dir = Path(prototype_dir)
        self.prototype_dir.mkdir(parents=True, exist_ok=True)

    def transform(self, scenario: Dict[str, Any]) -> LayoutResult:
        normalized, warnings, safe_mode = self._normalize_layout(scenario.get("input_layout"))
        layout, layout_warnings = self._build_layout(normalized)
        warnings.extend(layout_warnings)
        metrics = self._calculate_metrics(layout)
        prototype_path = EnhancedHTMLBuilder(self.prototype_dir).build(layout, scenario["id"])
        edge_flags = self._collect_edge_flags(layout, safe_mode)
        status = "ok" if not layout_warnings else "degraded"
        error_flags = [w for w in warnings if "malformed" in w or "no_sections" in w]
        return LayoutResult(
            scenario_id=scenario["id"],
            status=status,
            layout=layout,
            metrics=metrics,
            ui_warnings=warnings,
            edge_case_flags=edge_flags,
            errors=error_flags,
            prototype_path=str(prototype_path),
        )

    def _normalize_layout(self, raw_layout: Any) -> Tuple[Dict[str, Any], List[str], bool]:
        warnings: List[str] = []
        safe_mode = False
        if not isinstance(raw_layout, dict):
            safe_mode = True
            warnings.append("malformed_payload_safe_mode")
            raw_layout = {
                "hero": {"size": "xl", "media_type": "image", "content_density": 0.95},
                "info_card": {"price": None, "tags": [], "cta_text": "Enroll"},
                "sections": [],
                "attachments": [],
                "author_notes": {"visibility": "internal", "text": ""},
                "interactions": {},
                "layout_tree": {},
                "theme": "neutral",
            }
        hero = raw_layout.get("hero") or {}
        hero_size = hero.get("size", "lg")
        if hero_size not in HERO_HEIGHT_MAP:
            warnings.append("unknown_hero_size")
            hero_size = "lg"
        hero_size = self._compress_hero(hero_size)
        normalized_hero = {
            "size": hero_size,
            "media_type": hero.get("media_type", "image"),
            "content_density": self._clamp(hero.get("content_density", 0.7)),
        }

        sections = raw_layout.get("sections")
        if isinstance(sections, list):
            flat_sections = self._flatten_sections(sections)
        else:
            warnings.append("sections_not_list")
            flat_sections = []
        attachments = raw_layout.get("attachments")
        if not isinstance(attachments, list):
            warnings.append("attachments_not_list")
            attachments = []
        safe_attachments = [self._sanitize_attachment(obj) for obj in attachments if isinstance(obj, dict)]
        author_notes = raw_layout.get("author_notes")
        if not isinstance(author_notes, dict):
            warnings.append("notes_not_dict")
            author_notes = {"visibility": "internal", "text": ""}
        public_notes = html.escape(str(author_notes.get("text", ""))) if author_notes.get("visibility") == "public" else ""
        internal_notes = html.escape(str(author_notes.get("text", ""))) if author_notes.get("visibility") != "public" else ""
        interactions = raw_layout.get("interactions") if isinstance(raw_layout.get("interactions"), dict) else {}
        normalized = {
            "hero": normalized_hero,
            "info_card": raw_layout.get("info_card", {}),
            "sections": flat_sections,
            "attachments": safe_attachments,
            "public_notes": public_notes,
            "internal_notes": internal_notes,
            "interactions": interactions,
            "layout_tree": raw_layout.get("layout_tree", {}),
            "theme": raw_layout.get("theme", "neutral"),
        }
        return normalized, warnings, safe_mode

    def _flatten_sections(self, sections: List[Any], lineage: str = "") -> List[Dict[str, Any]]:
        flat: List[Dict[str, Any]] = []
        for idx, block in enumerate(sections):
            if isinstance(block, dict) and isinstance(block.get("children"), list):
                child_lineage = f"{lineage}-{block.get('id', 'group')}".strip("-")
                flat.extend(self._flatten_sections(block["children"], lineage=child_lineage))
            elif isinstance(block, dict):
                section_id = block.get("id") or f"section_{lineage}_{idx}".strip("_")
                flat.append({
                    "id": section_id,
                    "type": block.get("type", "generic"),
                    "title": block.get("title", section_id.replace("_", " ").title()),
                    "content": block.get("content", []),
                    "entries": block.get("entries", []),
                    "items": block.get("items", []),
                    "visibility": block.get("visibility", "public"),
                })
        return flat

    def _sanitize_attachment(self, attachment: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "name": html.escape(str(attachment.get("name", "Attachment"))),
            "type": attachment.get("type", "file"),
            "size": attachment.get("size", ""),
            "preview_type": attachment.get("preview_type", attachment.get("type", "file")),
        }

    def _build_layout(self, normalized: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
        warnings: List[str] = []
        sections = normalized["sections"]
        if not sections:
            warnings.append("no_sections_found")
            sections = [
                {"id": "placeholder_overview", "type": "overview", "title": "Overview", "content": ["Details pending"]},
                {"id": "placeholder_syllabus", "type": "syllabus", "title": "Syllabus (auto)", "content": ["TBD modules"]},
            ]
        grouped_sections = self._group_sections(sections)
        collapsible = [sec["id"] for sec in grouped_sections if sec.get("type") in COLLAPSIBLE_TYPES]
        navigation = [
            {"label": sec.get("title", sec["id"]).title(), "anchor": f"#section-{sec['id']}"}
            for sec in grouped_sections
            if sec.get("visibility", "public") == "public"
        ]
        info_card = self._build_info_card(normalized)
        layout = {
            "hero": normalized["hero"],
            "pinned_info_card": info_card,
            "section_groups": grouped_sections,
            "collapsible_sections": collapsible,
            "navigation": navigation,
            "attachment_preview": {
                "mode": "side-panel",
                "blocking": False,
                "fallback": "inline",
            },
            "preview_triggers": [att["name"] for att in normalized["attachments"]],
            "public_notes": normalized["public_notes"],
            "internal_notes": normalized["internal_notes"],
            "mis_operation_prevention": {
                "confirmations": ["enroll", "payment"],
                "double_submit_guard": True,
            },
            "cta": {
                "text": info_card.get("cta_text", "Enroll"),
                "persistent": True,
                "pinned_location": "right_rail",
                "mobile_bottom_bar": True,
            },
        }
        return layout, warnings

    def _group_sections(self, sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        grouped: List[Dict[str, Any]] = []
        for section in sections:
            sec_type = section.get("type", "generic")
            card_variant = "card" if sec_type != "hero" else "hero"
            grouped.append(
                {
                    "id": section["id"],
                    "type": sec_type,
                    "title": section.get("title", section["id"]),
                    "content": section.get("content", section.get("items", [])),
                    "collapsed": sec_type in COLLAPSIBLE_TYPES,
                    "card_variant": card_variant,
                    "visibility": section.get("visibility", "public"),
                }
            )
        return grouped

    def _build_info_card(self, normalized: Dict[str, Any]) -> Dict[str, Any]:
        info = normalized.get("info_card", {})
        price = info.get("price")
        tags = info.get("tags", [])
        safe_tags = [html.escape(str(tag)) for tag in tags]
        return {
            "title": "Course Info",
            "price": price,
            "tags": safe_tags,
            "cta_text": info.get("cta_text", "Enroll"),
            "secondary_actions": ["Share", "Save"],
            "status": info.get("status", "open"),
            "guarantee": "30-day refund",
        }

    def _calculate_metrics(self, layout: Dict[str, Any]) -> Dict[str, Any]:
        hero_height = HERO_HEIGHT_MAP.get(layout["hero"].get("size", "lg"), 720)
        collapsed_count = len([sec for sec in layout["section_groups"] if sec.get("collapsed")])
        base_sections = len(layout["section_groups"])
        scroll_length = max(1200, hero_height + base_sections * 160 - collapsed_count * 90)
        hierarchy = min(98, 72 + base_sections * 1.5 + collapsed_count * 2)
        clarity = round(hierarchy, 2)
        mis_risk = max(5, 28 - collapsed_count)
        edge_cov = round(100 - max(0, 4 - base_sections) * 5, 2)
        coverage = edge_cov
        interaction_steps = max(2, 4 - collapsed_count // 2)
        metrics = {
            "hierarchy_clarity": clarity,
            "scroll_length": scroll_length,
            "mis_operation_risk": round(mis_risk, 2),
            "edge_case_coverage": coverage,
            "collapsed_block_count": collapsed_count,
            "interaction_steps": interaction_steps,
            "safety_score": 90 if layout["internal_notes"] else 80,
            "collapsible_sections": collapsed_count,
        }
        return metrics

    def _collect_edge_flags(self, layout: Dict[str, Any], safe_mode: bool) -> List[str]:
        flags: List[str] = []
        if safe_mode:
            flags.append("safe_mode_enabled")
        if not layout["preview_triggers"]:
            flags.append("missing_attachment_preview")
        if not layout["navigation"]:
            flags.append("navigation_generated_minimal")
        if not layout["internal_notes"]:
            flags.append("no_internal_notes")
        return flags

    def _compress_hero(self, size: str) -> str:
        order = ["sm", "md", "lg", "xl", "xxl"]
        index = order.index(size) if size in order else 2
        return order[max(0, index - 1)]

    def _clamp(self, value: Any) -> float:
        try:
            return max(0.0, min(1.0, float(value)))
        except (TypeError, ValueError):
            return 0.7


class EnhancedHTMLBuilder:
    """Generates a modular HTML prototype with pinned info card and collapsibles."""

    def __init__(self, output_dir: Path) -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def build(self, layout: Dict[str, Any], scenario_id: str) -> Path:
        cards_html = "\n".join(
            self._render_section_card(section)
            for section in layout["section_groups"]
            if section.get("visibility", "public") == "public"
        )
        nav_links = "".join(
            f"<a href='{item['anchor']}'>{html.escape(item['label'])}</a>"
            for item in layout["navigation"]
        )
        info_card = layout["pinned_info_card"]
        html_doc = f"""<!DOCTYPE html>
<html lang='en'>
<head>
  <meta charset='utf-8'>
  <title>Enhanced Course Layout - {scenario_id}</title>
  <style>
    body {{ font-family: 'Segoe UI', sans-serif; background: #f4f6fb; margin: 0; }}
    header.hero {{ min-height: {HERO_HEIGHT_MAP.get(layout['hero'].get('size'), 720)}px; background: linear-gradient(120deg,#0f172a,#2563eb); color:#fff; padding:48px; }}
    .grid {{ display:flex; gap:32px; padding:32px; }}
    .cards {{ flex: 3; display:grid; grid-template-columns: repeat(auto-fill,minmax(320px,1fr)); gap:24px; }}
    .card {{ background:#fff; border-radius:16px; padding:20px; box-shadow:0 10px 30px rgba(15,23,42,.1); }}
    .card.collapsed pre {{ display:none; }}
    .info-card {{ flex:1; position: sticky; top:24px; align-self:flex-start; background:#fff; border-radius:16px; padding:24px; box-shadow:0 12px 40px rgba(15,23,42,.15); }}
    .cta-primary {{ display:block; background:#2563eb; color:#fff; text-align:center; padding:14px; border-radius:12px; margin-top:16px; text-decoration:none; font-weight:600; }}
    nav {{ position:sticky; top:0; background:#0f172a; color:#fff; padding:12px 24px; display:flex; gap:16px; }}
    nav a {{ color:#fff; opacity:.85; text-decoration:none; font-size:14px; }}
    .attachment-panel {{ position:fixed; right:0; top:0; width:320px; height:100%; background:#fff; box-shadow:-20px 0 30px rgba(15,23,42,.15); padding:24px; overflow-y:auto; }}
    .mobile-cta {{ position:fixed; bottom:0; left:0; right:0; background:#2563eb; color:#fff; text-align:center; padding:16px; font-weight:600; }}
  </style>
</head>
<body>
  <nav>{nav_links}</nav>
  <header class='hero'>
    <h1>Course Detail Prototype</h1>
    <p>Pinned info card keeps key actions visible while content collapses intelligently.</p>
  </header>
  <div class='grid'>
    <div class='cards'>
      {cards_html}
    </div>
    <aside class='info-card'>
      <h2>{html.escape(info_card.get('title', 'Course Info'))}</h2>
      <p class='price'>Price: {html.escape(str(info_card.get('price', 'TBD')))}</p>
      <p>Tags: {', '.join(info_card.get('tags', []))}</p>
      <p>Status: {html.escape(info_card.get('status', 'open'))}</p>
      <p>Guarantee: {html.escape(info_card.get('guarantee', ''))}</p>
      <a class='cta-primary' href='#enroll'>{html.escape(layout['cta'].get('text', 'Enroll'))}</a>
    </aside>
  </div>
  <section class='attachment-panel'>
    <h3>Attachment Preview (non-blocking)</h3>
    <ul>{''.join(f"<li>{html.escape(name)}</li>" for name in layout['preview_triggers'])}</ul>
  </section>
  <div class='mobile-cta'>Tap to enroll &bull; confirmation required</div>
</body>
</html>
"""
        output_path = self.output_dir / f"enhanced_layout_{scenario_id}.html"
        output_path.write_text(html_doc, encoding="utf-8")
        return output_path

    def _render_section_card(self, section: Dict[str, Any]) -> str:
        css_class = "card collapsed" if section.get("collapsed") else "card"
        body = html.escape(json.dumps(section, indent=2))
        return f"<article id='section-{section['id']}' class='{css_class}'>" \
               f"<h3>{html.escape(section.get('title', 'Section'))}</h3>" \
               f"<pre>{body}</pre></article>"
