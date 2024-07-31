import sqlite3

# Connect to SQLite database (this will create the database file if it doesn't exist)
conn = sqlite3.connect('sensors.db')

# Create a cursor object using the cursor() method
cursor = conn.cursor()

# Drop the movements table if it already exists
cursor.execute("DROP TABLE IF EXISTS movements")
cursor.execute("DROP TABLE IF EXISTS users")

# Create the movements table
cursor.execute('''
CREATE TABLE movements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sensor TEXT NOT NULL,
    timestamp DATETIME NOT NULL
)
''')

# Create the users table
cursor.execute('''
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
)
''')

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Database and tables created successfully.")
