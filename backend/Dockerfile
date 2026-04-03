FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# .env 제외하고 필요한 소스 파일만 복사
COPY main.py agent.py tools.py vector_store.py data_pipeline.py ./

# 환경 변수 기본값 설정
ENV ENVIRONMENT=local-docker
ENV PORT=8000

CMD uvicorn main:app --host 0.0.0.0 --port ${PORT}
