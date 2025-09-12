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

@app.post("/map_task")
async def map_task(task: MapTask):
    global tasks_in_progress
    tasks_in_progress += 1

    words = task.data.lower().split()
    counts = dict(Counter(words))

    result = {
        "job_id": task.job_id,
        "split_id": task.split_id,
        "results": counts
    }

    tasks_in_progress -= 1
    return result

@app.get("/status")
async def status():
    return {"tasks_in_progress": tasks_in_progress}
