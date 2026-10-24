import os
import json
from dotenv import load_dotenv
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from database import save_message, load_history
from agent import model

load_dotenv(override=True)

app = FastAPI()
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)


class FlexibleRequest(BaseModel):
    question: str
    all_files_content: str
    thread_id: str


async def generate_stream(prompt: str, thread_id: str, background_tasks: BackgroundTasks):
    full_response = ""

    # 流式生成
    async for chunk in model.astream(prompt):
        content = chunk.content if chunk.content else ""
        if content:
            full_response += content
            # 把文字包装成 JSON，避免换行符搞崩前端解析
            json_data = json.dumps({"text": content})
            yield f"data: {json_data}\n\n"

    # 使用 background_tasks 在后台存数据库，绝对不卡住流式输出
    background_tasks.add_task(save_message, thread_id, "assistant", full_response)


@app.post("/check_flexible")
async def check_flexible(req: FlexibleRequest, background_tasks: BackgroundTasks):
    prompt = f"""
    你是一个极其聪明的大学时间管理助手。用户上传了各种文件，里面包含了他的课表、各个部门的排班、志愿活动等乱七八糟的信息。
    以下是文件里的所有内容：
    {req.all_files_content}
    用户的问题是：
    {req.question}
    请仔细阅读文件内容，找出所有与用户问题相关的时间安排，判断是否有时间冲突。
    如果用户问的时间段有安排，请直接列出有哪些安排并警告冲突。如果没有安排，请回复空闲。
    """

    # 存用户消息也用后台任务
    background_tasks.add_task(save_message, req.thread_id, "user", req.question)

    return StreamingResponse(
        generate_stream(prompt, req.thread_id, background_tasks),
        media_type="text/event-stream"
    )


@app.get("/history/{thread_id}")
def get_history(thread_id: str):
    rows = load_history(thread_id)
    return {"thread_id": thread_id, "messages": rows}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)