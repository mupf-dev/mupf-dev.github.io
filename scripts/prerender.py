"""Schreibt die Projektliste als statisches HTML in index.html (für Suchmaschinen) und erzeugt sitemap.xml und robots.txt."""
import html
import json
import sys
from pathlib import Path

data_path, site = Path(sys.argv[1]), Path(sys.argv[2])
data = json.loads(data_path.read_text())
base = f"https://{data['owner']}.github.io/"
day = data["generated"][:10]

items = []
for r in data["repos"]:
    live = r.get("pages") or r.get("homepage")
    title = html.escape(r.get("title") or r["name"])
    desc = html.escape(r.get("description") or "")
    link = f'<a href="{html.escape(live)}">{title}</a>' if live else title
    items.append(f'<li>{link} – {desc} (<a href="{html.escape(r["url"])}">Code</a>)</li>')
static = '<ul class="static-list">\n' + "\n".join(items) + "\n</ul>"

index = site / "index.html"
page = index.read_text()
page = page.replace('<div id="list"></div>', f'<div id="list">{static}</div>', 1)
index.write_text(page)

urls = [base] + [r["pages"] for r in data["repos"] if r.get("pages")]
(site / "sitemap.xml").write_text(
    '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    + "".join(f"  <url><loc>{html.escape(u)}</loc><lastmod>{day}</lastmod></url>\n" for u in urls)
    + "</urlset>\n"
)
(site / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {base}sitemap.xml\n")
print(f"{len(items)} Projekte statisch, {len(urls)} URLs in sitemap.xml")
