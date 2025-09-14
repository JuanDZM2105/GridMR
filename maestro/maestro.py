from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, List
import requests
import uuid
import uvicorn

app = FastAPI(title="GridMR Maestro")

MAP_WORKERS = [
    "http://map1:8001",
    "http://map2:8003",
    "http://map3:8005",
    "http://map4:8007"
]

REDUCE_WORKERS = [
    "http://reduce1:8002",
    "http://reduce2:8004"
]

job_states: Dict[str, str] = {}
job_results: Dict[str, Dict] = {}


class JobRequest(BaseModel):
    data: str
    split_size: int = 100
    num_reducers: int = 1
    map_function: str
    reduce_function: str

def split_text(text: str, size: int) -> List[str]:
    words = text.lower().split()
    return [" ".join(words[i:i+size]) for i in range(0, len(words), size)]

def get_least_loaded_worker(workers: List[str]) -> str:
    min_load = float("inf")
    chosen_worker = None
    for w in workers:
        try:
            resp = requests.get(f"{w}/status", timeout=1).json()
            load = resp.get("tasks_in_progress", 0)
            if load < min_load:
                min_load = load
                chosen_worker = w
        except Exception:
            continue
    return chosen_worker or workers[0]

@app.post("/submit_job")
def submit_job(job: JobRequest):
    job_id = str(uuid.uuid4())
    job_states[job_id] = "RUNNING"

    splits = split_text(job.data, job.split_size)
    intermedios: Dict[str, List[int]] = {}

    for i, fragment in enumerate(splits):
        worker_url = get_least_loaded_worker(MAP_WORKERS)
        payload = {
            "job_id": job_id,
            "split_id": f"split_{i}",
            "data": fragment,
            "map_function": job.map_function
        }
        try:
            resp = requests.post(f"{worker_url}/map_task", json=payload)
            resp.raise_for_status()
            results = resp.json()["results"]
        except Exception as e:
            job_states[job_id] = "FAILED"
            return {"error": f"Falló worker MAP {worker_url}: {e}"}

        for palabra, count in results.items():
            intermedios.setdefault(palabra, []).extend(count)

    final_results = {}
    palabras = list(intermedios.keys())

    for i, palabra in enumerate(palabras):
        worker_url = get_least_loaded_worker(REDUCE_WORKERS)
        payload = {
            "job_id": job_id,
            "reduce_id": f"reduce_{i}",
            "data": {palabra: intermedios[palabra]},
            "reduce_function": job.reduce_function
        }
        try:
            resp = requests.post(f"{worker_url}/reduce_task", json=payload)
            resp.raise_for_status()
            results = resp.json()["results"]
        except Exception as e:
            job_states[job_id] = "FAILED"
            return {"error": f"Falló worker REDUCE {worker_url}: {e}"}

        final_results.update(results)

    job_results[job_id] = final_results
    job_states[job_id] = "DONE"

    return {"status": "Job submitted", "job_id": job_id}


@app.get("/job_status/{job_id}")
def job_status(job_id: str):
    return {"job_id": job_id, "state": job_states.get(job_id, "NOT_FOUND")}


@app.get("/job_result/{job_id}")
def job_result(job_id: str):
    if job_states.get(job_id) != "DONE":
        return {"error": "El job aún no está listo o falló"}
    return {"job_id": job_id, "result": job_results[job_id]}
