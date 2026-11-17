# mars_agent_vanila_echo_request.py

from fastapi import Body,FastAPI,APIRouter
from mars_base_agent import MarsBaseAgent
import json
import uvicorn
import httpx
import asyncio

class MarsVanilaEchoRequest(MarsBaseAgent):
    def __init__(self,
                 nickname="echo_request"):
        MarsBaseAgent.__init__(self,nickname=nickname)
        self.router = APIRouter()
        self.setup_routes()

        ## Regist to the orchestration_agent
        myBody = {"none":"none"} #regist message does not require content
        msg = make_mars_message(performative='regist',
                                toagent='mars_orchestration_agent',
                                toagentuuid='00000000-0000-0000-0000-000000000000',
                                toagenthost='localhost',
                                toagentport=8000,
                                content=myBody)
        send()
        ## Echo request to the orchestration_agent

        ## show replay and terminate

    def make_mars_message(performative='none',
                          toagent='mars_orchestration_agent',
                          toagentuuid='00000000-0000-0000-0000-000000000000',
                          toagenthost='localhost',
                          toagentport=8000,
                          content='{}'):
        msg = {}
        msg["fromagent"]     = self.nickname
        msg["fromagentuuid"] = self.MARS_agent_uuid
        msg["fromagenthost"] = self.MARS_agent_host_fqdn
        msg["fromagentport"] = self.MARS_agent_port_number
        msg["toagent"]     = toagent
        msg["toagentuuid"] = toagentuuid
        msg["toagenthost"] = toagenthost
        msg["toagentport"] = toagentport
        content['performative'] = performative
        msg["content"]     = content
        
        return json.loads(msg)

    def setup_routes(self):
        super().setup_routes()

        @self.router.get("/")
        async def root():
            return {"announcement": "I'm Vanila Echo Request Agent"}

        @self.router.post("/receive")
        async def json_message_receive(body=Body(...)):
            msgDict  = json.loads(body)
            fromHost = msgDict['from-agent-host']
            fromPort = msgDict['from-agent-port']
            toHost   = msgDict['to-agent-host']
            toPort   = msgDict['to-agent-port']
            content  = msgDict['content']
            performative = msgDict['performative']

            # handles performatvie
            if (performative == 'echo-reply'):
                print(body)
            else:
                print(f'unknown performative is received: {body}')

    ## Think about connection refuse, connection timeout, HTTP error and Request error, at next implementation
    async def send(tohost='localhost',toport=8000,json='{"arg":null}')->bool:
        URI = 'http://'+tohost+':'+toport+':'+'/receive'
        headers = {'content-type':'application/json'}
        try:
            async with httpx.AsyncClient() as http_client:
                response = await http_client.post(URI,headers=headers,json=json)
                mydict = json.load(response.text)
                if mydict['status'] == 'received':
                    return True
                else:
                    return False
        except httpx.TimeoutException as timeout_error:
            print(f'Request Timeout: {timeout_error}')
        except httpx.HTTPStatusError as exc_error:
            print(f'HTTP error, Status:{exc_error.response.status_code}')
        except httpx.RequestError as exc_error:
            print(f'Connection error: {exc_error}')
        return False
        
