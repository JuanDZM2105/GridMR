from fastapi import FastAPI, Request
from pydantic import BaseModel
from collections import Counter
import uvicorn

app = FastAPI()
tasks_in_progress = 0

class MapTask(BaseModel):
    job_id: str
    split_id: str
    data: str
    map_function: str  

@app.post("/map_task")
async def map_task(task: MapTask):
    global tasks_in_progress
    tasks_in_progress += 1

    #words = task.data.lower().split()
    #counts = dict(Counter(words))
    
    # Ejecutar la función enviada
    local_env = {}
    exec(task.map_function, {}, local_env)
    map_fn = local_env["map_fn"]

    # Aplicar sobre el fragmento
    results = {}
    for line in task.data.splitlines():
        for key, value in map_fn(line):
            results.setdefault(key, []).append(value)

    tasks_in_progress -= 1
    return {
        "job_id": task.job_id,
        "split_id": task.split_id,
        "results": results
    }

@app.get("/status")
async def status():
    return {"tasks_in_progress": tasks_in_progress}
