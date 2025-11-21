import json

class BaselineTransform:
    def __init__(self, layout):
        self.layout = layout or {}
        self.warnings = []

    def transform(self):
        # Minimal validation, no reordering
        out = {"layout": self.layout}
        # Add metrics
        out["metrics"] = {"hero_size": (self.layout.get("hero") or {}).get("size","default"),"sections_count": len(self.layout.get("sections",[]))}
        # No collapsible or protection
        return out

    def render_html(self, output_path):
        # Very simple prototype
        hero = self.layout.get('hero',{}) or {}
        title = hero.get('title','Untitled')
        size = hero.get('size','medium')
        sections = self.layout.get('sections',[])
        html = f"<html><head><meta charset='utf-8'><title>{title} - Baseline</title></head><body>"
        html += f"<div class='hero' style='height:{'400px' if size in ['large','xlarge'] else '200px'}; background:#eee;padding:20px;'><h1>{title}</h1><p>Size:{size}</p>" \
                f"<div>Price: {hero.get('price','Free')}</div><button>{hero.get('cta','') or 'Enroll'}</button></div>"
        for sec in sections:
            stype = sec.get('type','unknown')
            html += f"<section class='sec'><h2>{stype}</h2><div>{sec.get('content','')}</div>"
            if sec.get('attachments'):
                html += "<div class='attachments'>"
                for a in sec.get('attachments',[]):
                    html += f"<a href='#' onclick=\"window.open('{a.get('name')}','_blank')\">{a.get('name')}</a>"
                html += "</div>"
            html += "</section>"
        html += "</body></html>"
        with open(output_path,'w',encoding='utf-8') as f:
            f.write(html)
        return output_path
