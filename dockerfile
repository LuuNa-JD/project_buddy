FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y sqlite3
RUN sqlite3 --version
COPY . .

RUN python /app/database_setup.py

RUN ls /app

CMD ["python", "bot.py"]
