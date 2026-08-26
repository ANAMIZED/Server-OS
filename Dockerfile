# Glama inspects MCP over stdio. Do not start the HTTP control plane here.
# Admin generator: build ["pip install --no-cache-dir ."]
#                  CMD   ["python", "-m", "server_os.mcp.server"]
FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    SERVER_OS_DATA_DIR=/app/data \
    SERVER_OS_LLM_MODE=mock

COPY pyproject.toml README.md ./
COPY src ./src

RUN pip install --no-cache-dir . \
    && mkdir -p /app/data \
    && useradd --create-home --uid 10001 --shell /usr/sbin/nologin mcp \
    && chown -R mcp:mcp /app

USER mcp

CMD ["python", "-m", "server_os.mcp.server"]
