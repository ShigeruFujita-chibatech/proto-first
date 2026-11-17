# main.py
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from mars_echo import MarsEcho

echo_instance = MarsEcho()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await echo_instance.regist()
    await echo_instance.start_MarsEcho()
    yield
    
app = FastAPI(lifespan=lifespan)

app.include_router(echo_instance.router)
