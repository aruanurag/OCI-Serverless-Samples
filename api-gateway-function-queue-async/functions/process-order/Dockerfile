FROM python:3.9-slim
WORKDIR /app
COPY queue_poller.py .
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "queue_poller.py"]