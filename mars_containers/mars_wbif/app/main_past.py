# main.py on the mars_wbif
from typing import Optional
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()

# templates-directory for HTMLs files templates directory
templates = Jinja2Templates(directory="templates")

# 
SAMPLE_INFO = {
    "info_title": "Sample Title",
    "info_content": "Sample Content",
}

@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    """1) Show information"""
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
    """3) FORM processed"""
    result_message = "Here is your message"

    if action == "accept":
        result_message = "Get Accept"
    elif action == "reject":
        result_message = "Get Reject"
    elif action == "propose":
        result_message = (
            f"Get Propose: content: {proposal_text}"
        )
    elif action == "cancel":
        result_message = "Cancel-ed"
    else:
        result_message = "Unknown Selector"

    # Keep result and show again
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "llm_title": LLM_INFO["2nd LLM Topics"],
            "llm_content": LLM_INFO["2nd LLM Topics"],
            "message": result_message,
        },
    )
