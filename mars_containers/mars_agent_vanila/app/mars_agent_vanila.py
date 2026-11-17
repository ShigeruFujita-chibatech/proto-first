# mars_agent_vanila.py

from fastapi import Body,FastAPI,APIRouter
from mars_base_agent import MarsBaseAgent
import json
import uvicorn
import httpx
import asyncio

class MarsVanila(MarsBaseAgent):
    def __init__(self,
                       nickname="mars_vanila"):
        super().__init__(self,nickname=nickname)
        self.router = APIRouter()

    @classmethod
    async def start_MarsVanila(cls):
        instance = cls(nickname='mars_vanila')
        instance.setup_routes()
        
        await asyncio.gather(
            instance.send_regist(),
            instance.send_echo_request()
        )
        return instance

    async def send_regist(self):
        ## Regist to the orchestration_agent
        msg = self.make_mars_message(performative='regist')
        await self.send(json=msg)

    async def send_echo_request(self):
        ## Echo request to the orchestration_agent
        await asyncio.sleep(2) # wait for regist on the orchestration
        msg = self.make_mars_message(performative='echo-request',
                                to_agent='mars_orchestration',
                                to_agent_port=8000)
        await self.send(json=msg)

        ## show replay and terminate
        

    def make_mars_message(self,
                          performative='none',
                          to_agent='mars_orchestration',
                          to_agent_uuid='00000000-0000-0000-0000-000000000000',
                          to_agent_host='mars_orchestration',
                          to_agent_port=8000,
                          content={}):
        msg = {}
        msg["from_agent"]     = self.nickname
        msg["from_agent_uuid"] = self.MARS_agent_uuid
        msg["from_agent_host"] = self.MARS_agent_host_fqdn
        msg["from_agent_port"] = self.MARS_agent_port_number
        msg["to_agent"]     = to_agent
        msg["to_agent_uuid"] = to_agent_uuid
        msg["to_agent_host"] = to_agent_host
        msg["to_agent_port"] = to_agent_port
        content['performative'] = performative
        msg["content"]     = content
        
        return json.dumps(msg)

    def setup_routes(self):
        super().setup_routes()

        @self.router.get("/")
        async def root():
            return {"announcement": "I'm Vanila Agent"}

        @self.router.get("/info")
        async def show_info():
            return self.my_info()

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
            if (performative == 'echo_reply'):
                print(body)
            else:
                print(f'unknown performative is received: {body}')

    ## Think about connection refuse, connection timeout, HTTP error and Request error, at next implementation
    async def send(self,tohost='mars_orchestration',toport=8000,json='{"arg":null}')->bool:
        URI = f'http://{tohost}:{toport}/receive'
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

if __name__ == '__main__':
    async def test():
        my = await MarsVanila.start_MarsVanila()
        print(my.my_info())
    asyncio.run(test())
