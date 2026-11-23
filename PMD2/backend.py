"""API de lectura del checkpoint y consulta de políticas vigentes."""
import json
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from assistant import response, retrieve

BASE = Path(__file__).resolve().parent
app = FastAPI(title="Suministros Sur", version="1.0.0")
snapshot = json.loads((BASE/"salidas"/"tablero.json").read_text(encoding="utf-8"))


class Question(BaseModel):
    pregunta: str = Field(min_length=3, max_length=300)


@app.get("/api/health")
def health():
    return {"status":"ok", "series":len(snapshot["pronostico"])}


@app.get("/api/tablero")
def dashboard():
    return {k:v for k,v in snapshot.items() if k!="fuentes"}


@app.post("/api/asistente")
def query(body: Question):
    return response(retrieve(body.pregunta,snapshot["fuentes"]))


app.mount("/",StaticFiles(directory=BASE/"frontend",html=True),name="frontend")
