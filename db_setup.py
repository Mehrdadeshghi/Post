import sqlite3

def setup_db():
    conn = sqlite3.connect('sensors.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS movements (
                 id INTEGER PRIMARY KEY,
                 sensor TEXT,
                 timestamp TEXT)''')
    conn.commit()
    conn.close()

setup_db()
