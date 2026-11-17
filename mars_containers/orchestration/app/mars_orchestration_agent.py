# mars_orcestration_agent.py
from fastapi import Body,FastAPI,APIRouter, Request, HTTPException
import uuid
import json
import uvicorn
import psycopg2
from psycopg2 import DatabaseError,OperationalError, Error
from mars_base_agent import MarsBaseAgent
import httpx
import asyncio

class OrchestrationAgent(MarsBaseAgent):
    def __init__(self,
                 nickname='mars_orchestration_agent',
                 port_number = 8000,
                 auto_load=True,
                 localhost=True,
                 blackboard_host='mars_orchestration_agent',
                 blackboard_port_number = 8000):
        MarsBaseAgent.__init__(self,
                               nickname='mars_orchestration_agent',
                               port_number = 8000,
                               auto_load=True,
                               localhost=True,
                               blackboard_host='mars_orchestration_agent',
                               blackboard_port_number = 8000)
        print(f'INFO: MARS: {self.MARS_agent_host_fqdn}')
        try:
            self.connection = psycopg2.connect(
                host = 'mars_database',
                dbname = 'mars_db',
                user = 'mars_agent',
                password = '',
                port = 5432)
        except OperationalError as op_error:
            print(f'ERROR: MARS: {self.nickname}, Connection Error, Check host,dbname,user,password and portnumber: {op_error}')
        except DatabaseError as db_error:
            print(f'ERROR: MARS: {self.nickname}, Database error: {db_error}')
        except Error as my_error:
            print(f'ERROR: MARS: {self.nickname}, Error: {my_error}')
        
        self.router = APIRouter()
        self.setup_routes()

        self.agents = {} # {key:uuid, value:{'agent_name':str,'agent_uuid':uuid,'hostname':str,
                         #                   'port_number':int,'live_flag':bool,'information':json}}
        self.tasks  = [] # keep task (task := message send) # taskを維持すると、ゴミが残るかもしれない。

    @classmethod
    async def start_Orchestration(cls):
        instance = cls(nickname='orchestration')
        instance.setup_routes()

        await asyncio.gather(
            instance.loop() # dummy
        )
        return instance

    async def loop(self):
        await asyncio.sleep(1) # dummy loop

    def setup_routes(self):
        # regist parents class routes at first
        super().setup_routes()

        # define orchestration_agent specific routes
        @self.router.get("/")
        async def root():
            return {"announcement": "I'm Orcestration Agent"}

        @self.router.get("/agents")
        async def get_agents():
            return self.agents

        @self.router.get("/agent_list")
        async def get_agent_list():
            ag_list = self.make_agent_list_content() # For example: {"performative":"reply_agent_list","agent_list":["echo","echo_request","yolo","ffmpeg","wbif"]}
            return {"content":ag_list,"content":ag_list}

        """ START Router Process """
        @self.router.post("/receive")
        async def json_message_receive(request: Request):
            body_bytes = await request.body()

            try:
                msgDict = json.loads(body_bytes)
                if isinstance(msgDict,str):
                    msgDict = json.loads(msgDict)
                
            except (json.JSONDecodeError, TypeError):
                # return 400 error, when received data is not JSON.
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid JSON format. Request body must be a valid JSON string."
                )
            
            self.logging(msgDict) # message_log is a table name of database mars_db

            agent_name  = msgDict['from_agent']
            agent_uuid  = msgDict['from_agent_uuid']
            from_Host   = msgDict['from_agent_host']
            from_Port   = msgDict['from_agent_port']
            to_Agent    = msgDict['to_agent']
            to_Host     = msgDict['to_agent_host']
            to_Port     = msgDict['to_agent_port']
            content     = msgDict['content']
            in_reply_to = msgDict['reply_with']
            performative = msgDict['content']['performative']
            
            if msgDict['to_agent'] == self.nickname:
                # OA is requested action
                if (performative == 'echo_request'):
                    msg = self.make_mars_message(fromagent=self.nickname,
                                                 fromagentuuid=self.MARS_agent_uuid,
                                                 fromagenthost=self.MARS_agent_host_name,
                                                 fromagentport=self.MARS_agent_port_number,
                                                 toagent=agent_name,
                                                 toagentuuid=agent_uuid,
                                                 toagenthost=from_Host,
                                                 toagentport=from_Port,
                                                 performative='echo_reply',
                                                 content=msgDict)
                    msg['in_replay_to'] = in_reply_to
                    print(f'INFO: MARS: {self.nickname}, echo_reply send: {msg}')
                    await self.send(to_host=from_Host,to_port=from_Port,json_data=msg)
                    return {"status":"received"}

                elif (performative == 'regist'):
                    # INSERT INFORMATION TO DB
                    self.regist_agent(msgDict) # to postgresql
                    meta_info = content["info"] # content['meta_info'] is defined as meta-information of agent
                    self.agents[agent_uuid]={'agent_name':agent_name,
                                            'agent_uuid':agent_uuid,
                                            'hostname':from_Host,
                                            'port_number':from_Port,
                                            'live_flag':True,
                                            'information':meta_info}
                    
                elif (performative == 'unregister'):
                    # DELETE FROM MARS_DB:
                    self.unregister_agent(msgDict) # to postgresql
                    ag = self.agents.pop(agent_uuid)
                    print(f'INFO: MARS: {self.nickname} deletes {ag}')

                elif (performative == 'request_agent_list'):
                    ag_list = self.make_agent_list_content() # For example: {"performative":"reply_agent_list","agent_list":["echo","echo_request","yolo","ffmpeg","wbif"]}
                    msg = self.make_mars_message(fromagent=self.nickname,
                                                 fromagentuuid=self.MARS_agent_uuid,
                                                 fromagenthost=self.MARS_agent_host_name,
                                                 fromagentport=self.MARS_agent_port_number,
                                                 toagent=agent_name,
                                                 toagentuuid=agent_uuid,
                                                 toagenthost=from_Host,
                                                 toagentport=from_Port,
                                                 performative='reply_agent_list',
                                                 content=ag_list)
                    await self.send(to_host=from_Host,to_port=from_Port,json_data=msg)
                    return {"status":"received"}
                
                # add another performative for OA here

                # finally message does not understand 
                else:
                    print(f'DEBUG: MARS: Orchestration gets unkown performative for OA')
                    msg = self.make_mars_message(performative='does_not_understand_performative',content=json.dumps(msgDict))
                    await self.send(to_agent=agent_name,to_host=from_Host,to_port=from_Port,json_data=msg)
                    
                return {"status":"received"}

            elif self.check_agent_exist_by_name(agent_name=to_Agent) == True:
                msg = msgDict
                candidate_agent_info = [
                    inner_dict for inner_dict in self.agents.values() if inner_dict.get("agent_name") == to_Agent
                    ]
                # In the future, multiple dict will be return caused by multiple agent_name are occured.
                to_Host  = candidate_agent_info[0]["hostname"]
                to_Port  = candidate_agent_info[0]["port_number"]
                # to_Agent = candidate_agent_info[0]["agent_name"] # is already has in msg
                to_UUID  = candidate_agent_info[0]["agent_uuid"]

                msg['to_agent_uuid'] = to_UUID
                msg['to_agent_host'] = to_Host
                msg['to_agent_port'] = to_Port
                
                # await self.send(to_host=to_Host,to_port=to_Port,json_data=msg) #同期メッセージパッシング
                task = asyncio.create_task(self.send(to_host=to_Host,to_port=to_Port,json_data=msg) )# 非同期メッセージパッシング
                self.tasks.append(task) # keep task # ゴミとして残るかもしれない。
                return {"status":"received"}
            else:
                print(f'DEBUG: MARS: {to_Agent} does not exit in agents on OA')
                myJson = self.make_mars_message(performative='agent_does_not_exist',
                                           content=content)
                await self.send(to_host=from_Host,to_port=from_Port,json_data=myJson)
                return {"status":"agent does not exist"}
            
        return {"status":"received"} # anyone reaches this
        """ END Router Process """
    
    def check_agent_exist_by_uuid(self, myUUID):
        if myUUID in self.agents:
            return True
        else:
            return False

    def check_agent_exist_by_name(self, agent_name:str)->bool:
        for uuid, info in self.agents.items():
            print(f'DEBUG: MARS: in check_agent_exist_by_name: {agent_name}')
            print(f'DEBUG: MARS: {info}')
            if info.get("agent_name") == agent_name:
                return True
        return False

    ## Think about connection refuse, connection timeout, HTTP error and Request error, at next implementation
    async def send(self,to_host='localhost',to_port=8001,json_data={"arg":"null"}):
        # print(f'MARS: send: {json_data}')
        URI = f'http://{to_host}:{to_port}/receive'
        headers = {'Content-Type':'application/json'}
        try:
            async with httpx.AsyncClient() as http_client:
                response = await http_client.post(URI,headers=headers,json=json_data)
                if response.is_success:
                    try:
                        mydict = response.json()
                        # print(f'MARS OA: received: {mydict}')
                        status = mydict.get('status')
                        if status == 'received':
                            print(f'INFO: MARS {self.nickname}: OK, sending message is received by RA/UA')
                            ## BUG duplicated log, self.logging(json_data) # keep log on database 
                        else:
                            print(f'DEBUG MARS Fail:{self.nickname}: message is not received: {status} msg_json_data: {json_data}')
                    except Exception as e:
                        print(f'ERROR: MARS: {self.nickname}, Failed to parse JSON response: {e}')
                elif response.status_code == 422:
                    print('ERROR: MARS: {self.nickname}, Validation Error Details (422):', response.text)
                else:
                    print(f'ERROR: MARS: {self.nickname}, HTTP Error {response.status_code}: {response.text}')
        except httpx.TimeoutException as timeout_error:
            print(f'ERROR: MARS: {self.nickname}, Request Timeout: {timeout_error}')
        except httpx.HTTPStatusError as exc_error:
            print(f'ERROR: MARS: {self.nickname}, HTTP error, Status:{exc_error.response.status_code}')
        except httpx.RequestError as exc_error:
            print(f'ERROR: MARS: {self.nickname}, Connection error: {exc_error}')


    def make_mars_message(self,
                          fromagent='mars_orchestration_agent',
                          fromagentuuid='',
                          fromagenthost='mars_orchestration_agent',
                          fromagentport=8000,
                          toagent='none',
                          toagentuuid='',
                          toagenthost='',
                          toagentport=8000,
                          performative='none',
                          content=None):
        if content is None:
            content = {} # 呼び出しごとに新しい辞書を作成
        elif isinstance(content, str):
            content = json.loads(content) # もし JSON 文字列で渡されても dict に復元
        
        msg = {}
        msg["from_agent"]       = fromagent
        msg["from_agent_uuid"]  = fromagentuuid
        msg["from_agent_host"]  = fromagenthost
        msg["from_agent_port"]  = fromagentport
        msg["to_agent"]         = toagent
        msg["to_agent_uuid"]    = toagentuuid
        msg["to_agent_host"]    = toagenthost
        msg["to_agent_port"]    = toagentport
        content["performative"] = performative
        content["message_type"] = "mars"
        msg["content"]          = content
        msg["reply_with"]       = str(uuid.uuid4())
        
        return json.dumps(msg,indent=2, ensure_ascii=False)


    def regist_agent(self,msgDict):
        cursor = self.connection.cursor()
        # msgDict = json.loads(receiveJSON)
        fromAg = msgDict['from_agent']
        fromUUID = msgDict['from_agent_uuid']
        fromHost = msgDict['from_agent_host']
        fromPort = msgDict['from_agent_port']
        information = json.dumps(msgDict['content']) 
            
        SQL="""
        INSERT INTO agents (agent_name,agent_uuid,hostname,port_number,live_flag,information)
                VALUES (%s,%s,%s,%s,%s,%s);
        """

        try:
            cursor.execute(SQL, (fromAg,fromUUID,fromHost,fromPort,'True',information))
            self.connection.commit()
        except OperationalError as error:
            self.connection.rollback()
            print(f'ERROR: MARS: {self.nickname}, {error}')
        finally:
            cursor.close()

    def unregister_agent(self,msgDict):
        cursor = self.connection.cursor()
        # msgDict = json.loads(receiveJSON)
        fromAg = msgDict['from_agent']
        fromUUID = msgDict['from_agent_uuid']
        fromHost = msgDict['from_agent_host']
        fromPort = msgDict['from_agent_port']
        information = json.dumps(msgDict['content']) 
            
        SQL="""
        DELETE FROM agents
           WHERE agent_name=%s
           AND agent_uuid=%s
           AND hostname=%s
           AND port_number=%s;
        """

        try:
            cursor.execute(SQL, (fromAg,fromUUID,fromHost,fromPort))
            self.connection.commit()
        except OperationalError as error:
            self.connection.rollback()
            print(f'ERROR: MARS: {self.nickname}, {error}')
        finally:
            cursor.close()
                
    def make_agent_list_content(self): # For example: {"performative":"reply_agent_list","agent_list":["echo","echo_request","yolo","ffmpeg","wbif"]}
        myDict = {"performative":"replay_agent_list"}
        myList = [d["agent_name"] for d in self.agents.values()]
        myDict["agent_list"] = myList
        return myDict

    def logging(self, msgDict):
        cursor = self.connection.cursor()
        try:
            if isinstance(msgDict, str):
                receiveJSON = msgDict
                msgDict = json.loads(msgDict)
            else:
                receiveJSON = json.dumps(msgDict)
            
            fromAg = msgDict['from_agent']
            toAgent = msgDict['to_agent']
            fromUUID = msgDict['from_agent_uuid']
            toUUID = msgDict['to_agent_uuid']
                
            SQL = """
            INSERT INTO message_log (from_agent, from_agent_uuid, to_agent, to_agent_uuid, message)
            VALUES (%s, %s, %s, %s, %s);
            """
            receiveJSON = json.dumps(msgDict)
            cursor.execute(SQL, (fromAg, fromUUID, toAgent, toUUID, receiveJSON))
            self.connection.commit()
        except Exception as error:  # JSONエラーやDBの他のエラーもまとめて捕捉
            self.connection.rollback()
            print(f"ERROR: MARS: {self.nickname}, Logging error: {error}")
        finally:
                cursor.close()
# only test user, normally container call this
if __name__ == "__main__":
    uvicorn.run("mars_orchestration_agent:app",
                host=app.MARS_agent_host_fqdn,
                port=app.MARS_agent_port_number,
                reload=True,
                log_level="debug")
