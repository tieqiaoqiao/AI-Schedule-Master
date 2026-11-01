from datetime import datetime
from langchain_core.tools import tool

@tool
def get_current_time() -> str:
    """查询当前的系统时间和星期几。在回答任何关于“今天”、“明天”的问题前，请务必先调用此工具。"""
    now = datetime.now()
    weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    day_of_week = weekdays[now.weekday()]
    return f"现在是 {now.strftime('%Y年%m月%d日 %H:%M:%S')} {day_of_week}"