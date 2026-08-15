FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt pyproject.toml README.md ./
COPY src ./src

RUN pip install --no-cache-dir -e .

RUN mkdir -p /app/data

ENV SERVER_OS_DATA_DIR=/app/data
ENV SERVER_OS_LLM_MODE=mock
ENV PYTHONUNBUFFERED=1

EXPOSE 8080

CMD ["python", "-c", "from server_os.main import run; run()"]
