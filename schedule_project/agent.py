import os
from dotenv import load_dotenv
from langchain_deepseek import ChatDeepSeek
from langchain.agents import create_agent

# 👈 从 tools.py 导入你的工具
from tools import get_current_time

load_dotenv(override=True)

# 初始化模型
model = ChatDeepSeek(
    model="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_BASE_URL"),
)

# 创建 Agent，把工具挂载上去
agent = create_agent(
    model=model,
    tools=[get_current_time], # 👈 把导进来的工具放这里
    system_prompt="你是一个时间管理助手。当用户询问今天、明天或具体日期时，请务必先调用 get_current_time 获取真实时间。"
)