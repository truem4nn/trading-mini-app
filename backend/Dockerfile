FROM python:3.11.0-slim

WORKDIR /app

# Salin requirements.txt dari subfolder backend
COPY backend/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Salin seluruh kode backend
COPY backend/ .

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]