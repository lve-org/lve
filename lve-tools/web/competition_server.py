"""
Simple fastapi and uvicorn-based HTTP server for 
serving LVE competitions.
"""
import os
import sys
import json
import asyncio
import time
import random
from lve.lve import LVE

from fastapi.responses import StreamingResponse
from starlette.responses import Response
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.background import BackgroundTask
from starlette.types import Receive, Scope, Send


import fastapi

app = fastapi.FastAPI()

@app.get("/competition/{competition_id}/leaderboard")
async def get_leaderboard(competition_id: str):
    """
    Get the leaderboard for a given competition.
    """
    return {
        "competition_id": competition_id,
        "leaderboard": [
            {
                "user_id": "user1",
                "score": 123,
            }
        ]
    }

@app.post("/competition/{competition_id}/submit")
async def submit(competition_id: str, request: Request):
    """
    Submit a solution to a given competition.

    The response is an SSE stream that will update
    as the user submission is evaluated and scored.
    """
    # body parameters
    params = await request.json()

    async def event_generator():
        yield "data: {}\n\n".format(json.dumps({"status": "processing", "parameters": params}))
        
        fake_response = [
            " This",
            " is",
            " a",
            " fake",
            " response"
        ]
        
        for token in fake_response:
            yield "data: {}\n\n".format(json.dumps({"token": token}))
            await asyncio.sleep(0.1)
        
        if random.random() > 0.5:
            yield "data: {}\n\n".format(json.dumps({"status": "success", "score": 123}))
        else:
            yield "data: {}\n\n".format(json.dumps({"status": "failed"}))

    return StreamingResponse(event_generator(), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    # access control policy
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )

    uvicorn.run(app, host="localhost", port=9999)