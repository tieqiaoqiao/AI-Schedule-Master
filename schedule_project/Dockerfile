# 基于 Python 3.10 官方精简版镜像
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 防止 Python 写出 .pyc 文件和缓冲标准输出（便于看日志）
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 先复制 requirements.txt 并安装依赖（利用 Docker 缓存机制）
COPY requirements.txt .
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# 复制项目所有代码到容器内
COPY . .

# 暴露 8000 端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]