# main.py

import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from mars_orchestration_agent import OrchestrationAgent

vanila_instance = None

@asynccontextmanager
async def lifespan(app:FastAPI):
    global orchestration_instance
    orchestration_instance = await OrchestrationAgent.start_Orchestration()
    app.include_router(orchestration_instance.router)
    yield

    print('OrchestrationAgent is terminated')

app = FastAPI(lifespan=lifespan)
