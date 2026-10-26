"""Ergänzt repos.json um Titel und Screenshots von der jeweiligen Projektseite (GitHub Pages)."""
import json
import sys
import urllib.request
from html.parser import HTMLParser
from urllib.parse import urljoin

MAX_IMAGES = 5
SKIP = ("shields.io", "badge", "logo", "icon", "favicon", "avatar", "${")


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title, self.og_title, self.og_image = "", None, None
        self.images, self._in_title = [], False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "title":
            self._in_title = True
        elif tag == "meta" and a.get("property") == "og:title":
            self.og_title = a.get("content")
        elif tag == "meta" and a.get("property") == "og:image":
            self.og_image = a.get("content")
        elif tag == "img" and a.get("src"):
            # Hell/Dunkel-Paare nur einmal aufnehmen
            if "theme-only-light" not in (a.get("class") or ""):
                self.images.append(a["src"])

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data


def fetch(url, method="GET"):
    req = urllib.request.Request(url, method=method, headers={"User-Agent": "portfolio-builder"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read().decode("utf-8", "replace") if method == "GET" else r.status


def exists(url):
    try:
        return fetch(url, "HEAD") == 200
    except Exception:
        return False


def enrich(repo):
    page = repo.get("pages") or repo.get("homepage")
    repo["title"], repo["tagline"], repo["images"] = None, None, []
    if not page:
        return
    try:
        p = PageParser()
        p.feed(fetch(page))
    except Exception as e:
        print(f"  {repo['name']}: Seite nicht lesbar ({e})", file=sys.stderr)
        return

    title = (p.og_title or p.title).strip()
    if title:
        name, _, tagline = title.partition(" – ")
        repo["title"], repo["tagline"] = name.strip(), tagline.strip() or None

    candidates = ([p.og_image] if p.og_image else []) + p.images
    seen = []
    for src in candidates:
        url = urljoin(page, src)
        if url in seen or any(s in url.lower() for s in SKIP):
            continue
        if exists(url):
            seen.append(url)
        if len(seen) >= MAX_IMAGES:
            break
    repo["images"] = seen


path = sys.argv[1]
with open(path) as f:
    data = json.load(f)
for repo in data["repos"]:
    enrich(repo)
    print(f"  {repo['name']}: {repo['title']!r}, {len(repo['images'])} Bilder", file=sys.stderr)
with open(path, "w") as f:
    json.dump(data, f, ensure_ascii=False, indent=1)
