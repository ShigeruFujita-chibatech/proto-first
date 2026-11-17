# main.py in mars_echo_request/app
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from mars_echo_request import MarsEchoRequest

instance = MarsEchoRequest()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await instance.regist()
    await instance.start()
    
    asyncio.create_task(instance.echo_request())
    
    yield
    await instance.unregister()
    
app = FastAPI(lifespan=lifespan)
app.include_router(instance.router)
