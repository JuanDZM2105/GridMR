from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, List
import requests
import uuid
import uvicorn

app = FastAPI(title="GridMR Maestro")

# === Configuración inicial ===
MAP_WORKERS = [
    "http://localhost:8001",
    "http://localhost:8003",
    "http://localhost:8005",
    "http://localhost:8007"
  ]
   # Lista de workers MAP
   
REDUCE_WORKERS = [
    "http://localhost:8002",
    "http://localhost:8004"
  ]  # Lista de workers REDUCE

# === Estado global ===
job_states: Dict[str, str] = {}   # job_id -> estado
job_results: Dict[str, Dict] = {} # job_id -> resultado final


# === Modelos ===
class JobRequest(BaseModel):
    data: str
    split_size: int = 100
    num_reducers: int = 1


# === Funciones auxiliares ===
def split_text(text: str, size: int) -> List[str]:
    """Divide un texto en bloques de 'size' palabras."""
    words = text.lower().split()
    return [" ".join(words[i:i+size]) for i in range(0, len(words), size)]


# === Endpoints ===
@app.post("/submit_job")
def submit_job(job: JobRequest):
    # 1. Crear ID único y registrar estado
    job_id = str(uuid.uuid4())
    job_states[job_id] = "RUNNING"

    # 2. Dividir en splits
    splits = split_text(job.data, job.split_size)
    intermedios: Dict[str, List[int]] = {}

    # 3. Asignar a workers MAP
    for i, fragment in enumerate(splits):
        worker_url = MAP_WORKERS[i % len(MAP_WORKERS)]
        payload = {
            "job_id": job_id,
            "split_id": f"split_{i}",
            "data": fragment
        }
        try:
            resp = requests.post(f"{worker_url}/map_task", json=payload)
            resp.raise_for_status()
            results = resp.json()["results"]
        except Exception as e:
            job_states[job_id] = "FAILED"
            return {"error": f"Falló worker MAP {worker_url}: {e}"}

        # Acumular resultados
        for palabra, count in results.items():
            intermedios.setdefault(palabra, []).extend([1] * count)

    # 4. Asignar a workers REDUCE
    final_results = {}
    palabras = list(intermedios.keys())

    for i, palabra in enumerate(palabras):
        worker_url = REDUCE_WORKERS[i % len(REDUCE_WORKERS)]
        payload = {
            "job_id": job_id,
            "reduce_id": f"reduce_{i}",
            "data": {palabra: intermedios[palabra]}
        }
        try:
            resp = requests.post(f"{worker_url}/reduce_task", json=payload)
            resp.raise_for_status()
            results = resp.json()["results"]
        except Exception as e:
            job_states[job_id] = "FAILED"
            return {"error": f"Falló worker REDUCE {worker_url}: {e}"}

        final_results.update(results)

    # 5. Guardar y actualizar estado
    job_results[job_id] = final_results
    job_states[job_id] = "DONE"

    return {"status": "Job submitted", "job_id": job_id}


@app.get("/job_status/{job_id}")
def job_status(job_id: str):
    """Consultar estado de un job."""
    return {"job_id": job_id, "state": job_states.get(job_id, "NOT_FOUND")}


@app.get("/job_result/{job_id}")
def job_result(job_id: str):
    """Obtener resultados de un job ya terminado."""
    if job_states.get(job_id) != "DONE":
        return {"error": "El job aún no está listo o falló"}
    return {"job_id": job_id, "result": job_results[job_id]}


# === Main ===
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)