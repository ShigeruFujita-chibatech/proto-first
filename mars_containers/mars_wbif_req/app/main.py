# main.py on the mars_wbif
from typing import Optional
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()

# templatesディレクトリを指定
templates = Jinja2Templates(directory="templates")

# サンプル情報（データベース等から取得する想定）
SAMPLE_INFO = {
    "info_title": "案件 #1024: ネットワーク構成変更リクエスト",
    "info_content": "VLAN 238および239のタグ付け設定変更に関する承認依頼です。",
}

@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    """1) 情報を画面に表示するルーティング"""
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "info_title": SAMPLE_INFO["info_title"],
            "info_content": SAMPLE_INFO["info_content"],
            "message": None,
        },
    )


@app.post("/submit", response_class=HTMLResponse)
async def handle_submit(
    request: Request,
    action: str = Form(...),
    proposal_text: Optional[str] = Form(None),
):
    """3) フォーム送信を受け付ける処理"""
    result_message = ""

    if action == "accept":
        result_message = "「Accept（承認）」を受け付けました。"
    elif action == "reject":
        result_message = "「Reject（却下）」を受け付けました。"
    elif action == "propose":
        result_message = (
            f"「Propose（提案）」を受け付けました。提案内容: {proposal_text}"
        )
    elif action == "cancel":
        result_message = "「Cancel（キャンセル）」を受け付けました。"
    else:
        result_message = "不明な操作です。"

    # 処理結果を保持して画面を再描画
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "info_title": SAMPLE_INFO["info_title"],
            "info_content": SAMPLE_INFO["info_content"],
            "message": result_message,
        },
    )
