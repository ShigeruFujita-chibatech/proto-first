# mars_wbif.py
from typing import Optional
from fastapi import Body, FastAPI, APIRouter, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from mars_base_agent import MarsBaseAgent
import os
import signal
import json
import uvicorn
import uuid
import httpx
import asyncio

# templates-directory for HTMLs files templates directory
templates = Jinja2Templates(directory="templates")

LLM_INFO = {
    "llm_title": "LLM Topics",
    "llm_content": "LLM Response",
    "llm_answer": "not yet request"
    }

class MarsWbIF(MarsBaseAgent):
    def __init__(self,nickname="wbif"):
        MarsBaseAgent.__init__(self,nickname=nickname)
        self.router = APIRouter()
        self.setup_routes()
        print(f'MARS: {self.nickname} is initialised')

    async def start(self):
        print(f'MARS: {self.nickname} starts now')

    def setup_routes(self):
        super().setup_routes()

        @self.router.get("/", response_class=HTMLResponse)
        async def read_item(request: Request):
            """1) Show the default user IF"""
            return templates.TemplateResponse(
                request=request,
                name="index.html",
                context={
                    "llm_title": LLM_INFO["llm_title"],
                    "llm_content": LLM_INFO["llm_content"],
                    "message": None,
                },
            )
        
        # for Web User Interface
        @self.router.post("/submit", response_class=HTMLResponse)
        async def handle_submit(
                request: Request,
                action: str = Form(...),
                proposal_text: Optional[str] = Form(None),
                query_text: Optional[str] = Form(None),
        ):
            """3) a process for FORM format"""
            result_message = ""
            
            if action == "accept":
                result_message = "Accept message is received."

            elif action == "reject":
                result_message = "Reject message is received."

            elif action == "propose":
                result_message = (
                    f"Propose message is received.\n Content: {proposal_text}"
                )

            elif action == "query":
                result_message = (
                    f"Query is received.\n Content: {query_text}"
                )
                # send to LLM_agent
                # get LLM_agent name; hard_coding now; mars_ministral_3_14b_cit_cis_gpu0
                msgDict={}
                msgDict["prompt"]         = result_message
                msgDict["role_direction"] = "Specialist of Software Engineering in Database"
                msgDict["max_tokens"]     = 1024
                msg = self.make_mars_message(performative='query',
                                             # toagent='mars_ministral_3_14b_cit_cis_gpu0',
                                             toagent='mars_specialist',
                                             content=msgDict)
                result_message = "A wait for LLM response"
                await self.send(json_data=msg)
            
            elif action == "cancel":
                result_message = "Cancel is ONLY for the web-browser side process."

            else:
                result_message = "Unknown action message is recieved."
                
            # Redraw Interface with keep information
            return templates.TemplateResponse(
                request=request,
                name="index.html",
                context={
                    "llm_title": LLM_INFO["llm_title"],
                    "llm_content": LLM_INFO["llm_content"],
                    "message": result_message,
                    "llm_answer": LLM_INFO["llm_answer"],
                },
            )
        ##################################################################
        # /info for a human developper
        ##################################################################
        @self.router.get("/info")
        async def show_info():
            return self.my_info()

        ##################################################################
        # recieve answer from LLM, MARS Protocol Handler
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
            
            fromAgent    = msgDict['from_agent']            
            fromHost     = msgDict['from_agent_host']
            fromPort     = msgDict['from_agent_port']
            fromAgentUUID= msgDict['from_agent_uuid']
            toHost       = msgDict['to_agent_host']
            toPort       = msgDict['to_agent_port']
            content      = msgDict['content']
            performative = content['performative']

            toHost       = msgDict['to_agent_host']
            toPort       = msgDict['to_agent_port']
            in_reply_to  = msgDict['reply_with']

            ##################################################################
            # handles performative, answer, echo_request
            ##################################################################
            if (performative == 'echo_request'):
                msg = self.make_mars_message(performative='echo_reply',
                                             toagent=fromAgent,
                                             toagentuuid=fromAgentUUID,
                                             toagenthost=fromHost,
                                             toagentport=fromPort,
                                             content=msgDict)
                print(f'INFO: MARS: {self.nickname} echo_reply send: {msg}')
                await self.send(json_data=msg)
                return {"status":"received"} # reply to agent which sent the echo_request
            elif (performative == 'answer'):
                answer = content['answer']
                LLM_INFO["llm_content"] = answer # content # LLM replys as a raw string which will be post processing
                LLM_INFO["llm_title"]   = "title"
                LLM_INFO["llm_answer"]  = "answer"
                return {"status":"received"} # reply to LLM agent
            else:
                print(f'unknown performative is received: {msgDict}')
                return {"status":"received unknown performative"} # reply to LLM agent
            ###############################################################
            # End of Agent code. No code is adding blow.
            ###############################################################
