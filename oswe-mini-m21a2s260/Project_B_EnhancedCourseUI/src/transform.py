import html

class EnhancedTransform:
    def __init__(self, layout):
        self.layout = layout or {}
        self.warnings = []

    def sanitize(self, text):
        if not isinstance(text,str):
            return ''
        return html.escape(text)

    def extract_info_card(self):
        hero = (self.layout.get('hero') or {})
        return {"title": self.sanitize(hero.get('title','Untitled')),
                "price": self.sanitize(hero.get('price','Free')),
                "tags": [self.sanitize(t) for t in hero.get('tags',[])],
                "cta": self.sanitize(hero.get('cta','Enroll'))}

    def collapse_sections(self, sections):
        out = []
        for s in sections:
            stype = s.get('type','unknown')
            safe_content = self.sanitize(s.get('content',''))
            if stype in ['syllabus','reviews','related_courses']:
                out.append({"type":stype,"content":safe_content,"collapsible":True,"collapsed":True,"attachments":s.get('attachments',[])})
            elif stype=='internal_note':
                out.append({"type":stype,"content":self.sanitize('[Internal note hidden]') ,"internal":True})
            else:
                out.append({"type":stype,"content":safe_content})
        return out

    def transform(self):
        # Re-structure and add pinned info card
        info = self.extract_info_card()
        sections = self.layout.get('sections',[])
        new_sections = self.collapse_sections(sections)
        # Handle malformed layout
        if not self.layout.get('hero'):
            self.warnings.append('Missing hero; added defaults')
        return {"info_card":info,"sections":new_sections,"warnings":self.warnings}

    def render_html(self, output_path):
        data = self.transform()
        info = data['info_card']
        sections = data['sections']
        # Build HTML prototype with pinned sidebar
        style = "body{font-family:Arial;} .container{display:flex;gap:20px;} .content{flex:1;} .card{background:#fff;padding:12px;border-radius:6px;box-shadow:0 1px 4px rgba(0,0,0,0.06)} .sidebar{width:300px;position:sticky;top:10px;height:fit-content;background:#f8f9fb;padding:10px;border-radius:8px} summary{cursor:pointer}"
        html_out = f"<html><head><meta charset='utf-8'><title>Enhanced - {info['title']}</title><style>{style}</style></head><body>"
        html_out += "<div class='container'><div class='content'>"
        html_out += f"<h1>{info['title']}</h1>"
        html_out += "<div style='display:flex;gap:10px;flex-wrap:wrap'>"
        for s in sections:
            if s.get('internal'):
                html_out += f"<div class='card' style='background:#fff3f3'><strong>Internal</strong><div>{s['content']}</div></div>"
            elif s.get('collapsible'):
                html_out += f"<details open={'false' if s.get('collapsed') else 'true'}><summary>{s['type'].title()}</summary><div>{s['content']}</div>"
                if s.get('attachments'):
                    html_out += "<div class='attachments' style='margin-top:8px;'>"
                    for a in s.get('attachments',[]):
                        html_out += f"<a href='#' onclick=\"document.getElementById('preview').innerText='Preview: {a.get('name')}';return false;\">{a.get('name')}</a> "
                    html_out += "</div>"
                html_out += "</details>"
            else:
                html_out += f"<div class='card'><h3>{s.get('type')}</h3><div>{s.get('content')}</div></div>"
        html_out += "</div></div>"
        # sidebar info card
        html_out += "<div class='sidebar card'><div><strong>Course Info</strong></div>"
        html_out += f"<div>Price: {info['price']}</div><div>Tags: {', '.join(info['tags'])}</div>"
        html_out += "<div style='margin-top:8px;'><button onclick=\"if(confirm('Confirm enroll?')){alert('Enrolled');}\">"+info['cta']+"</button></div>"
        html_out += "<div id='preview' style='margin-top:12px;background:#fff;padding:6px;border:1px dashed #ccc;'>Attachment preview area</div>"
        html_out += "</div></div></body></html>"
        with open(output_path,'w',encoding='utf-8') as f:
            f.write(html_out)
        return output_path
