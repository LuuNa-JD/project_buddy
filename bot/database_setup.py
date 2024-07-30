import sqlite3

# Créez une connexion à la base de données
conn = sqlite3.connect('clients.db')
c = conn.cursor()

# Créez la table pour stocker les informations des clients
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

conn.commit()
conn.close()
