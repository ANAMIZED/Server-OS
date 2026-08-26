FROM python:3.12-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 SERVER_OS_LLM_MODE=mock SERVER_OS_DATA_DIR=/app/data
COPY pyproject.toml README.md ./
COPY src ./src
COPY scripts ./scripts
RUN pip install --no-cache-dir . \
    && mkdir -p /app/data \
    && useradd --create-home --uid 10001 --shell /usr/sbin/nologin mcp \
    && chown -R mcp:mcp /app
USER mcp
CMD ["python", "-m", "server_os.mcp"]
