"""
Baseline Course UI Implementation
Simplistic transformation without optimization
- No hierarchy restructuring
- No collapsible sections
- Blocking attachment previews
- No mis-operation protection
- No public/internal content separation
"""

import json
import html
from typing import Dict, List, Any, Optional


class BaselineCourseUI:
    """Baseline implementation with minimal UI/UX considerations"""
    
    def __init__(self):
        self.warnings = []
        self.errors = []
        
    def transform(self, course_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform course data to UI layout (baseline version)
        No optimizations applied
        """
        try:
            layout = {
                "course_id": course_data.get("course_id", "UNKNOWN"),
                "sections": [],
                "metadata": {
                    "hero_height_px": 500,
                    "info_card_pinned": False,
                    "sections_collapsible": False,
                    "attachment_preview_mode": "blocking",
                    "public_internal_separated": False,
                    "enrollment_confirmation": False,
                    "mobile_optimized": False
                }
            }
            
            # Hero section (full size, no optimization)
            if "hero" in course_data:
                layout["sections"].append(self._build_hero(course_data["hero"]))
            
            # Title and basic info (not pinned)
            layout["sections"].append(self._build_title_section(course_data))
            
            # Description (includes author notes without separation)
            layout["sections"].append(self._build_description(course_data))
            
            # Instructor (full width)
            if "instructor" in course_data:
                layout["sections"].append(self._build_instructor(course_data["instructor"]))
            
            # Syllabus (always expanded, full width)
            if "syllabus" in course_data:
                layout["sections"].append(self._build_syllabus(course_data["syllabus"]))
            
            # Reviews (always expanded, full width)
            if "reviews" in course_data:
                layout["sections"].append(self._build_reviews(course_data["reviews"]))
            
            # Related courses (always expanded)
            if "related_courses" in course_data:
                layout["sections"].append(self._build_related(course_data["related_courses"]))
            
            # Attachments (blocking preview)
            if "attachments" in course_data:
                layout["sections"].append(self._build_attachments(course_data["attachments"]))
            
            # CTA at bottom only
            layout["sections"].append(self._build_cta(course_data))
            
            return {
                "status": "success",
                "layout": layout,
                "warnings": self.warnings,
                "errors": self.errors,
                "metrics": self._calculate_metrics(layout)
            }
            
        except Exception as e:
            self.errors.append(f"Transform failed: {str(e)}")
            return {
                "status": "error",
                "layout": None,
                "warnings": self.warnings,
                "errors": self.errors,
                "metrics": {}
            }
    
    def _build_hero(self, hero_data: Any) -> Dict[str, Any]:
        """Build hero section - oversized, not optimized"""
        if not isinstance(hero_data, dict):
            height = 500
        else:
            height = hero_data.get("height_px", 500)
            if not isinstance(height, int):
                height = 500
                
        return {
            "type": "hero",
            "height_px": height,
            "optimization": None,
            "above_fold": False
        }
    
    def _build_title_section(self, course_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build title section - not pinned"""
        return {
            "type": "title",
            "content": course_data.get("title", "Untitled Course"),
            "price": course_data.get("price"),
            "tags": course_data.get("tags", []),
            "pinned": False,
            "layout": "full_width"
        }
    
    def _build_description(self, course_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build description - no separation of public/internal content"""
        description = course_data.get("description", "")
        author_notes = course_data.get("author_notes", "")
        
        # Mix public and internal content (security issue)
        combined_content = description
        if author_notes:
            combined_content += "\n\n" + author_notes
            self.warnings.append("Author notes exposed publicly")
        
        return {
            "type": "description",
            "content": combined_content,
            "public_internal_separated": False,
            "sanitized": False,
            "layout": "full_width"
        }
    
    def _build_instructor(self, instructor_data: Any) -> Dict[str, Any]:
        """Build instructor section - full width, not card-based"""
        if instructor_data is None:
            return {"type": "instructor", "content": None, "layout": "full_width"}
            
        return {
            "type": "instructor",
            "content": instructor_data if isinstance(instructor_data, dict) else {},
            "layout": "full_width",
            "card_based": False
        }
    
    def _build_syllabus(self, syllabus_data: Any) -> Dict[str, Any]:
        """Build syllabus - always expanded, linear"""
        if not isinstance(syllabus_data, list):
            syllabus_data = []
            
        return {
            "type": "syllabus",
            "modules": syllabus_data,
            "collapsible": False,
            "default_state": "expanded",
            "layout": "full_width",
            "nested_depth": self._calculate_nesting_depth(syllabus_data)
        }
    
    def _build_reviews(self, reviews_data: Any) -> Dict[str, Any]:
        """Build reviews - always expanded"""
        if not isinstance(reviews_data, list):
            reviews_data = []
            
        return {
            "type": "reviews",
            "items": reviews_data,
            "collapsible": False,
            "default_state": "expanded",
            "layout": "full_width"
        }
    
    def _build_related(self, related_data: Any) -> Dict[str, Any]:
        """Build related courses - always expanded"""
        if not isinstance(related_data, list):
            related_data = []
            
        return {
            "type": "related_courses",
            "courses": related_data,
            "collapsible": False,
            "default_state": "expanded"
        }
    
    def _build_attachments(self, attachments_data: Any) -> Dict[str, Any]:
        """Build attachments - blocking fullscreen preview"""
        if not isinstance(attachments_data, list):
            attachments_data = []
            
        return {
            "type": "attachments",
            "items": attachments_data,
            "preview_mode": "blocking_fullscreen",
            "context_preserved": False
        }
    
    def _build_cta(self, course_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build CTA - only at bottom, no confirmation"""
        return {
            "type": "cta",
            "action": "enroll",
            "position": "bottom_only",
            "pinned": False,
            "confirmation_required": False,
            "mobile_optimized": False
        }
    
    def _calculate_nesting_depth(self, data: Any, current_depth: int = 0) -> int:
        """Calculate maximum nesting depth"""
        if not isinstance(data, (dict, list)):
            return current_depth
            
        max_depth = current_depth
        
        if isinstance(data, dict):
            for value in data.values():
                depth = self._calculate_nesting_depth(value, current_depth + 1)
                max_depth = max(max_depth, depth)
        elif isinstance(data, list):
            for item in data:
                depth = self._calculate_nesting_depth(item, current_depth + 1)
                max_depth = max(max_depth, depth)
                
        return max_depth
    
    def _calculate_metrics(self, layout: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate basic metrics"""
        sections = layout.get("sections", [])
        
        return {
            "total_sections": len(sections),
            "expanded_sections": len(sections),
            "collapsible_sections": 0,
            "pinned_elements": 0,
            "hero_height_px": layout.get("metadata", {}).get("hero_height_px", 500),
            "scroll_optimization_score": 0.0,
            "hierarchy_clarity_score": 0.3,
            "mis_operation_risk": 1.0,
            "edge_case_handling_score": 0.2
        }
    
    def generate_html(self, transform_result: Dict[str, Any], output_path: str):
        """Generate HTML prototype for baseline UI"""
        if transform_result["status"] != "success":
            html_content = self._generate_error_html(transform_result)
        else:
            html_content = self._generate_layout_html(transform_result["layout"])
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def _generate_error_html(self, result: Dict[str, Any]) -> str:
        """Generate error page HTML"""
        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Error - Baseline Course UI</title>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; background: #f5f5f5; }}
        .error {{ background: #ffebee; border: 1px solid #f44336; padding: 20px; border-radius: 4px; }}
    </style>
</head>
<body>
    <div class="error">
        <h1>Error Loading Course</h1>
        <p>Errors: {', '.join(result.get('errors', []))}</p>
    </div>
</body>
</html>"""
    
    def _generate_layout_html(self, layout: Dict[str, Any]) -> str:
        """Generate full layout HTML"""
        sections_html = ""
        
        for section in layout.get("sections", []):
            sections_html += self._render_section(section)
        
        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Baseline Course UI - {layout.get('course_id', 'Unknown')}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; }}
        .hero {{ width: 100%; height: {layout.get('metadata', {}).get('hero_height_px', 500)}px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); display: flex; align-items: center; justify-content: center; color: white; }}
        .section {{ padding: 40px 20px; max-width: 100%; margin: 0 auto; }}
        .section-title {{ font-size: 24px; margin-bottom: 20px; color: #333; }}
        .section-content {{ background: white; padding: 20px; border: 1px solid #ddd; }}
        .full-width {{ width: 100%; }}
        .module {{ margin-bottom: 20px; padding: 15px; background: #f9f9f9; border-left: 3px solid #667eea; }}
        .lesson {{ margin-left: 20px; padding: 10px; background: white; margin-top: 10px; }}
        .review {{ padding: 15px; background: #f5f5f5; margin-bottom: 10px; border-radius: 4px; }}
        .attachment {{ display: block; padding: 10px; background: #e3f2fd; margin-bottom: 10px; text-decoration: none; color: #1976d2; }}
        .cta {{ position: static; background: #4CAF50; color: white; padding: 20px; text-align: center; font-size: 18px; cursor: pointer; }}
        .warning-banner {{ background: #fff3cd; border: 1px solid #ffc107; padding: 10px; margin: 10px 0; }}
        .instructor-info {{ padding: 20px; background: #f5f5f5; }}
        .tags {{ display: flex; gap: 10px; flex-wrap: wrap; margin-top: 10px; }}
        .tag {{ background: #e0e0e0; padding: 5px 10px; border-radius: 3px; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="warning-banner">
        ⚠️ BASELINE UI - No optimizations applied. Large hero, no pinned CTA, all sections expanded, blocking previews.
    </div>
    {sections_html}
</body>
</html>"""
    
    def _render_section(self, section: Dict[str, Any]) -> str:
        """Render individual section"""
        section_type = section.get("type", "unknown")
        
        if section_type == "hero":
            return f'<div class="hero"><h1>Course Hero Image</h1></div>'
        
        elif section_type == "title":
            tags_html = "".join([f'<span class="tag">{html.escape(str(tag))}</span>' for tag in section.get("tags", [])])
            return f"""
            <div class="section full-width">
                <h1>{html.escape(str(section.get('content', 'Untitled')))}</h1>
                <p style="font-size: 24px; color: #4CAF50; margin-top: 10px;">Price: ${section.get('price', 'N/A')}</p>
                <div class="tags">{tags_html}</div>
            </div>"""
        
        elif section_type == "description":
            return f"""
            <div class="section full-width">
                <h2 class="section-title">Description</h2>
                <div class="section-content">
                    <p>{html.escape(str(section.get('content', '')))}</p>
                    <p style="color: #d32f2f; margin-top: 10px;"><strong>⚠️ Warning: Public and internal content mixed</strong></p>
                </div>
            </div>"""
        
        elif section_type == "instructor":
            content = section.get('content', {})
            if content:
                return f"""
                <div class="section full-width">
                    <h2 class="section-title">Instructor</h2>
                    <div class="instructor-info">
                        <h3>{html.escape(str(content.get('name', 'Unknown')))}</h3>
                        <p>{html.escape(str(content.get('bio', '')))}</p>
                    </div>
                </div>"""
        
        elif section_type == "syllabus":
            modules_html = ""
            for module in section.get("modules", []):
                if isinstance(module, dict):
                    lessons_html = ""
                    for lesson in module.get("lessons", []):
                        if isinstance(lesson, dict):
                            lessons_html += f'<div class="lesson">📄 {html.escape(str(lesson.get("title", "Lesson")))}</div>'
                    modules_html += f"""
                    <div class="module">
                        <h4>Module {module.get('module', '?')}: {html.escape(str(module.get('title', 'Untitled')))}</h4>
                        {lessons_html}
                    </div>"""
            
            return f"""
            <div class="section full-width">
                <h2 class="section-title">Syllabus (Always Expanded - No Collapse)</h2>
                <div class="section-content">
                    {modules_html if modules_html else '<p>No modules available</p>'}
                </div>
            </div>"""
        
        elif section_type == "reviews":
            reviews_html = ""
            for review in section.get("items", []):
                if isinstance(review, dict):
                    reviews_html += f"""
                    <div class="review">
                        <strong>{html.escape(str(review.get('user', 'Anonymous')))}</strong> - Rating: {review.get('rating', 'N/A')}
                        <p>{html.escape(str(review.get('comment', '')))}</p>
                    </div>"""
            
            return f"""
            <div class="section full-width">
                <h2 class="section-title">Reviews (Always Expanded)</h2>
                <div class="section-content">
                    {reviews_html if reviews_html else '<p>No reviews yet</p>'}
                </div>
            </div>"""
        
        elif section_type == "related_courses":
            courses = section.get("courses", [])
            courses_html = ", ".join([html.escape(str(c)) for c in courses])
            return f"""
            <div class="section full-width">
                <h2 class="section-title">Related Courses (Always Expanded)</h2>
                <div class="section-content">
                    <p>{courses_html if courses_html else 'None'}</p>
                </div>
            </div>"""
        
        elif section_type == "attachments":
            attachments_html = ""
            for attachment in section.get("items", []):
                if isinstance(attachment, dict):
                    attachments_html += f"""
                    <a href="#" class="attachment" onclick="alert('BLOCKING FULLSCREEN PREVIEW - Context lost!'); return false;">
                        📎 {html.escape(str(attachment.get('name', 'Unnamed')))} ({attachment.get('size_kb', '?')} KB)
                    </a>"""
            
            return f"""
            <div class="section full-width">
                <h2 class="section-title">Attachments (Blocking Preview)</h2>
                <div class="section-content">
                    {attachments_html if attachments_html else '<p>No attachments</p>'}
                </div>
            </div>"""
        
        elif section_type == "cta":
            return f"""
            <div class="cta" onclick="alert('IMMEDIATE ENROLLMENT - No confirmation!');">
                🛒 Enroll Now (Bottom Only - No Confirmation)
            </div>"""
        
        return ""
