# -----------------------------------------------------------------------------
# Copyright (c) 2025 Oracle and/or its affiliates.
#
# Licensed under the Universal Permissive License v 1.0 as shown at
# https://oss.oracle.com/licenses/upl

# DO NOT ALTER OR REMOVE COPYRIGHT NOTICES OR THIS HEADER.
# -----------------------------------------------------------------------------

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

COPY app.py ./
COPY tools/ ./tools/
# Default port
ENV FASTMCP_PORT=8080 FASTMCP_HOST=0.0.0.0 FASTMCP_APP_NAME=fastmcp-demo
# Run the HTTP transport
CMD ["python", "app.py"]