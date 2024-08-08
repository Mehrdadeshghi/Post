from flask import Flask, request, render_template, redirect, url_for, flash
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import generate_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Notwendig für Flash-Messages

# Datenbankverbindung einrichten
def connect_db():
    return psycopg2.connect(
        dbname="post",
        user="myuser",
        password="mypassword",
        host="localhost"
    )

# Benutzerregistrierung
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        password_hash = generate_password_hash(password)

        if not all([username, email, password]):
            flash('Bitte füllen Sie alle Felder aus.', 'danger')
            return render_template('register.html')

        try:
            conn = connect_db()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("""
                INSERT INTO users (username, email, password_hash)
                VALUES (%s, %s, %s)
                RETURNING user_id, username, email, created_at
            """, (username, email, password_hash))
            
            user = cursor.fetchone()
            conn.commit()
            cursor.close()
            conn.close()

            flash('Registrierung erfolgreich. Sie können sich jetzt anmelden.', 'success')
            return redirect(url_for('register'))
        except Exception as e:
            print(f"Error: {e}")
            flash('Es gab ein Problem mit der Registrierung. Bitte versuchen Sie es erneut.', 'danger')
            return render_template('register.html')
    return render_template('register.html')

# API-Endpunkt zum Abrufen aller Raspberry Pis
@app.route('/raspberrys', methods=['GET'])
def view_raspberrys():
    try:
        conn = connect_db()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT rp.raspberry_id, rp.serial_number, rp.model, rp.os_version, rp.firmware_version, rp.ip_address, rp.created_at, l.street, l.house_number, l.postal_code, l.city, l.state, l.country
            FROM raspberry_pis rp
            LEFT JOIN locations l ON rp.location_id = l.location_id
        """)
        raspberrys = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('raspberrys.html', raspberrys=raspberrys)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

# API-Endpunkt zum Abrufen der PIR-Sensoren eines Raspberry Pi
@app.route('/raspberry/<int:raspberry_id>/pirs', methods=['GET'])
def view_pirs(raspberry_id):
    try:
        conn = connect_db()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT ps.sensor_id, ps.location
            FROM pir_sensors ps
            WHERE ps.raspberry_id = %s
        """, (raspberry_id,))
        pirs = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('pirs.html', raspberry_id=raspberry_id, pirs=pirs)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

# API-Endpunkt zum Zuweisen eines Benutzers zu einem PIR-Sensor
@app.route('/assign_user/<int:sensor_id>', methods=['GET', 'POST'])
def assign_user(sensor_id):
    if request.method == 'POST':
        user_id = request.form['user_id']
        raspberry_id = request.form['raspberry_id']
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE pir_sensors
                SET user_id = %s
                WHERE sensor_id = %s
            """, (user_id, sensor_id))
            conn.commit()
            cursor.close()
            conn.close()
            flash('User assigned successfully', 'success')
            return redirect(url_for('view_pirs', raspberry_id=raspberry_id))
        except Exception as e:
            print(f"Error: {e}")
            flash('Failed to assign user', 'danger')
            return redirect(url_for('assign_user', sensor_id=sensor_id, raspberry_id=raspberry_id))
    try:
        conn = connect_db()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT user_id, username FROM users")
        users = cursor.fetchall()
        cursor.close()
        conn.close()
        raspberry_id = request.args.get('raspberry_id')
        return render_template('assign_user.html', sensor_id=sensor_id, users=users, raspberry_id=raspberry_id)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
