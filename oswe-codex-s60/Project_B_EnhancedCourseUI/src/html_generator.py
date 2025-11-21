from pathlib import Path
try:
  from jinja2 import Environment, select_autoescape
except ImportError:
  Environment = None
  select_autoescape = None

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"UTF-8\" />
  <title>{{ title }}</title>
  <style>
    body { font-family: 'Segoe UI', Arial, sans-serif; margin: 0; background: #f7f8fa; color: #222; }
    a { color: #1757b8; text-decoration: none; }
    .page { display: grid; grid-template-columns: 2fr 1fr; gap: 24px; padding: 24px; }
    .main { background: #fff; border-radius: 8px; padding: 16px 24px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); }
    .sidebar { position: sticky; top: 24px; align-self: start; }
    .info-card { background: #fff; border-radius: 8px; padding: 20px; box-shadow: 0 1px 4px rgba(0,0,0,0.1); }
    .info-card .price { font-size: 1.4rem; font-weight: bold; }
    .info-card .cta { margin-top: 16px; width: 100%; padding: 12px; background: #2563eb; color: #fff; border: none; border-radius: 6px; cursor: pointer; font-size: 1rem; }
    .info-card .tags { margin-top: 8px; font-size: 0.9rem; color: #555; }
    .hero { padding: 32px; border-radius: 8px; background: linear-gradient(135deg, #eef2ff, #e0f2fe); margin-bottom: 16px; }
    .hero h1 { margin: 0 0 8px; font-size: 1.8rem; }
    details.section { border-bottom: 1px solid #eee; padding: 12px 0; }
    details.section summary { cursor: pointer; font-weight: 600; list-style: none; }
    details.section[open] summary::after { content: '▲'; float: right; }
    details.section summary::after { content: '▼'; float: right; }
    .section-content { padding: 8px 16px 0; }
    .reviews, .related { border-bottom: 1px solid #eee; padding: 12px 0; }
    .attachment { margin: 6px 0; }
    .attachment a { cursor: pointer; }
    .anchors { position: sticky; top: 0; background: #f7f8fa; padding: 8px 24px; margin: -24px -24px 16px; border-bottom: 1px solid #e5e7eb; display: flex; gap: 16px; flex-wrap: wrap; }
    .anchors a { font-size: 0.95rem; padding: 4px 8px; border-radius: 4px; }
    .anchors a:hover { background: #e0e7ff; }
    /* Side preview panel */
    .preview-panel { position: fixed; top: 0; right: -40%; width: 40%; height: 100%; background: #fff; box-shadow: -2px 0 8px rgba(0,0,0,0.2); transition: right 0.3s ease; z-index: 9000; display: flex; flex-direction: column; }
    .preview-panel.open { right: 0; }
    .preview-header { padding: 12px 16px; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; align-items: center; }
    .preview-body { flex: 1; }
    .preview-body iframe { width: 100%; height: 100%; border: none; }
    .preview-close { cursor: pointer; font-size: 20px; }
    /* Bottom mobile CTA */
    .bottom-cta { display: none; position: fixed; bottom: 0; left: 0; right: 0; background: #2563eb; color: #fff; padding: 14px; text-align: center; font-size: 1rem; z-index: 8000; }
    .hidden { display: none; }
    @media (max-width: 960px) {
      .page { grid-template-columns: 1fr; }
      .sidebar { position: static; }
      .bottom-cta { display: block; }
    }
  </style>
</head>
<body>
  {% if layout.anchors %}
  <nav class="anchors">
    {% for anchor in layout.anchors %}
      <a href="#{{ anchor.id }}">{{ anchor.label }}</a>
    {% endfor %}
  </nav>
  {% endif %}

  <div class="page">
    <div class="main">
      {% macro render_node(node) %}
        {% set ntype = node.type %}
        {% if ntype == 'hero' %}
          <div class="hero" id="{{ node.id }}">
            <h1>{{ node.title or '' }}</h1>
            <p>{{ node.content or '' }}</p>
          </div>
        {% elif ntype == 'section' %}
          <details class="section" id="{{ node.id }}" {% if node.meta.default_expanded %}open{% endif %}>
            <summary>{{ node.title or 'Section' }}</summary>
            <div class="section-content">
              {% if node.content %}<p>{{ node.content|safe }}</p>{% endif %}
              {% if node.children %}
                {% for child in node.children %}
                  {{ render_node(child) }}
                {% endfor %}
              {% endif %}
            </div>
          </details>
        {% elif ntype == 'reviews' %}
          <details class="section" id="{{ node.id }}">
            <summary>Reviews</summary>
            <div class="section-content">
              <p>Rating: {{ node.meta.rating if node.meta and node.meta.rating is defined else 'N/A' }}</p>
            </div>
          </details>
        {% elif ntype == 'related_courses' %}
          <details class="section" id="{{ node.id }}">
            <summary>Related Courses</summary>
            <div class="section-content">
              <p>{{ node.content or '' }}</p>
            </div>
          </details>
        {% elif ntype == 'attachment' %}
          <div class="attachment" id="{{ node.id }}">
            <a href="#" class="attachment-link" data-url="{{ node.content.url if node.content and node.content.url is defined else '' }}" data-title="{{ node.title or 'Attachment' }}">{{ node.title or 'Attachment' }}</a>
          </div>
        {% elif ntype == 'action' %}
          <div class="section" id="{{ node.id }}">
            <button class="cta-confirm">{{ node.title or 'Action' }}</button>
          </div>
        {% else %}
          <div class="section" id="{{ node.id }}">
            {% if node.title %}<h3>{{ node.title }}</h3>{% endif %}
            <p>{{ node.content or '' }}</p>
          </div>
        {% endif %}
      {% endmacro %}

      {% for node in layout.main %}
        {{ render_node(node) }}
      {% endfor %}

      {% if layout.internal_notes %}
        <details class="section" id="internal_notes">
          <summary>Instructor Notes (Hidden)</summary>
          <div class="section-content">
            {% for note in layout.internal_notes %}
              <h4>{{ note.title or 'Note' }}</h4>
              <p>{{ note.content or '' }}</p>
            {% endfor %}
          </div>
        </details>
      {% endif %}
    </div>

    <div class="sidebar">
      {% for card in layout.sidebar %}
        {% if card.type == 'info_card' %}
          <div class="info-card" id="{{ card.id }}">
            <div class="price">{{ card.content.price if card.content and card.content.price is defined else '' }}</div>
            <div class="level">{{ card.content.level if card.content and card.content.level is defined else '' }}</div>
            <div class="tags">{{ ', '.join(card.content.tags) if card.content and card.content.tags is defined else '' }}</div>
            {% if card.content and card.content.cta is defined %}
              <button class="cta cta-confirm">{{ card.content.cta }}</button>
            {% endif %}
          </div>
        {% endif %}
      {% endfor %}
    </div>
  </div>

  <!-- Side preview panel -->
  <div class="preview-panel" id="previewPanel">
    <div class="preview-header">
      <span id="previewTitle"></span>
      <span class="preview-close" id="previewClose">&times;</span>
    </div>
    <div class="preview-body"><iframe id="previewFrame" src=""></iframe></div>
  </div>

  <div class="bottom-cta" id="bottomCta">Enroll Now</div>

  <script>
    document.addEventListener('DOMContentLoaded', function() {
      // Attachment previews (side panel)
      const panel = document.getElementById('previewPanel');
      const frame = document.getElementById('previewFrame');
      const titleEl = document.getElementById('previewTitle');
      const close = document.getElementById('previewClose');
      document.querySelectorAll('.attachment-link').forEach(link => {
        link.addEventListener('click', e => {
          e.preventDefault();
          const url = link.getAttribute('data-url');
          const title = link.getAttribute('data-title');
          frame.src = url || 'about:blank';
          titleEl.textContent = title;
          panel.classList.add('open');
        });
      });
      close.addEventListener('click', () => { panel.classList.remove('open'); frame.src = ''; });
      panel.addEventListener('click', e => { if (e.target === panel) { panel.classList.remove('open'); frame.src = ''; } });

      // Confirmation prompts for CTAs
      document.querySelectorAll('.cta-confirm').forEach(btn => {
        btn.addEventListener('click', e => {
          const label = btn.textContent.trim() || 'this action';
          if (!confirm(`Are you sure you want to proceed with ${label}?`)) {
            e.preventDefault();
          }
        });
      });

      // Bottom mobile CTA mirrors primary CTA
      const bottomCta = document.getElementById('bottomCta');
      const infoCta = document.querySelector('.info-card .cta-confirm');
      if (infoCta) {
        bottomCta.textContent = infoCta.textContent;
        bottomCta.addEventListener('click', () => infoCta.click());
      }
    });
  </script>
</body>
</html>
"""

def _render_plain(layout: dict, title: str):
  def render_node(n):
    if not isinstance(n, dict):
      return ""
    ntype = n.get("type")
    nid = n.get("id", "")
    title = n.get("title", "") or ""
    content = n.get("content", "") or ""
    children_html = "".join(render_node(ch) for ch in n.get("children", []) or [])
    if ntype == "hero":
      return f'<div class="hero" id="{nid}"><h1>{title}</h1><p>{content}</p></div>'
    if ntype == "section":
      return f'<details class="section" id="{nid}"><summary>{title or "Section"}</summary><div class="section-content">{content}{children_html}</div></details>'
    if ntype == "attachment":
      url = content.get("url", "") if isinstance(content, dict) else ""
      return f'<div class="attachment" id="{nid}"><a href="#" class="attachment-link" data-url="{url}">{title or "Attachment"}</a></div>'
    if ntype == "reviews":
      return f'<details class="section" id="{nid}"><summary>Reviews</summary><div class="section-content"></div></details>'
    if ntype == "action":
      return f'<div class="section" id="{nid}"><button class="cta-confirm">{title or "Action"}</button></div>'
    return f'<div class="section" id="{nid}">{title}{content}{children_html}</div>'

  anchors_html = "".join(f"<a href='#${a.get('id','')}'>{a.get('label','')}</a>" for a in layout.get("anchors", []) or []) if isinstance(layout, dict) else ""
  main_html = "".join(render_node(ch) for ch in layout.get("main", []) or []) if isinstance(layout, dict) else ""
  sidebar_html = "".join("<div class='info-card'></div>" for _ in layout.get("sidebar", []) or []) if isinstance(layout, dict) else ""
  return f"<!DOCTYPE html><html><head><meta charset='utf-8'><title>{title}</title></head><body><nav>{anchors_html}</nav><div class='page'><div class='main'>{main_html}</div><div class='sidebar'>{sidebar_html}</div></div></body></html>"


def generate_html(layout: dict, output_path: str, title: str = "Enhanced Course UI"):
  out_path = Path(output_path)
  if Environment is None:
    html = _render_plain(layout, title)
  else:
    env = Environment(autoescape=select_autoescape())
    template = env.from_string(HTML_TEMPLATE)
    html = template.render(layout=layout, title=title)
  out_path.write_text(html, encoding="utf-8")
  return str(out_path)
