FROM python:3.11-slim

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /app
COPY load_dwh.py .

CMD ["python", "load_dwh.py"]
