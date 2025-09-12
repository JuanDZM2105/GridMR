from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict
import requests
import uvicorn

app = FastAPI()

job_results = {}

class JobRequest(BaseModel):
    job_id: str
    data: str
    split_size: int
    map_workers: List[str]
    reduce_workers: List[str]

def split_text(text: str, size: int):
    words = text.lower().split()
    for i in range(0, len(words), size):
        yield " ".join(words[i:i+size])

@app.post("/submit_job")
def submit_job(job: JobRequest):
    splits = list(split_text(job.data, job.split_size))
    intermedios = {}

    for i, fragment in enumerate(splits):
        worker_url = job.map_workers[i % len(job.map_workers)]
        payload = {
            "job_id": job.job_id,
            "split_id": f"split_{i}",
            "data": fragment
        }
        resp = requests.post(f"{worker_url}/map_task", json=payload).json()
        for palabra, count in resp["results"].items():
            intermedios.setdefault(palabra, []).extend([1] * count)

    final_results = {}
    palabras = list(intermedios.keys())
    for i, palabra in enumerate(palabras):
        worker_url = job.reduce_workers[i % len(job.reduce_workers)]
        payload = {
            "job_id": job.job_id,
            "reduce_id": f"r{i}",
            "data": {palabra: intermedios[palabra]}
        }
        resp = requests.post(f"{worker_url}/reduce_task", json=payload).json()
        final_results.update(resp["results"])

    job_results[job.job_id] = final_results
    return {"status": "Job submitted", "job_id": job.job_id}

@app.get("/results/{job_id}")
def get_results(job_id: str):
    return job_results.get(job_id, {"error": "No results for this job yet"})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
