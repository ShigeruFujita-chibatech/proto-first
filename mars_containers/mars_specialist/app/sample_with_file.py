# sample_with_file.py
import requests
import base64
import logging
import os
import mimetypes

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def encode_file_to_base64(file_path: str) -> tuple[str, str]:
    """ファイルを Base64 エンコードし、MIME タイプとともに返す"""
    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type:
        mime_type = "application/octet-stream"

    with open(file_path, "rb") as f:
        encoded_string = base64.b64encode(f.read()).decode("utf-8")
    
    return encoded_string, mime_type

def ask_llama_cpp_with_nginx_auth(prompt: str, file_path: str = None) -> str:
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

    # ユーザーコンテンツの構築
    user_content = []

    # ファイル指定がある場合処理を分岐
    if file_path and os.path.exists(file_path):
        encoded_data, mime_type = encode_file_to_base64(file_path)
        
        if mime_type.startswith("image/"):
            # 画像ファイルの場合（Visionモデル用）
            user_content = [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{mime_type};base64,{encoded_data}"
                    }
                }
            ]
        else:
            # テキスト等の場合（内容を直接プロンプトに結合）
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    file_text = f.read()
                combined_prompt = f"{prompt}\n\n--- 添付ファイル内容 ({os.path.basename(file_path)}) ---\n{file_text}"
                user_content = combined_prompt
            except Exception as e:
                logger.warning(f"テキストとして読み込めないため無視します: {e}")
                user_content = prompt
    else:
        user_content = prompt

    # リクエストボディ（OpenAI Chat Completions 互換）
    payload = {
        "messages": [
            {"role": "system", "content": "あなたは安全第一なエンジニアです"},
            {"role": "user", "content": user_content}
        ],
        "max_tokens": 2048,
        "stream": False
    }

    # エンドポイント
    url = "https://"

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()

        result = response.json()
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
    # フルパスでファイルを指定
    dir = "/home/shigeru/usr/repos/books/python/src/basic/llama/"
    file = "sample_calc.py"  # または .txt .png など
    file_full_path = os.path.join(dir,file)

    response = ask_llama_cpp_with_nginx_auth(
        prompt="このファイルについて説明してください。", 
        file_path=file_full_path
    )
    print("Response:\n", response)
