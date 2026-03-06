FROM python:3.12-slim

WORKDIR /app
COPY pyproject.toml ./
RUN pip install --no-cache-dir .
COPY src/ ./src/
COPY config/ ./config/

EXPOSE 8080

CMD ["uvicorn", "mcp_lektor.server:mcp.app", "--host", "0.0.0.0", "--port", "8080"]
