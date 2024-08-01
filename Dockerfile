FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && \
    apt-get install -y sqlite3 && \
    pip install --no-cache-dir -r requirements.txt && \
    sqlite3 --version && \
    rm -rf /var/lib/apt/lists/*

COPY . .

RUN python /app/database_setup.py

CMD ["python", "bot.py"]
