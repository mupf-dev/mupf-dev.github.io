# mupf-dev.github.io

Übersichtsseite aller öffentlichen Projekte von [mupf-dev](https://github.com/mupf-dev) – live unter
**https://mupf-dev.github.io/**.

Die Projektliste wird nicht von Hand gepflegt: Der Workflow `.github/workflows/pages.yml` liest bei jedem Push und
einmal täglich alle öffentlichen, eigenen Repositories (ohne Forks) über die GitHub-API aus, erzeugt daraus
`repos.json` und veröffentlicht die Seite. Hat ein Repository GitHub Pages aktiviert, verlinkt die Karte direkt
auf dessen Projektseite.

Lokal testen:

```bash
./scripts/build-data.sh repos.json   # benötigt gh + jq
python3 -m http.server 8000          # dann http://localhost:8000
```
