FROM python:3.10-slim

RUN apt-get update && apt-get install -y sqlite3 libsqlite3-dev

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python3 /app/database_setup.py

CMD ["python3", "bot.py"]
