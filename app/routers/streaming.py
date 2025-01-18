from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse
import asyncio
from app.routers.auth import get_current_user
from fastapi import Depends
from typing import Annotated
from app.routers.book import events_queue

user_dependency = Annotated[dict, Depends(get_current_user)]

router = APIRouter(prefix="/event", tags=["Streaming CRUD events"])

@router.get("/stream")
async def stream_events(user: user_dependency):
    async def event_generator():
        while True:
            if events_queue:
                event = events_queue.pop(0)  # Get the first event in the queue
                yield (f"data: {event}\n\n")
            await asyncio.sleep(3)
    return EventSourceResponse(event_generator())