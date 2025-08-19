FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
PYTHONUNBUFFERED=1

WORKDIR /app
# System deps (optional but useful for SSL/certs & runtime)
RUN apt-get update && apt-get install -y --no-install-recommends \
ca-certificates curl && \
rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY mcp_server.py ./
COPY text_analysis.py ./
# Default port
ENV FASTMCP_PORT=8080 FASTMCP_HOST=0.0.0.0 FASTMCP_APP_NAME=fastmcp-demo
# Run the HTTP transport
CMD ["python", "mcp_server.py"]