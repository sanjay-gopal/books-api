from fastapi import APIRouter
import asyncio
from app.routers.auth import get_current_user
from fastapi import Depends
from typing import Annotated
from fastapi.responses import StreamingResponse

user_dependency = Annotated[dict, Depends(get_current_user)]

router = APIRouter(prefix="/v1/stream", tags=["Streaming CRUD events of Book API"])

#Queue to store the book events
book_queue = asyncio.Queue()

@router.get("/book-events", response_class=StreamingResponse)
async def stream_book_events():
    """
    Streams the book event for all the CRUD operations
    """
    return StreamingResponse(event_generator(), media_type="text/event-stream")


async def event_generator():
    """
    Event generator func stores the events emmited by the GET, PUT, and DELETE methods
    """
    while True:
        try:
            book_event = await asyncio.wait_for(book_queue.get(), timeout=3.0)
            book_queue.task_done()
        except asyncio.TimeoutError:
            continue
        yield f"Book event: {book_event}  \n \n \n"

async def emit_book_event(event: str):
    """
    emit_book_event puts the received event messages to the event queue when the book endpoints are called.
    """
    await book_queue.put(event)