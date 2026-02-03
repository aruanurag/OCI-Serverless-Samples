# -----------------------------------------------------------------------------
# Copyright (c) 2025 Oracle and/or its affiliates.
#
# Licensed under the Universal Permissive License v 1.0 as shown at
# https://oss.oracle.com/licenses/upl

# DO NOT ALTER OR REMOVE COPYRIGHT NOTICES OR THIS HEADER.
# -----------------------------------------------------------------------------

FROM python:3.9-slim
WORKDIR /app
COPY queue_poller.py .
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "queue_poller.py"]