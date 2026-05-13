FROM python:3.12-slim

WORKDIR /app

COPY workers/requirements.txt ./workers/requirements.txt
RUN pip install --no-cache-dir -r workers/requirements.txt

COPY workers /app/workers
COPY dashboard /app/dashboard

ENV PYTHONPATH=/app

CMD ["python", "-m", "workers.alert_worker"]
