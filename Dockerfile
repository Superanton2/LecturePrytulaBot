FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY Vianor_telegram_bot .

CMD ["python", "main.py"]