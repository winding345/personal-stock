FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# 依赖先装（利用层缓存）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 业务代码
COPY app ./app

# 数据目录（SQLite 持久化，容器内路径 /data）
RUN mkdir -p /data
ENV STOCK_DB_PATH=/data/stock.db

EXPOSE 8000

# 生产/普通：启动 FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
