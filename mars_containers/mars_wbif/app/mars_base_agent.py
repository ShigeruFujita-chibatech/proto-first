# mars_base_agent.py

import os
import signal
import uuid
import json
import socket
import sqlite3
import hashlib
from fastapi import FastAPI,APIRouter, APIRouter, Request
import datetime
import subprocess
import httpx
import asyncio
from abc import ABCMeta
from abc import abstractmethod

class MarsBaseAgent(metaclass = ABCMeta):
    def __init__(self, nickname='mars base agent as an abstract', port_number = 8001, auto_load=True, localhost=True, blackboard_host='mars_orchestration', blackboard_port_number = 8001):
        # Intialize self
        self.nickname  = nickname
        self.localhost = localhost
        self.MARS_agent_uuid = str(uuid.uuid4())
        self.MARS_agent_birthtime = datetime.datetime.now(datetime.timezone.utc) # use UTC timezone ONLY
        self.MARS_agent_file_path_name = str(os.getcwd())
        self.MARS_agent_host_fqdn = str(socket.getfqdn())
        self.MARS_agent_port_number = port_number
        self.MARS_agent_host_name = str(socket.gethostname())
        self.MARS_agent_IPv4_address = str(socket.gethostbyname(self.MARS_agent_host_name))
        self.MARS_agent_file_name = __file__
        mtime = os.stat(__file__).st_mtime
        adjust_utc_mtime = datetime.datetime.fromtimestamp(mtime).astimezone(datetime.timezone.utc)
        self.MARS_agent_file_modified_date = adjust_utc_mtime
        myfile = open(self.MARS_agent_file_name,encoding='utf-8')
        myfilebody = myfile.read()
        self.MARS_agent_file_sha3_512 = hashlib.sha3_512(myfilebody.encode()).hexdigest()
        self.MARS_agent_git_hash = self.get_git_commit_id()
        self.MARS_agent_meta_information = {"information":"base agent"} # will be overwritten by each agent.

        self.MARS_agent_blackboard_host = blackboard_host               # will be deleted eventually
        self.MARS_agent_blackboard_port_number = blackboard_port_number # will be deleted eventually

    def set_meta_information(self, info:dict):
        self.MARS_agent_meta_information = info

    def setup_routes(self):
        @self.router.get("/health")
        def health_check():
            return {"status":"ok"}

    def __del__(self):
        """
        An instance of Sub class must call this method: super.__del__()
        """
        # sendMsgToBlackboard()
        ## unsubscribe all topics to the blackboard
        ## save an information to storage if requested
        
    def print_my_info(self):
        print('I am mars agent:')
        print('nickname: ',self.nickname)
        print('localhost: ',self.localhost)
        print('agent_uuid: ',self.MARS_agent_uuid)
        print('agent_birthtime: ',self.MARS_agent_birthtime)
        print('agent_file_path_name: ',self.MARS_agent_file_path_name)
        print('agent_host_fqdn: ',self.MARS_agent_host_fqdn)
        print('agent_IPv4_address: ',self.MARS_agent_IPv4_address)
        print('agent_port_number: ',self.MARS_agent_port_number)
        print('agent_host_name: ',self.MARS_agent_host_name)
        print('agent_file_name: ',self.MARS_agent_file_name)
        print('agent_file_modified_date: ',self.MARS_agent_file_modified_date)
        print('agent_file_sha3_512: ',self.MARS_agent_file_sha3_512)
        print('agent_git_hash: ',self.MARS_agent_git_hash)
        print('agent_meta_information infomation: ',self.MARS_agent_meta_information)

    def get_git_commit_id(self):
        try:
            result = subprocess.run(["git","show","-s","--format=%H"],capture_output=True,text=True).stdout
            result = result.rstrip('\r\n')
            return result
        except Exception as error:
            # print(error)
            return 'no git command on this environment'

    def is_port_free(self,host: str, port: int) -> bool:
        # socket.AF_INET: IPv4, socket.SOCK_STREAM: TCP
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # 接続のタイムアウトを1秒に設定
            s.settimeout(1.0)
            # connect_exは成功すると0、失敗するとエラーコードを返す
            result = s.connect_ex((host, port))
            # 0以外（エラー）ならポートは空いている
            return result != 0

    # 未使用関数、将来は削除する
    def make_meta_information(self)->dict:
        metaDict = {}
        metaDict['name'] = self.nickname
        metaDict['uuid'] = self.MARS_agent_uuid
        metaDict['hash'] = self.MARS_agent_file_sha3_512
        metaDict['info'] = self.MARS_agent_meta_information
        return metaDict

    async def regist(self):
        ## Regist to the orchestration_agent
        myBody = {}
        myBody['info'] = self.MARS_agent_meta_information # will be stored as a information which is a meta-data of agent its self.
        myBody['info']['file_name'] = self.MARS_agent_file_name
        myBody['info']['file_hash'] = self.MARS_agent_file_sha3_512
        msg = self.make_mars_message(performative='regist',
                                toagent='mars_orchestration_agent',
                                content=myBody)
        # print(f'INFO: MARS: {self.nickname} regist() is called') # Framework Developer uses this
        # print(f'INFO: MARS: {self.nickname} {msg} in regist()')  # Framework Developer uses this

        await self.send(json_data=msg) # no return value from await

    async def unregister(self):
        ## Unregister from the orchestration_agent
        myBody = {"none":"none"} #regist message does not require content
        msg = self.make_mars_message(performative='unregister',
                                toagent='mars_orchestration_agent',
                                content=myBody)
        print(f'INFO: MARS: {self.nickname} unregister() is called')

        await self.send(json_data=msg) # no return value from await

    async def stop_server(self):
        # stop the FastAPI
        print(f"INFO MARS: {self.nickname} is requesting server shutdown...")
        await asyncio.sleep(0.1)
        os.kill(os.getpid(),signal.SIGINT)

    def make_mars_message(self,
                          performative='none',
                          toagent='mars_orchestration_agent',
                          toagentuuid='123e4567-e89b-12d3-a456-426614174000',
                          toagenthost='mars_orchestration',
                          toagentport=8001,
                          content=None):

        if content is None:
            content = {}  # 呼び出しごとに新しい辞書を作成
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
        content['performative'] = performative
        content['message-type'] = 'mars'
        msg["content"]     = content
        msg["reply_with"]   = str(uuid.uuid4()) # will be replase uuidv7() on python 3.14 and upper
        
        return json.dumps(msg, indent=2, ensure_ascii=False)
    
    ## Think about connection refuse, connection timeout, HTTP error and Request error, at next implementation
    async def send(self,to_host='mars_orchestration',to_port=8001,json_data={"arg":"null"}):
        # print(f'INFO: MARS: {self.nickname} send: {json_data}')
        URI = f'http://{to_host}:{to_port}/receive'
        headers = {'Content-Type':'application/json'}
        print(f'INFO: MARS: {self.nickname}, send to: {URI}')
        try:
            async with httpx.AsyncClient() as http_client:
                response = await http_client.post(URI,headers=headers,json=json_data) # SEND! This code.
                if response.is_success:                                               # Check the response
                    try:
                        mydict = response.json()
                        print(f'INFO: MARS: {self.nickname} gets: {mydict}')
                        status = mydict.get('status')
                        if status == 'received':
                            print(f'INFO: MARS: {self.nickname} OK, "received html" message is received')
                        else:
                            print(f'DEBUG: MARS: {self.nickname} Fail: message is not received: {status}')
                    except Exception as e:
                        print(f'ERROR: MARS: {self.nickname} Failed to parse JSON response: {e}')
                elif response.status_code == 422:
                    print('ERROR: MARS: {self.nickname} Validation Error Details (422):', response.text)
                else:
                    print(f'ERROR: MARS: {self.nickname} HTTP Error {response.status_code}: {response.text}')
        except httpx.TimeoutException as timeout_error:
            print(f'ERROR: MARS: {self.nickname} Request Timeout: {timeout_error}')
        except httpx.HTTPStatusError as exc_error:
            print(f'ERROR: MARS: {self.nickname} HTTP error, Status:{exc_error.response.status_code}')
        except httpx.RequestError as exc_error:
            print(f'ERROR: MARS: Connection error: {exc_error}')
  

def main():
    print('mars_base_agent.py is an abstract class! Please make a sub class of this')

    mars_agent_1 = MarsBaseAgent()
    mars_agent_2 = MarsBaseAgent(nickname='I am number two',port_number=8004)

    mars_agent_1.print_my_info()
    mars_agent_2.print_my_info()
    
    print('mars_base_agent.py is an abstract class! Please make a sub class of this')

if __name__ == '__main__':
    main()
