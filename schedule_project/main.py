import os
import json
from dotenv import load_dotenv
from dotenv import load_dotenv
from fastapi import FastAPI, BackgroundTasks, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from langchain_core.messages import HumanMessage

# 导入你的数据库操作和模型
from database import init_db, save_message, load_history, create_user, get_user
from agent import agent


# 导入 JWT 鉴权相关的全部功能
from auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user_id
)

load_dotenv(override=True)

app = FastAPI()
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()
    print("✅ 数据库表检查/创建完毕！")


# ==========================================
# 1. 请求体模型
# ==========================================
class FlexibleRequest(BaseModel):
    question: str
    all_files_content: str = ""  # 允许不传文本
    image_url: str = ""  # 新增：允许传图片链接
    thread_id: str


class AuthRequest(BaseModel):
    username: str
    password: str


# ==========================================
# 2. 注册与登录
# ==========================================
@app.post("/register")
def register(req: AuthRequest):
    hashed_pwd = hash_password(req.password)
    ok = create_user(req.username, hashed_pwd)
    if ok:
        return {"msg": "注册成功"}
    return {"msg": "用户名已存在"}


@app.post("/login")
def login(req: AuthRequest):
    user = get_user(req.username)
    if user is None:
        return {"msg": "密码或用户名错误"}
    if verify_password(req.password, user["password"]):
        token = create_access_token(user_id=user["id"])
        return {"msg": "登录成功", "token": token}
    return {"msg": "密码或用户名错误"}


# ==========================================
# 3. 流式生成器（完美版）
# ==========================================
async def generate_stream(prompt: str, thread_id: str, background_tasks: BackgroundTasks):
    full_response = ""
    inputs = {"messages": [HumanMessage(content=prompt)]}

    try:
        async for msg, metadata in agent.astream(inputs, stream_mode="messages"):
            if msg.content and metadata.get("langgraph_node") in ["agent", "model"]:
                content = msg.content
                full_response += content
                json_data = json.dumps({"text": content})
                yield f"data: {json_data}\n\n"
    except Exception as e:
        print(f"❌ 流式输出崩溃: {e}")
        yield f"data: {json.dumps({'text': f'[系统错误] {e}'})}\n\n"

    background_tasks.add_task(save_message, thread_id, "assistant", full_response)


# ==========================================
# 4. 受保护的日程接口（支持文本+图片双模态）
# ==========================================
@app.post("/check_flexible")
async def check_flexible(
        req: FlexibleRequest,
        background_tasks: BackgroundTasks,
        user_id: str = Depends(get_current_user_id)
):
    # 1. 构建基础的 Prompt
    prompt = f"""
    你是一个极其聪明的大学时间管理助手。
    用户的问题是：{req.question}
    """

    # 2. 如果前端传了文本，就把文本加进去
    if req.all_files_content:
        prompt += f"\n以下是用户上传的文本课表内容：\n{req.all_files_content}"

    # 3. 如果前端传了图片链接，就强制它去调工具
    if req.image_url:
        prompt += f"\n用户还提供了一张图片链接：{req.image_url}。请立刻调用 ocr_image_text 工具提取图片中的课表文字，然后再判断冲突。"

    # 4. 加上时间工具的强制指令
    prompt += "\n【极其重要】：如果用户问题中提到了“今天”、“明天”等相对时间，你必须先调用 get_current_time 工具获取真实的当前时间！"

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