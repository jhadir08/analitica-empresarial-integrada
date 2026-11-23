"""Prepara los archivos estáticos de Netlify con el snapshot del checkpoint."""
import argparse
import json
import shutil
from pathlib import Path
from urllib.parse import urlparse

project = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("destino", type=Path)
parser.add_argument("--render-url")
args = parser.parse_args()
target = args.destino
target.mkdir(parents=True, exist_ok=True)
for name in ("index.html", "styles.css", "app.js"):
    shutil.copy2(project/"frontend"/name,target/name)

snapshot = json.loads((project/"salidas"/"tablero.json").read_text(encoding="utf-8"))
snapshot.pop("fuentes", None)
(target/"tablero.json").write_text(json.dumps(snapshot,ensure_ascii=False),encoding="utf-8")
if args.render_url:
    url = urlparse(args.render_url)
    if url.scheme != "https" or not url.hostname or not url.hostname.endswith(".onrender.com") or url.path not in ("","/") or url.query or url.fragment or url.username:
        parser.error("--render-url debe ser la URL HTTPS del servicio de Render.")
    (target/"_redirects").write_text(f"/api/* https://{url.netloc}/api/:splat 200\n",encoding="utf-8")
elif (target/"_redirects").exists():
    parser.error("El directorio ya contiene un proxy. Use un destino nuevo para la vista de resultados.")
