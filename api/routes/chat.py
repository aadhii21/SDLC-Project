from fastapi import APIRouter
from pydantic import BaseModel
from queues.redis_queue import queue,redis_conn
from rq.job import Job
from queues.worker import process_query

router=APIRouter()
class ChatRequest(BaseModel):
    query:str

@router.post("/chat")
async def chat(request:ChatRequest):
    job=queue.enqueue(
        process_query,
        request.query
    )
    return{
        "job_id":job.id,
        "status":"queued"
    }
@router.get("/jobstatus/{job_id}")
async def get_status(job_id:str):
    job=Job.fetch(
        job_id,
        connection=redis_conn
    )
    if job.isfinished:
        return{
            "status":"finished",
            "result":job.result
        }
    if job.isfailed:
        return{
            "status":"failed",
        }
    return{
        "status":job.get_started()
    }