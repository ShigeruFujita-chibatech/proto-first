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
    echo_task = asyncio.create_task(instance.echo_request())
    yield
    
    #
    echo_task.cancel()
    try:
        await echo_task
    except asyncio.CancelledError:
        pass
    
    await instance.terminate() # unregister from orchestration
    #
    
app = FastAPI(lifespan=lifespan)

app.include_router(instance.router)
