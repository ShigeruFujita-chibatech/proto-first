# main.py

import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from mars_agent_vanila import MarsVanila

vanila_instance = MarsVanila()

@asynccontextmanager
async def lifespan(app:FastAPI):
    global vanila_instance
    vanila_instance = await MarsVanila.start_MarsVanila()
    app.include_router(vanila_instance.router)
    yield

    print('mars_vanila is terminated')

app = FastAPI(lifespan=lifespan)


