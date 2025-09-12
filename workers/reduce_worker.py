from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, List

app = FastAPI()
tasks_in_progress = 0

class ReduceTask(BaseModel):
    job_id: str
    reduce_id: str
    data: Dict[str, List[int]]  # { "palabra": [1,1,1,1,...] }

@app.post("/reduce_task")
async def reduce_task(task: ReduceTask):

    reduced = {word: sum(values) for word, values in task.data.items()}

    result = {
        "job_id": task.job_id,
        "reduce_id": task.reduce_id,
        "results": reduced
    }
    return result

@app.get("/status")
async def status():
    return {"tasks_in_progress": tasks_in_progress}

