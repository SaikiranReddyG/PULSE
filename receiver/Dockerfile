FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/receiver

ENV PYTHONPATH=/app

EXPOSE 8765

CMD ["sh", "-c", "uvicorn receiver.app:app --host ${CODEX_RECEIVER_BIND:-0.0.0.0} --port ${CODEX_RECEIVER_PORT:-8765}"]