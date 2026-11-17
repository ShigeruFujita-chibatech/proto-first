# mars_ministral_3_14b_cit_cis_gpu0.py

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
import requests
import base64
import logging
from dotenv import load_dotenv
import hashlib

load_dotenv()

llm_username = os.getenv("LLM_USERNAME")
llm_password = os.getenv("LLM_PASSWORD")
llm_endpoint = os.getenv("LLM_ENDPOINT")

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Mars_Ministral(MarsBaseAgent):
    # LLMへプロンプトを送り文字列による返答を得る
    def ask_llama_cpp_with_nginx_auth(self,
                                      prompt: str,
                                      role_direction: str,
                                      max_tokens: int) -> str:
        # Basic認証情報の設定
        username            = llm_username
        password            = llm_password
        credentials         = f"{username}:{password}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        # エンドポイント
        url = llm_endpoint

        # リクエストヘッダ
        headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/json"
        }
        
        # リクエストボディ（OpenAI Chat Completions 互換）
        payload = {
            "messages": [
                { "role" : "system",
                  "content" : role_direction},
                {"role": "user",
                 "content": prompt}
            ],
            "max_tokens": max_tokens,
            "stream": False
        }
        
        print(f'INFO: MARS: username:{llm_username}')
        print(f'INFO: MARS: password:{llm_password}')
        print(f'INFO: MARS: url:{llm_endpoint}')
        
        try:
            # LLMの応答時間を考慮し timeout を 30秒 に推奨変更
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()  # HTTPエラー（4xx/5xx）を検知
            result = response.json()
            print(f'DEBUG: {self.nickname}')
            print(f'DEBUG LLM answer result: {result}')
            
            # OpenAI 互換フォーマットから回答テキストを取り出して返す
            return result["choices"][0]["message"]["content"]

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            return f"Error: {str(e)}"
        except (ValueError, KeyError, IndexError) as e:
            logger.error(f"Response parsing error: {e}")
            return "Error: Invalid response structure from server"
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return f"Unexpected error: {str(e)}"

    # .env等の外部ファイルから読み込むようにするべきかもしれない
    def __init__(self,nickname="mars_ministral_3_14b_cit_cis_gpu0"):
        MarsBaseAgent.__init__(self,nickname=nickname)

        # overwritten by each agent.
        self.MARS_agent_file_name = __file__ # overwrite
        myfile = open(self.MARS_agent_file_name,encoding='utf-8')
        myfilebody = myfile.read()
        self.MARS_agent_file_sha3_512 = hashlib.sha3_512(myfilebody.encode()).hexdigest()
        self.MARS_agent_git_hash = self.get_git_commit_id()
        self.MARS_agent_meta_information = {"information":"LLM agent"} # will be orver written by main.py

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
        # Define the MARS_agent message handlers
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
            
            ###############################################################
            # handles performative
            ###############################################################
            if (performative == 'echo_request'):
                msg = self.make_mars_message(performative='echo_reply',
                                             toagent=fromAgent,
                                             toagentuuid=fromAgentUUID,
                                             toagenthost=fromHost,
                                             toagentport=fromPort,
                                             content=msgDict)
                print(f'INFO: MARS: {self.nickname} echo_reply send: {msg}')
                await self.send(json_data=msg)
                return {"status":"received"}
            elif (performative == 'query'):

                # get prompt, role_direction, and max_token from content
                prompt         = content["prompt"]
                role_direction = content["role_direction"]
                max_tokens     = content["max_tokens"]

                # qeury to LLM
                rst_str = self.ask_llama_cpp_with_nginx_auth(prompt=prompt,
                                              role_direction=role_direction,
                                              max_tokens=max_tokens)

                # make JSON reply from answer from LLM
                reply_content = {}
                reply_content["answer"] = rst_str
                msg = self.make_mars_message(
                    performative='answer',
                    toagent=fromAgent,
                    toagentuuid=fromAgentUUID,
                    toagenthost=fromHost,
                    toagentport=fromPort,
                    content=reply_content)

                # send JSON to query sender agent
                await self.send(json_data=msg)
                # task = asyncio.create_task(self.send(json_data=msg)) #Asyncronous send no wait response from other agent
                
                return {"status":"received"} # for HTTP response, not a MARS protocol
            else:
                print(f'unknown performative is received: {msgDict}')
                return {"status":"received unknown performative"}
            ###############################################################
            # End of Agent code. No code is adding blow.
            ###############################################################