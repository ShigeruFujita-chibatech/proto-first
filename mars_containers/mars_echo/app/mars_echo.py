# mars_echo.py

from fastapi import Body,FastAPI,APIRouter, Request
from mars_base_agent import MarsBaseAgent
import uuid
import json
import uvicorn
import httpx
import asyncio

class MarsEcho(MarsBaseAgent):
    def __init__(self,
                 nickname="echo"):
        MarsBaseAgent.__init__(self,nickname=nickname)
        self.router = APIRouter()
        self.setup_routes()
        print(f'MARS: {self.nickname} is initialised')

    async def regist(self):
        ## Regist to the orchestration_agent
        myBody = {"none":"none"} #regist message does not require content
        msg = self.make_mars_message(performative='regist',
                                toagent='mars_orchestration_agent',
                                content=myBody)
        print(f'MARS: {self.nickname} regist() is called')
        print(f'MARS: {msg} in regist()')

        await self.send(json_data=msg) # no return value from await

    async def echo_request(self):
        ## Echo request to the orchestration_agent
        myBody = {"message_type":"mars","performative":"echo_request"} # echo request
        msg = self.make_mars_message(performative='echo_request',
                                toagent='mars_orchestration_agent',
                                content=myBody)
        # print(f'{self.nickname} echo_request() is called')        
        await self.send(json_data=msg) # no return value from await
        
    async def start_MarsEcho(self,nickname='echo'):
        return self
    
    async def loop(self):
        await asyncio.sleep(1) # dummy loop

    def make_mars_message(self,
                          performative='none',
                          toagent='mars_orchestration_agent',
                          toagentuuid='123e4567-e89b-12d3-a456-426614174000',
                          toagenthost='mars_orchestration',
                          toagentport=8000,
                          in_reply_to = '',
                          content=None):

        if content is None:
            content = {}  # 呼び出しごとに新しいdictを作成
        elif isinstance(content, str):
            content = json.loads(content)  # もし JSON 文字列で渡されても dict に復元
        
        msg = {}
        msg["from_agent"]     = self.nickname
        msg["from_agent_uuid"] = self.MARS_agent_uuid
        msg["from_agent_host"] = self.MARS_agent_host_fqdn
        msg["from_agent_port"] = self.MARS_agent_port_number
        msg["to_agent"]     = toagent
        msg["to_agent_uuid"] = toagentuuid
        msg["to_agent_host"] = toagenthost
        msg["to_agent_port"] = toagentport
        content["performative"] = performative
        content["message_type"] = "mars"
        msg["content"]     = content
        msg["reply_with"]       = str(uuid.uuid4())
        msg["in_reply_to"]      = in_reply_to
        return json.dumps(msg, indent=2, ensure_ascii=False)

    def setup_routes(self):
        super().setup_routes()

        @self.router.get("/")
        async def root():
            return {"announcement": "I'm MarsEcho"}

        @self.router.get("/info")
        async def show_info():
            return self.my_info()

        @self.router.post("/receive")
        async def json_message_receive(request: Request):
            body_bytes = await request.body()

            try:
                msgDict = json.loads(body_bytes)
                if isinstance(msgDict,str):
                    msgDict = json.loads(msgDict)
                    
            except (json.JSONDecodeError, TypeError):
                # JSON でない場合は 400 エラーを返して安全に拒否する
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid JSON Payload. Request body must be a valid JSON string."
                )

            formatted_json  = json.dumps(msgDict, indent=4, ensure_ascii=False)
            print(f"MARS: mars_echo.py: recieve: {formatted_json}")
            
            fromHost  = msgDict['from_agent_host']
            fromPort  = msgDict['from_agent_port']
            fromAgent = msgDict['from_agent']
            toHost    = msgDict['to_agent_host']
            toPort    = msgDict['to_agent_port']
            content   = msgDict['content']
            performative = content['performative']
            in_reply_to = msgDict['reply_with']

            # handles performative
            if (performative == 'echo_request'):
                msg = self.make_mars_message(performative='echo_reply',
                                             toagent=fromAgent,
                                             toagentuuid='123e4567-e89b-12d3-a456-426614174000',
                                             toagenthost='assign_by_OA',
                                             toagentport=8000,
                                             in_reply_to = in_reply_to,
                                             content=msgDict)
                print(f'MARS: mars_echo echo_reply send: {msg}')
                await self.send(json_data=msg)
                return {"status":"received"}
            else:
                print(f'unknown performative is received: {msgDict}')
                return {"status":"received unknown performative"}
                
    ## Think about connection refuse, connection timeout, HTTP error and Request error, at next implementation
    async def send(self,to_host='mars_orchestration',to_port=8000,json_data={"arg":"null"}):
        print(f'MARS: send: {json_data}')
        URI = f'http://{to_host}:{to_port}/receive'
        headers = {'Content-Type':'application/json'}
        print(f'MARS: {self.nickname} send to: {URI}')
        try:
            async with httpx.AsyncClient() as http_client:
                response = await http_client.post(URI,headers=headers,json=json_data)
                if response.is_success:
                    try:
                        mydict = response.json()
                        print(f'MARS: receive: {mydict}')
                        status = mydict.get('status')
                        if status == 'received':
                            print(f'MARS: OK, message is received')
                        else:
                            print(f'MARS: Fail: message is not received: {status}')
                    except Exception as e:
                        print(f'MARS: Failed to parse JSON response: {e}')
                elif response.status_code == 422:
                    print('MARS: Validation Error Details (422):', response.text)
                else:
                    print(f'MARS: HTTP Error {response.status_code}: {response.text}')
        except httpx.TimeoutException as timeout_error:
            print(f'Request Timeout: {timeout_error}')
        except httpx.HTTPStatusError as exc_error:
            print(f'HTTP error, Status:{exc_error.response.status_code}')
        except httpx.RequestError as exc_error:
            print(f'Connection error: {exc_error}')
