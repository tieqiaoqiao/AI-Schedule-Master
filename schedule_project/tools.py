import os
import requests
from datetime import datetime
from langchain_core.tools import tool
from dotenv import load_dotenv

# 确保读取环境变量
load_dotenv(override=True)


# ==========================================
# 1. 查时间工具
# ==========================================
@tool
def get_current_time() -> str:
    """查询当前的系统时间和星期几。在回答任何关于“今天”、“明天”的问题前，请务必先调用此工具。"""
    now = datetime.now()
    weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    day_of_week = weekdays[now.weekday()]
    return f"现在是 {now.strftime('%Y年%m月%d日 %H:%M:%S')} {day_of_week}"


# ==========================================
# 2. 百度 OCR 工具
# ==========================================
def get_baidu_token():
    """获取百度 API 的 Access Token"""
    api_key = os.getenv("BAIDU_API_KEY")
    secret_key = os.getenv("BAIDU_SECRET_KEY")
    url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={api_key}&client_secret={secret_key}"
    response = requests.post(url)
    return response.json().get("access_token")


@tool
def ocr_image_text(image_url: str) -> str:
    """识别图片中的文字。参数 image_url 可以是图片的网络链接。"""
    token = get_baidu_token()
    if not token:
        return "获取百度 Token 失败，请检查 API Key。"

    url = f"https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic?access_token={token}"
    payload = f"url={image_url}"
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    try:
        response = requests.request("POST", url, headers=headers, data=payload)
        result = response.json()
        if "words_result" in result:
            texts = [item["words"] for item in result["words_result"]]
            return "\n".join(texts)
        else:
            return f"识别失败，错误信息：{result}"
    except Exception as e:
        return f"OCR 接口请求报错：{e}"