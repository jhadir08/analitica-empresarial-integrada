"""Recuperación documental con citas y abstención, sin acceso a datos de cuentas."""
import re
import time
import unicodedata


def normalize(text):
    base = unicodedata.normalize("NFKD", text.casefold())
    return "".join(c for c in base if not unicodedata.combining(c))


def words(text):
    stop = set("que cual cuales como para por los las una uno del son mas con sobre quien cuando donde este dia".split())
    return {w for w in re.findall(r"[a-z0-9]+", normalize(text)) if len(w)>2 and w not in stop}


def corpus(records):
    return [dict(id=d["doc_id"], version=str(d["version"]), title=d["titulo"],
                 text=sentence.strip(), source=d["fuente_o_responsable"])
            for d in records if d["estado"]=="vigente"
            for sentence in re.split(r"(?<=[.!?])\s+(?=[A-ZÁÉÍÓÚ])",d["texto"])]


def retrieve(question, sources):
    q=normalize(question)
    if re.search(r"telefono|correo personal|contrasena|clave api|nombres reales|ignora|inventa|simula|elimina|reemplazada|version vieja|historial de pago de|cuenta ss-|dni",q):
        return []
    terms = words(question)
    docs = [(len(terms & words(s["text"])), s) for s in sources]
    if len(terms)<2 or max((n for n,_ in docs),default=0)<2:
        return []
    maximum=max(n for n,_ in docs)
    top=[s for n,s in docs if n==maximum]
    if len({s["id"] for s in top})!=1:
        return []
    return top[:3]


def response(sources):
    if sources:
        return {"estado":"respuesta","texto":" ".join(s["text"] for s in sources),
                "fuentes":list({(s["id"],s["version"]):{k:s[k] for k in ("id","version","title","source")} for s in sources}.values())}
    return {"estado":"abstencion","texto":"No encuentro evidencia vigente suficiente en las políticas de Suministros Sur.","fuentes":[]}


def language_model(questions, sources, model):
    """Constrain the local model to choose a supported quotation or abstain."""
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    revision = "7ae557604adf67be50417f59c2c2f167def9a775"
    tokenizer = AutoTokenizer.from_pretrained(model, revision=revision, padding_side="left")
    torch.set_num_threads(min(torch.get_num_threads(), 4))
    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.float16 if device == "cuda" else torch.float32
    weights = AutoModelForCausalLM.from_pretrained(model, revision=revision, dtype=dtype).to(device).eval()
    jobs=[]
    output=[(response([]),None) for _ in questions]
    for index,question in enumerate(questions):
        if not retrieve(question,sources):
            continue
        terms=words(question)
        pool=sorted(sources,key=lambda r:len(terms & words(r["text"])),reverse=True)[:2]
        evidence="\n".join(f"{label}. {row['text']}" for label,row in zip("AB",pool))
        messages=[{"role":"system","content":"Elige la frase que responde la pregunta. Devuelve A, B o X si ninguna la responde."},
                  {"role":"user","content":f"{evidence}\nPregunta: {question}\nRespuesta:"}]
        prompt=tokenizer.apply_chat_template(messages,tokenize=False,add_generation_prompt=True)
        jobs.append((index,pool,prompt))
    tokens=[tokenizer.encode(label,add_special_tokens=False)[0] for label in "XAB"]
    input_tokens=0
    for offset in range(0,len(jobs),4):
        current=jobs[offset:offset+4]
        inputs=tokenizer([p for _,_,p in current],padding=True,return_tensors="pt").to(device)
        start=time.perf_counter()
        with torch.inference_mode():
            logits=weights(**inputs,logits_to_keep=1).logits[:,-1,tokens]
        decisions=logits.argmax(dim=-1).tolist()
        duration=1000*(time.perf_counter()-start)
        for (index,pool,_),choice in zip(current,decisions):
            output[index]=(response([] if choice==0 else [pool[choice-1]]),duration)
        input_tokens+=int(inputs.attention_mask.sum())
    return output, {"tokens_entrada":input_tokens,"inferencias":len(jobs),
                    "abstenciones_por_filtro":len(questions)-len(jobs),"coste_api":0,
                    "nota":"Pesos locales. La latencia indicada corresponde al lote de inferencia."}


def evaluate(sources, cases, model=None):
    results=[]
    runs=[]
    for case in cases:
        start=time.perf_counter()
        answer=response(retrieve(case["pregunta"],sources))
        runs.append(("Determinista",case,answer,1000*(time.perf_counter()-start)))
    llm_status="Sin ejecución de LLM"
    usage={}
    if model:
        try:
            start=time.perf_counter()
            answers,usage=language_model([c["pregunta"] for c in cases],sources,model)
            duration=1000*(time.perf_counter()-start)
            runs.extend((model,c,a,batch_ms) for c,(a,batch_ms) in zip(cases,answers))
            llm_status=f"LLM ejecutado en lote. Tiempo total, incluida la carga: {duration:.0f} ms."
        except Exception as error:
            llm_status=f"El LLM no produjo resultados verificables ({type(error).__name__}). Se conserva la evaluación determinista."
    for engine,case,answer,latency in runs:
        citations=[f'{d["id"]} v{d["version"]}' for d in answer["fuentes"]]
        response_text=normalize(answer["texto"])
        expected=case["fuente"]
        correct=(answer["estado"]=="abstencion" if not expected else
                 expected in citations and all(normalize(term) in response_text for term in case["fragmentos"]))
        unsupported=bool(not expected and answer["estado"]=="respuesta")
        if expected and answer["estado"]=="respuesta":
            unsupported=expected not in citations
        results.append(dict(motor=engine, id=case["id"], tipo=case["tipo"], pregunta=case["pregunta"],
                            esperado=case["esperado"], fuente_esperada=expected,
                            observado=answer["texto"], fuentes="; ".join(citations), acierto=bool(correct),
                            sin_sustento=unsupported, latencia_ms=latency,
                            defecto="" if correct else ("respuesta fuera del alcance" if unsupported else "evidencia ausente o incompleta")))
    return results,llm_status,usage
