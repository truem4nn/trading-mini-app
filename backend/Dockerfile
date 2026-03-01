FROM python:3.11-slim-bookworm

WORKDIR /app


COPY backend/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt


COPY backend/ .

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]