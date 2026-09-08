# 生产部署镜像：OpenList Episode Rename (FastAPI Web 服务 + 前端静态资源)
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

ENV EPISODE_PATH=/data

COPY core.py server.py ./
COPY frontend ./frontend

VOLUME /data

EXPOSE 8000

CMD ["python", "server.py", "0.0.0.0", "8000"]