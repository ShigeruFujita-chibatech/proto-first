# mars_llm_utility_query.py
import os                      # standard module
import httpx                   # pip install httpx
import base64                  # standard module
from dotenv import load_dotenv # pip install dotenv

load_dotenv() # read .env from current directory
llm_username  = os.getenv("LLM_USERNAME")
llm_password  = os.getenv("LLM_PASSWORD")
llm_endpoint  = str(os.getenv("LLM_ENDPOINT"))
llm_maxtokens = 512
# print(llm_endpoint) # confirm at development

def qeury(myURL:str, role:str, prompt:str):
    credentials         = f"{llm_username}:{llm_password}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    # リクエストヘッダ
    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/json"
        }
    # リクエストボディ（OpenAI Chat Completions 互換）
    payload = {
        "messages": [
            {
                "role" : "system",
                "content" : role
            },
            {
                "role": "user",
                "content": prompt}
            ],
        "max_tokens": llm_maxtokens,
        "stream": False
    }

    try:
        with httpx.Client() as client:
            #myURL="https://gpu0.cis.chibatech.ac.jp/llama/minimistral/v1/chat/completions"
            response = client.post(myURL, headers=headers, json=payload, timeout=30)
            response.raise_for_status()  # detection of HTTP error（4xx/5xx）
            result = response.json()
            print(f'INFO: {result}') # development use
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Unexpected error: {str(e)}"

def main():
    prompt              = "共和国の定義は？"
    role                = "歴史の専門家"

    answer = qeury(llm_endpoint, role, prompt)
    print(answer)

if __name__ == '__main__':
    main()