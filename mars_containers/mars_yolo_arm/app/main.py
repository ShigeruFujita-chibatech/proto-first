# main.py
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from mars_agent_vanila_echo_request import MarsVanilaEchoRequest

echo_instance = MarsVanilaEchoRequest()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await echo_instance.regist()
    await echo_instance.start_MarsVanilaEchoRequest()
    echo_task = asyncio.create_task(echo_instance.echo_request())
    yield
    
app = FastAPI(lifespan=lifespan)

app.include_router(echo_instance.router)
