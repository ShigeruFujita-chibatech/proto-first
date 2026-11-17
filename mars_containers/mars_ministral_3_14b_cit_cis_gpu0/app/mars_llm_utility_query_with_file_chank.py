# mars_llm_utiliy_query_with_file_chank.py

import base64
import mimetypes
import os
import re
from dotenv import load_dotenv
import httpx

load_dotenv()
llm_username = os.getenv("LLM_USERNAME")
llm_password = os.getenv("LLM_PASSWORD")
llm_endpoint = str(os.getenv("LLM_ENDPOINT"))
llm_maxtokens = 2048


def main():
    prompt = "この文書での共和国の定義は？"
    role = "歴史の専門家"
    myfile = "kenseino_hongio_toite.txt"
    answer = query(llm_endpoint, role, prompt, myfile)
    print(answer)


def split_text(text: str, max_chars: int = 1500, overlap: int = 200) -> list[str]:
    """テキストを指定文字数ごとに分割（少し重複させてチャンク化）"""
    chunks = []
    start = 0
    while start < len(text):
        end = start + max_chars
        chunks.append(text[start:end])
        start += max_chars - overlap
    return chunks


def score_chunk(chunk: str, keywords: list[str]) -> int:
    """プロンプトに含まれるキーワードとの一致度をスコアリング"""
    score = 0
    for kw in keywords:
        score += chunk.count(kw)
    return score


def extract_relevant_context(
    file_path: str, prompt: str, max_total_chars: int = 15000
) -> str:
    """ファイルからプロンプトに関連する部分のみを優先抽出"""
    mime_type, _ = mimetypes.guess_type(file_path)

    # テキストファイル以外は従来通りの読み込み（必要に応じてBase64等）
    if mime_type and not mime_type.startswith("text/"):
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8") # 今後UTF-8でない場合の対処が必要

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        full_text = f.read()

    # print(full_text) # debug
    # exit() # debug

    # 全体文字数が小さければそのまま返す
    if len(full_text) <= max_total_chars:
        return full_text

    # プロンプトからキーワード抽出（2文字以上の単語）
    keywords = [kw for kw in re.findall(r"\w+", prompt) if len(kw) >= 2]
    # 特定キーワード補強（例: 「共和国」「定義」など）
    if "共和国" in prompt and "共和国" not in keywords:
        keywords.append("共和国")

    # 分割して類似度スコアを計算
    chunks = split_text(full_text, max_chars=1500, overlap=200)
    scored_chunks = [
        (score_chunk(chunk, keywords), i, chunk)
        for i, chunk in enumerate(chunks)
    ]

    # スコアが高い順（同じスコアなら出現順）にソート
    scored_chunks.sort(key=lambda x: (x[0], -x[1]), reverse=True)

    # 上限文字数に収まる分だけ選択
    selected_chunks = []
    current_chars = 0
    for score, idx, chunk in scored_chunks:
        if current_chars + len(chunk) > max_total_chars:
            break
        # 出現順を保持するためインデックスも記憶
        selected_chunks.append((idx, chunk))
        current_chars += len(chunk)

    # 元のテキスト順に並び替えて結合
    selected_chunks.sort(key=lambda x: x[0])
    combined_text = "\n\n...[省略]...\n\n".join(
        [chunk for _, chunk in selected_chunks]
    )

    return combined_text


def query(myURL: str, role: str, prompt: str, filename: str):
    credentials = f"{llm_username}:{llm_password}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()

    file_path = os.path.join(os.path.dirname(__file__), filename)

    if file_path and os.path.exists(file_path):
        # 関連度の高いテキストのみを安全なサイズで抽出
        file_content = extract_relevant_context(
            file_path, prompt, max_total_chars=15000
        )
        combined_prompt = f"{prompt}\n\n--- 添付ファイル抜粋: ({os.path.basename(file_path)})\n --- コンテンツ:\n{file_content}"
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
                myURL, headers=headers, json=payload, timeout=60
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
    except httpx.HTTPStatusError as e:
        return f"HTTP error {e.response.status_code}: {e.response.text}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"


if __name__ == "__main__":
    main()