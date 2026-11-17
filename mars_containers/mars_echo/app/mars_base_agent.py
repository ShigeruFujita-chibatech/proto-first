# mars_base_agent.py

import os
import uuid
import json
import socket
import sqlite3
import hashlib
from fastapi import FastAPI,APIRouter
# import uvicorn
import datetime
#import requests
import subprocess
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
        self.MARS_agent_blackboard_host = blackboard_host
        self.MARS_agent_blackboard_port_number = blackboard_port_number

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
        print('agent_blackboard_host: ',self.MARS_agent_blackboard_host)
        print('agent_blackboard_host: ',self.MARS_agent_blackboard_port_number)

    def get_git_commit_id(self):
        try:
            result = subprocess.run(["git","show","-s","--format=%H"],capture_output=True,text=True).stdout
            result = result.rstrip('\r\n')
            return result
        except Exception as error:
            # print(error)
            return 'no git command on this environment'

    def is_port_free(host: str, port: int) -> bool:
        # socket.AF_INET: IPv4, socket.SOCK_STREAM: TCP
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # 接続のタイムアウトを1秒に設定
            s.settimeout(1.0)
            # connect_exは成功すると0、失敗するとエラーコードを返す
            result = s.connect_ex((host, port))
            # 0以外（エラー）ならポートは空いている
            return result != 0


def main():
    print('mars_base_agent.py is an abstract class! Please make a sub class of this')

    mars_agent_1 = MarsBaseAgent()
    mars_agent_2 = MarsBaseAgent(nickname='I am number two',port_number=8002)

    mars_agent_1.print_my_info()
    mars_agent_2.print_my_info()
    
    print('mars_base_agent.py is an abstract class! Please make a sub class of this')

if __name__ == '__main__':
    main()
