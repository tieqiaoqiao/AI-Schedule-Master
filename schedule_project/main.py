import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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


@app.post("/check_flexible")
def check_flexible(req: FlexibleRequest):
    prompt = f"""
    你是一个极其聪明的大学时间管理助手。用户上传了各种文件，里面包含了他的课表、各个部门的排班、志愿活动等乱七八糟的信息。
    以下是文件里的所有内容：
    {req.all_files_content}
    用户的问题是：
    {req.question}
    请仔细阅读文件内容，找出所有与用户问题相关的时间安排，判断是否有时间冲突。
    如果用户问的时间段有安排，请直接列出有哪些安排并警告冲突。如果没有安排，请回复空闲。
    """

    # 存入数据库
    save_message(req.thread_id, "user", req.question)

    # 调用大模型
    response = model.invoke(prompt).content

    # 存入数据库
    save_message(req.thread_id, "assistant", response)

    return {"result": response}


@app.get("/history/{thread_id}")
def get_history(thread_id: str):
    rows = load_history(thread_id)
    return {"thread_id": thread_id, "messages": rows}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)