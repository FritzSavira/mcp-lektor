FROM python:3.12-slim

WORKDIR /app

# 1. Wir kopieren das pyproject.toml
COPY pyproject.toml ./

# 2. Wir kopieren den Quellcode und die Config
COPY src/ ./src/
COPY config/ ./config/

# 3. Wir installieren alles
RUN pip install --no-cache-dir .

EXPOSE 8080 8501

# Korrektur: Wir verweisen direkt auf 'mcp', da FastMCP selbst die ASGI-App ist
CMD ["uvicorn", "mcp_lektor.server:mcp", "--host", "0.0.0.0", "--port", "8080"]
