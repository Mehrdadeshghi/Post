import psycopg2
from datetime import datetime

def connect_db():
    return psycopg2.connect(
        dbname="post",
        user="myuser",
        password="mypassword",
        host="localhost"
    )

def add_sensor(raspberry_id, location):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO pir_sensors (raspberry_id, location, created_at)
        VALUES (%s, %s, %s)
        RETURNING sensor_id;
    """, (raspberry_id, location, datetime.now()))
    sensor_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    return sensor_id

# Beispiel: Füge einen Sensor für einen bestimmten Raspberry Pi hinzu
raspberry_id = 1  # Beispiel Raspberry Pi ID
location = "Briefkasten Standort 1"
sensor_id = add_sensor(raspberry_id, location)
print(f"Sensor hinzugefügt mit ID: {sensor_id}")
