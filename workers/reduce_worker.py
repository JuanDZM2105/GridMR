from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, List

app = FastAPI()
tasks_in_progress = 0

class ReduceTask(BaseModel):
    job_id: str
    reduce_id: str
    data: Dict[str, List[int]]
    reduce_function: str  # { "palabra": [1,1,1,1,...] }

@app.post("/reduce_task")
async def reduce_task(task: ReduceTask):
    local_env = {}
    exec(task.reduce_function, {}, local_env)
    reduce_fn = local_env["reduce_fn"]

    reduced = {}
    for key, values in task.data.items():
        k, v = reduce_fn(key, values)
        reduced[k] = v

    return {
        "job_id": task.job_id,
        "reduce_id": task.reduce_id,
        "results": reduced
    }

@app.get("/status")
async def status():
    return {"tasks_in_progress": tasks_in_progress}

