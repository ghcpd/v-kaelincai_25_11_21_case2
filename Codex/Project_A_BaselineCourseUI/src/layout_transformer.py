"""Baseline layout transformer for the overloaded course detail page.
The transformer keeps the legacy behaviors so tests can benchmark improvements.
"""
from __future__ import annotations

import html
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple


HERO_HEIGHT_MAP = {"xxl": 1200, "xl": 980, "lg": 860, "md": 640, "sm": 520}


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


class CourseLayoutTransformer:
    """Legacy transformer that intentionally keeps inefficient structure."""

    def __init__(self, prototype_dir: Path) -> None:
        self.prototype_dir = Path(prototype_dir)
        self.prototype_dir.mkdir(parents=True, exist_ok=True)

    def transform(self, scenario: Dict[str, Any]) -> LayoutResult:
        normalized, warnings = self._normalize_layout(scenario.get("input_layout"))
        layout = self._build_layout(normalized)
        metrics = self._calculate_metrics(layout, normalized)
        prototype_path = BaselineHTMLBuilder(self.prototype_dir).build(layout, scenario["id"])
        edge_flags = self._collect_edge_flags(normalized, layout)
        errors = [w for w in warnings if "malformed" in w or "not_" in w]
        return LayoutResult(
            scenario_id=scenario["id"],
            status="ok",
            layout=layout,
            metrics=metrics,
            ui_warnings=warnings,
            edge_case_flags=edge_flags,
            errors=errors,
            prototype_path=str(prototype_path),
        )

    def _normalize_layout(self, raw_layout: Any) -> Tuple[Dict[str, Any], List[str]]:
        warnings: List[str] = []
        sanitized: Dict[str, Any]
        if not isinstance(raw_layout, dict):
            warnings.append("malformed_payload")
            sanitized = {
                "hero": {"size": "xl", "media_type": "image", "content_density": 0.95},
                "info_card": {"price": None, "tags": [], "cta_text": "Enroll"},
                "sections": [],
                "attachments": [],
                "author_notes": {"visibility": "internal", "text": ""},
                "interactions": {"cta_locations": ["footer"], "enrollment_confirmation": False},
                "layout_tree": {},
                "theme": "light",
            }
        else:
            sanitized = raw_layout.copy()

        hero = sanitized.get("hero") or {}
        hero_size = hero.get("size") if isinstance(hero, dict) else "xl"
        if hero_size not in HERO_HEIGHT_MAP:
            warnings.append("unknown_hero_size")
            hero_size = "xl"
        sanitized_hero = {
            "size": hero_size,
            "media_type": hero.get("media_type", "image") if isinstance(hero, dict) else "image",
            "content_density": self._clamp(hero.get("content_density", 0.9) if isinstance(hero, dict) else 0.9),
        }

        sections = sanitized.get("sections")
        if not isinstance(sections, list):
            warnings.append("sections_not_list")
            sections = []
        flat_sections = self._flatten_sections(sections)

        attachments = sanitized.get("attachments")
        if not isinstance(attachments, list):
            warnings.append("attachments_not_list")
            attachments = []
        safe_attachments = [self._sanitize_attachment(obj) for obj in attachments if isinstance(obj, dict)]

        author_notes = sanitized.get("author_notes")
        if not isinstance(author_notes, dict):
            warnings.append("notes_not_dict")
            author_notes = {"visibility": "internal", "text": ""}
        else:
            author_notes = {
                "visibility": author_notes.get("visibility", "internal"),
                "text": html.escape(str(author_notes.get("text", ""))),
            }

        interactions = sanitized.get("interactions")
        if not isinstance(interactions, dict):
            warnings.append("interactions_not_dict")
            interactions = {"cta_locations": ["footer"], "enrollment_confirmation": False}

        normalized = {
            "hero": sanitized_hero,
            "info_card": sanitized.get("info_card", {}),
            "sections": flat_sections,
            "attachments": safe_attachments,
            "author_notes": author_notes,
            "interactions": interactions,
            "layout_tree": sanitized.get("layout_tree", {}),
            "theme": sanitized.get("theme", "light"),
        }
        return normalized, warnings

    def _flatten_sections(self, sections: List[Any]) -> List[Dict[str, Any]]:
        flat: List[Dict[str, Any]] = []
        for block in sections:
            if isinstance(block, dict) and block.get("children") and isinstance(block.get("children"), list):
                flat.extend(self._flatten_sections(block["children"]))
            elif isinstance(block, dict):
                safe_block = {k: v for k, v in block.items() if k in {"id", "type", "title", "content", "entries", "items", "full_width", "visibility"}}
                safe_block.setdefault("id", f"section_{len(flat)}")
                safe_block.setdefault("type", "unknown")
                flat.append(safe_block)
        return flat

    def _sanitize_attachment(self, attachment: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "name": html.escape(str(attachment.get("name", "attachment"))),
            "type": attachment.get("type", "file"),
            "size": attachment.get("size", ""),
        }

    def _build_layout(self, normalized: Dict[str, Any]) -> Dict[str, Any]:
        sections = normalized["sections"]
        layout = {
            "hero": normalized["hero"],
            "info_card": normalized.get("info_card", {}),
            "sections": sections,
            "cta": {
                "text": normalized.get("info_card", {}).get("cta_text", "Enroll"),
                "persistent": False,
                "locations": normalized.get("interactions", {}).get("cta_locations", ["footer"]),
            },
            "attachment_preview": {
                "mode": "overlay",
                "blocking": True,
            },
            "collapsible_sections": [],
            "public_notes": normalized.get("author_notes", {}).get("text", ""),
            "internal_notes": normalized.get("author_notes", {}).get("text", ""),
            "navigation": [],
        }
        return layout

    def _calculate_metrics(self, layout: Dict[str, Any], normalized: Dict[str, Any]) -> Dict[str, Any]:
        hero_penalty = HERO_HEIGHT_MAP.get(normalized["hero"]["size"], 1000)
        section_penalty = len(layout["sections"]) * 220
        scroll_length = hero_penalty + section_penalty
        hierarchy = max(25, 60 - len(layout["sections"]) * 3 - normalized["hero"]["content_density"] * 20)
        mis_operation = min(100, 65 + len(layout["sections"]))
        edge_coverage = self._edge_case_score(layout)
        interaction_steps = max(3, len(layout["sections"]) // 2 + 3)
        safety_score = 35 if normalized.get("interactions", {}).get("enrollment_confirmation") is not True else 55
        metrics = {
            "hierarchy_clarity": round(hierarchy, 2),
            "scroll_length": scroll_length,
            "mis_operation_risk": round(mis_operation, 2),
            "edge_case_coverage": edge_coverage,
            "collapsed_block_count": len(layout["collapsible_sections"]),
            "collapsible_sections": len(layout["collapsible_sections"]),
            "interaction_steps": interaction_steps,
            "safety_score": safety_score,
        }
        return metrics

    def _edge_case_score(self, layout: Dict[str, Any]) -> float:
        recognized = sum(1 for s in layout["sections"] if s.get("type") in {"overview", "syllabus", "reviews", "instructor", "attachments", "faq", "related"})
        total = max(1, len(layout["sections"]))
        return round((recognized / total) * 100, 2)

    def _collect_edge_flags(self, normalized: Dict[str, Any], layout: Dict[str, Any]) -> List[str]:
        flags: List[str] = []
        if not layout["sections"]:
            flags.append("no_sections")
        if normalized.get("author_notes", {}).get("visibility") != "public":
            flags.append("internal_notes_exposed")
        if normalized.get("interactions", {}).get("enrollment_confirmation") is not True:
            flags.append("missing_enrollment_confirmation")
        if layout["attachment_preview"]["blocking"]:
            flags.append("attachment_blocks_view")
        return flags

    def _clamp(self, value: Any) -> float:
        try:
            return max(0.0, min(1.0, float(value)))
        except (TypeError, ValueError):
            return 0.9


class BaselineHTMLBuilder:
    """Generates a long one-column HTML prototype to visualize baseline issues."""

    def __init__(self, output_dir: Path) -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def build(self, layout: Dict[str, Any], scenario_id: str) -> Path:
        sections_html = "\n".join(
            f"<section class='block block-{html.escape(section.get('type', 'unknown'))}'>"
            f"<h2>{html.escape(section.get('title', section.get('id', 'Section')))}</h2>"
            f"<pre>{html.escape(json.dumps(section, indent=2))}</pre>"
            "</section>"
            for section in layout["sections"]
        )
        hero_class = f"hero hero-{layout['hero'].get('size', 'xl')}"
        html_doc = f"""<!DOCTYPE html>
<html lang='en'>
<head>
  <meta charset='utf-8'>
  <title>Baseline Course Layout - {scenario_id}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }}
    .{hero_class} {{ height: {HERO_HEIGHT_MAP.get(layout['hero'].get('size'), 900)}px; background: #222; color: #fff; display: flex; align-items: center; justify-content: center; text-transform: uppercase; }}
    section.block {{ padding: 24px; border-bottom: 1px solid #ddd; background: #fff; }}
    .cta {{ position: relative; margin: 24px; padding: 16px; background: #ffdede; text-align: center; }}
    pre {{ white-space: pre-wrap; background: #f0f0f0; padding: 12px; overflow-x: auto; }}
  </style>
</head>
<body>
  <div class='{hero_class}'>Oversized Hero</div>
  <div class='cta'>CTA lives in footer only: {html.escape(layout['cta'].get('text', 'Enroll'))}</div>
  {sections_html}
  <div class='attachments'>Attachments open as overlay (blocking)</div>
</body>
</html>
"""
        output_path = self.output_dir / f"baseline_layout_{scenario_id}.html"
        output_path.write_text(html_doc, encoding="utf-8")
        return output_path
