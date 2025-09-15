from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, List
import requests
import uuid
import logging

logging.basicConfig(level=logging.INFO)

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


def process_job(job_id: str, job: JobRequest):
    try:
        job_states[job_id] = "RUNNING"
        logging.info(f"[{job_id}] Iniciando job con split_size={job.split_size}, num_reducers={job.num_reducers}")

        # 1. Dividir en splits
        splits = split_text(job.data, job.split_size)
        logging.info(f"[{job_id}] Se generaron {len(splits)} splits")
        intermedios: Dict[str, List[int]] = {}

        # 2. Mandar a workers MAP
        for i, fragment in enumerate(splits):
            logging.info(f"[{job_id}] Enviando split {i} a MAP worker")
            worker_url = get_least_loaded_worker(MAP_WORKERS)
            payload = {
                "job_id": job_id,
                "split_id": f"split_{i}",
                "data": fragment,
                "map_function": job.map_function,
            }
            try:
                resp = requests.post(f"{worker_url}/map_task", json=payload)
                resp.raise_for_status()
                results = resp.json()["results"]
            except Exception as e:
                job_states[job_id] = "FAILED"
                job_results[job_id] = {"error": f"Falló worker MAP {worker_url}: {e}"}
                return

            for palabra, count in results.items():
                intermedios.setdefault(palabra, []).extend(count)

        # 3. Reducir en workers REDUCE
        final_results = {}
        palabras = list(intermedios.keys())

        chunks = [palabras[i::job.num_reducers] for i in range(job.num_reducers)]

        for i, chunk in enumerate(chunks):
            logging.info(f"[{job_id}] Reducer {i} recibió {len(chunk)} claves: {chunk}")
            if not chunk:  # puede haber un lote vacío si hay más reducers que claves
                continue
            worker_url = get_least_loaded_worker(REDUCE_WORKERS)

            # juntar todas las claves de este chunk
            data_chunk = {palabra: intermedios[palabra] for palabra in chunk}

            payload = {
                "job_id": job_id,
                "reduce_id": f"reduce_{i}",
                "data": data_chunk,
                "reduce_function": job.reduce_function
            }

            try:
                resp = requests.post(f"{worker_url}/reduce_task", json=payload)
                resp.raise_for_status()
                results = resp.json()["results"]
            except Exception as e:
                job_states[job_id] = "FAILED"
                job_results[job_id] = {"error": f"Falló worker REDUCE {worker_url}: {e}"}
                return

            final_results.update(results)

        # 4. Guardar resultado
        job_results[job_id] = final_results
        job_states[job_id] = "DONE"

    except Exception as e:
        job_states[job_id] = "FAILED"
        job_results[job_id] = {"error": str(e)}


@app.post("/submit_job")
def submit_job(job: JobRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    job_states[job_id] = "QUEUED"
    background_tasks.add_task(process_job, job_id, job)
    return {"status": "Job encolado", "job_id": job_id}


@app.get("/job_status/{job_id}")
def job_status(job_id: str):
    return {"job_id": job_id, "state": job_states.get(job_id, "NOT_FOUND")}


@app.get("/job_result/{job_id}")
def job_result(job_id: str):
    state = job_states.get(job_id, "NOT_FOUND")
    if state != "DONE":
        return {"error": f"El job no está listo (estado: {state})"}
    return {"job_id": job_id, "result": job_results[job_id]}
