import os
from dotenv import load_dotenv
from langchain_deepseek import ChatDeepSeek
from langchain.agents import create_agent
# 导入你的两个工具
from tools import get_current_time, ocr_image_text

load_dotenv(override=True)

model = ChatDeepSeek(
    model="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_BASE_URL"),
)

# 创建 Agent，把工具挂载上去
agent = create_agent(
    model=model,
    tools=[get_current_time, ocr_image_text],
    system_prompt="你是一个时间管理助手。如果用户发了图片链接，请调用 ocr_image_text 识别文字；如果问时间，调用 get_current_time。"
)