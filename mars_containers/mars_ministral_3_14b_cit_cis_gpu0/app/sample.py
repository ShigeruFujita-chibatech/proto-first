import requests
import base64
import logging

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def ask_llama_cpp_with_nginx_auth(prompt: str) -> str:
    # Basic認証情報の設定
    username = ""
    password = ""
    credentials = f"{username}:{password}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()

    # リクエストヘッダ
    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/json"
    }

    # リクエストボディ（OpenAI Chat Completions 互換）
    payload = {
        "messages": [
            { "role" : "system",
              "content" : "You are new commer for meeting."
            },
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 2048,
        "stream": False
    }

    # エンドポイント
    url = "https://"

    try:
        # LLMの応答時間を考慮し timeout を 30秒 に推奨変更
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()  # HTTPエラー（4xx/5xx）を検知

        result = response.json()
        
        # ★ 修正点: OpenAI 互換フォーマットから回答テキストを取り出して返す
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

# 使用例
if __name__ == "__main__":
    response = ask_llama_cpp_with_nginx_auth("please describe your self")
    # ★ 修正点: 関数側で文字列を返しているため、そのまま print する
    print("Response:\n", response)
