import sqlite3

print("Connecting to database...")
# Créez une connexion à la base de données
conn = sqlite3.connect('clients.db')
c = conn.cursor()


print("Creating table if not exists...")
c.execute('''
          CREATE TABLE IF NOT EXISTS clients
          (id INTEGER PRIMARY KEY,
          name TEXT,
          company TEXT,
          email TEXT,
          phone TEXT,
          project_name TEXT,
          project_description TEXT,
          key TEXT,
          visio_date TEXT)
          ''')

print("Creating articles table if not exists...")
c.execute('''
          CREATE TABLE IF NOT EXISTS articles
          (id INTEGER PRIMARY KEY,
          title TEXT,
          url TEXT UNIQUE,
          summary TEXT)
          ''')

conn.commit()
print("Database setup completed successfully.")
conn.close()
