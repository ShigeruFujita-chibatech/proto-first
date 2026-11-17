# mars_Ministral_3_14B_cit_cis_gpu0.py
from typing import Optional
from fastapi import Body, FastAPI, APIRouter, Form, Request
from fastapi.responses import HTMLResponse
from mars_base_agent import MarsBaseAgent
import os
import signal
import json
import uvicorn
import uuid
import httpx
import asyncio

class Mars_Ministral(MarsBaseAgent):
    def __init__(self,nickname="ministral314b"):
        MarsBaseAgent.__init__(self,nickname=nickname)
        self.router = APIRouter()
        self.setup_routes()
        print(f'MARS: {self.nickname} is initialised')

    async def start(self):
        print(f'MARS: {self.nickname} starts now')

    def setup_routes(self):
        super().setup_routes()

        @self.router.get("/", response_class=HTMLResponse)
        async def root(request: Request):
            return {"announcement": "I'm Mars_Ministral314b"}

        @self.router.get("/info")
        async def show_info():
            return self.my_info()
        ##################################################################
        #
        ##################################################################
        @self.router.post("/receive")
        async def json_message_receive(request: Request):
            body_bytes = await request.body()

            try:
                msgDict = json.loads(body_bytes)
                if isinstance(msgDict,str):
                    msgDict = json.loads(msgDict)
                    
            except (json.JSONDecodeError, TypeError):
                # If body_bytes not a JSON, return 400 error to sender
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid JSON Payload. Request body must be a valid JSON string."
                )
            
            fromHost = msgDict['from_agent_host']
            fromPort = msgDict['from_agent_port']
            toHost   = msgDict['to_agent_host']
            toPort   = msgDict['to_agent_port']
            content  = msgDict['content']
            performative = content['performative']

            # handles performative
            if (performative == 'echo_request'):
                msg = self.make_mars_message(performative='echo_reply',
                                             toagent=fromAgent,
                                             toagentuuid='123e4567-e89b-12d3-a456-426614174000',
                                             toagenthost='assign_by_OA',
                                             toagentport=8000,
                                             content=msgDict)
                print(f'INFO: MARS: {self.nickname} echo_reply send: {msg}')
                await self.send(json_data=msg)
                return {"status":"received"}
            else:
                print(f'unknown performative is received: {msgDict}')
                return {"status":"received unknown performative"}
