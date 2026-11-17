# mars_llm_utility_query_with_file.py
import base64
import mimetypes
import os
from dotenv import load_dotenv
import httpx

load_dotenv()
llm_username = os.getenv("LLM_USERNAME")
llm_password = os.getenv("LLM_PASSWORD")
llm_endpoint = str(os.getenv("LLM_ENDPOINT"))
llm_maxtokens = 512


def main():
    prompt = "この文書での共和国の定義は？"
    role = "歴史の専門家"
    myfile = "kenseino_hongio_toite.txt"
    answer = query(llm_endpoint, role, prompt, myfile)
    print(answer)


def read_file_content(file_path: str) -> tuple[str, str]:
    """ファイルタイプに応じてプレーンテキストまたはBase64で読み込む"""
    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type:
        mime_type = "application/octet-stream"

    # テキストファイルの場合はそのままテキストとして読み込む
    if mime_type.startswith("text/"):
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    else:
        # 画像等のバイナリファイルの場合のみ Base64 化
        with open(file_path, "rb") as f:
            content = base64.b64encode(f.read()).decode("utf-8")

    return content, mime_type


def query(myURL: str, role: str, prompt: str, filename: str):
    credentials = f"{llm_username}:{llm_password}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()

    file_path = os.path.join(os.path.dirname(__file__), filename)

    if file_path and os.path.exists(file_path):
        file_content, mime_type = read_file_content(file_path)
        combined_prompt = f"{prompt}\n\n--- 添付ファイル名: ({os.path.basename(file_path)})\n --- コンテンツ:\n{file_content}"
    else:
        print(f"{file_path}が読めませんでした")
        exit()

    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/json",
    }

    payload = {
        "messages": [
            {"role": "system", "content": role},
            {"role": "user", "content": combined_prompt},
        ],
        "max_tokens": llm_maxtokens,
        "stream": False,
    }

    try:
        with httpx.Client() as client:
            response = client.post(
                myURL, headers=headers, json=payload, timeout=30
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
    except httpx.HTTPStatusError as e:
        # HTTPエラー時のレスポンス詳細（サーバー側の詳細メッセージ）を表示
        return f"HTTP error {e.response.status_code}: {e.response.text}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"


if __name__ == "__main__":
    main()