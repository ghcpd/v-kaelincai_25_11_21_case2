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
    body { font-family: Arial, sans-serif; margin: 0; padding: 0; }
    .hero { background: #eef3ff; padding: 60px 40px; font-size: 1.4rem; }
    .info-card { padding: 20px; border-bottom: 1px solid #ddd; background: #fafafa; }
    .section { padding: 20px 40px; border-bottom: 1px solid #eee; }
    .reviews { padding: 20px 40px; background: #f5f5f5; }
    .attachment { margin: 10px 0; }
    .attachment a { color: #0645ad; cursor: pointer; }
    /* Blocking preview modal */
    .modal { display: none; position: fixed; top:0; left:0; width:100%; height:100%; background: rgba(0,0,0,0.75); z-index:9999; }
    .modal-content { position: relative; margin: 5% auto; padding: 20px; background: #fff; width: 80%; height: 80%; overflow: auto; }
    .modal-close { position: absolute; top: 10px; right: 20px; cursor: pointer; font-size: 20px; }
  </style>
</head>
<body>
  {% macro render_node(node) %}
    {% set ntype = node.type %}
    {% if ntype == 'hero' %}
      <div class="hero" id="{{ node.id }}">
        <h1>{{ node.title or '' }}</h1>
        <p>{{ node.content or '' }}</p>
      </div>
    {% elif ntype == 'info_card' %}
      <div class="info-card" id="{{ node.id }}">
        <div><strong>Price:</strong> {{ node.content.price if node.content and node.content.price is defined else '' }}</div>
        <div><strong>Level:</strong> {{ node.content.level if node.content and node.content.level is defined else '' }}</div>
        <div><strong>Tags:</strong> {{ ', '.join(node.content.tags) if node.content and node.content.tags is defined else '' }}</div>
        {% if node.content and node.content.cta is defined %}
          <button class="cta">{{ node.content.cta }}</button>
        {% endif %}
      </div>
    {% elif ntype == 'section' %}
      <div class="section" id="{{ node.id }}">
        {% if node.title %}<h2>{{ node.title }}</h2>{% endif %}
        {% if node.content %}<p>{{ node.content }}</p>{% endif %}
        {% if node.children %}
          {% for child in node.children %}
            {{ render_node(child) }}
          {% endfor %}
        {% endif %}
      </div>
    {% elif ntype == 'reviews' %}
      <div class="reviews" id="{{ node.id }}">
        <h2>Reviews</h2>
        <p>Rating: {{ node.meta.rating if node.meta and node.meta.rating is defined else 'N/A' }}</p>
      </div>
    {% elif ntype == 'attachment' %}
      <div class="attachment" id="{{ node.id }}">
        <a href="#" class="attachment-link" data-url="{{ node.content.url if node.content and node.content.url is defined else '' }}">{{ node.title or 'Attachment' }}</a>
      </div>
    {% elif ntype == 'notes' %}
      <div class="section" id="{{ node.id }}">
        <h2>{{ node.title or 'Notes' }}</h2>
        <p>{{ node.content or '' }}</p>
      </div>
    {% elif ntype == 'action' %}
      <div class="section" id="{{ node.id }}">
        <button class="cta">{{ node.title or 'Action' }}</button>
      </div>
    {% else %}
      <div class="section" id="{{ node.id }}">
        <p>{{ node.content or '' }}</p>
      </div>
    {% endif %}
  {% endmacro %}

  {% if layout and layout.children %}
    {% for node in layout.children %}
      {{ render_node(node) }}
    {% endfor %}
  {% endif %}

  <div class="modal" id="attachmentModal">
    <div class="modal-content">
      <span class="modal-close" id="modalClose">&times;</span>
      <iframe id="modalFrame" src="" style="width:100%; height:100%; border:none;"></iframe>
    </div>
  </div>

  <script>
    document.addEventListener('DOMContentLoaded', function() {
      const modal = document.getElementById('attachmentModal');
      const modalFrame = document.getElementById('modalFrame');
      const modalClose = document.getElementById('modalClose');
      document.querySelectorAll('.attachment-link').forEach(link => {
        link.addEventListener('click', function(e) {
          e.preventDefault();
          const url = this.getAttribute('data-url');
          modalFrame.src = url || 'about:blank';
          modal.style.display = 'block';
        });
      });
      modalClose.addEventListener('click', function() {
        modal.style.display = 'none';
        modalFrame.src = '';
      });
      modal.addEventListener('click', function(e) {
        if (e.target === modal) {
          modal.style.display = 'none';
          modalFrame.src = '';
        }
      });
    });
  </script>
</body>
</html>
"""

def _render_node_plain(node):
  if not isinstance(node, dict):
    return ""
  ntype = node.get("type")
  nid = node.get("id", "")
  title = node.get("title", "") or ""
  content = node.get("content", "") or ""
  children_html = "".join(_render_node_plain(ch) for ch in node.get("children", []) or [])
  if ntype == "hero":
    return f'<div class="hero" id="{nid}"><h1>{title}</h1><p>{content}</p></div>'
  if ntype == "info_card":
    price = content.get("price", "") if isinstance(content, dict) else ""
    level = content.get("level", "") if isinstance(content, dict) else ""
    tags = ", ".join(content.get("tags", [])) if isinstance(content, dict) and content.get("tags") else ""
    cta = content.get("cta", "") if isinstance(content, dict) else ""
    btn = f'<button class="cta">{cta}</button>' if cta else ""
    return f'<div class="info-card" id="{nid}"><div><strong>Price:</strong> {price}</div><div><strong>Level:</strong> {level}</div><div><strong>Tags:</strong> {tags}</div>{btn}</div>'
  if ntype == "attachment":
    url = content.get("url", "") if isinstance(content, dict) else ""
    return f'<div class="attachment" id="{nid}"><a href="#" class="attachment-link" data-url="{url}">{title or "Attachment"}</a></div>'
  if ntype == "reviews":
    rating = node.get("meta", {}).get("rating", "N/A") if isinstance(node.get("meta"), dict) else "N/A"
    return f'<div class="reviews" id="{nid}"><h2>Reviews</h2><p>Rating: {rating}</p></div>'
  # default/section
  sect = f'<h2>{title}</h2>' if title else ""
  cont = f'<p>{content}</p>' if content else ""
  return f'<div class="section" id="{nid}">{sect}{cont}{children_html}</div>'


def generate_html(layout: dict, output_path: str, title: str = "Baseline Course UI"):
  out_path = Path(output_path)
  if Environment is None:
    # fallback plain rendering
    body = "".join(_render_node_plain(ch) for ch in layout.get("children", []) or []) if isinstance(layout, dict) else ""
    html = f"<!DOCTYPE html><html><head><meta charset='utf-8'><title>{title}</title></head><body>{body}</body></html>"
  else:
    env = Environment(autoescape=select_autoescape())
    template = env.from_string(HTML_TEMPLATE)
    html = template.render(layout=layout, title=title)
  out_path.write_text(html, encoding="utf-8")
  return str(out_path)
