"""API de lectura del checkpoint y consulta de políticas vigentes."""
import hmac
import json
import os
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, Header, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from assistant import LUNA, LunaError, luna_answers, normalize

BASE = Path(__file__).resolve().parent
app = FastAPI(title="Suministros Sur", version="1.1.0")
snapshot = json.loads((BASE / "salidas" / "tablero.json").read_text(encoding="utf-8"))
sources = snapshot["fuentes"]
fixed_results = {
    normalize(row["pregunta"]).strip(): row
    for row in snapshot["evaluacion_asistente"] if row["motor"] == LUNA
}
source_metadata = {
    f'{source["id"]} v{source["version"]}': {
        field: source[field] for field in ("id", "version", "title", "source")
    }
    for source in sources
}


class Question(BaseModel):
    pregunta: str = Field(min_length=3, max_length=300)


def live_enabled():
    return bool(os.environ.get("OPENAI_API_KEY") and os.environ.get("PMD2_ACCESS_TOKEN"))


@app.get("/api/health")
def health():
    return {"status": "ok", "series": len(snapshot["pronostico"]), "luna_en_vivo": live_enabled()}


@app.get("/api/tablero")
def dashboard():
    return {k: v for k, v in snapshot.items() if k != "fuentes"} | {"luna_en_vivo": live_enabled()}


@app.post("/api/asistente")
def query(body: Question, access_token: Annotated[str | None, Header(alias="X-PMD2-Access")] = None):
    saved = fixed_results.get(normalize(body.pregunta).strip())
    # Las preguntas ya evaluadas se reproducen sin volver a invocar la API.
    if saved:
        citations = [source_metadata[ref] for ref in saved["fuentes"].split("; ") if ref]
        return {"estado": "respuesta" if citations else "abstencion", "texto": saved["observado"],
                "fuentes": citations, "modo": "evaluacion_guardada"}
    if not live_enabled():
        raise HTTPException(503, "La consulta en vivo está desactivada. Selecciona una pregunta evaluada.")
    expected = os.environ["PMD2_ACCESS_TOKEN"]
    if not access_token or not hmac.compare_digest(access_token.encode(), expected.encode()):
        raise HTTPException(403, "Se requiere el código de acceso para una consulta nueva.")
    try:
        answers, _ = luna_answers([body.pregunta], sources)
    except (LunaError, OSError):
        raise HTTPException(502, "Luna no pudo completar la consulta.") from None
    return answers[0] | {"modo": "luna_en_vivo"}


app.mount("/", StaticFiles(directory=BASE / "frontend", html=True), name="frontend")
