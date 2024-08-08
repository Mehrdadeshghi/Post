from flask import Flask, request, render_template, redirect, url_for, flash, session, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import check_password_hash, generate_password_hash
import os
import datetime

app = Flask(__name__)

# Generieren Sie eine sichere secret_key
app.secret_key = os.urandom(24)  # Notwendig für Flash-Messages und Sessions

# Datenbankverbindung einrichten
def connect_db():
    return psycopg2.connect(
        dbname="post",
        user="myuser",
        password="mypassword",
        host="localhost"
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if not all([email, password]):
            flash('Bitte füllen Sie alle Felder aus.', 'danger')
            return render_template('login.html')

        try:
            conn = connect_db()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
            cursor.close()
            conn.close()

            if user and check_password_hash(user['password_hash'], password):
                session['user_id'] = user['user_id']
                session['username'] = user['username']
                flash('Erfolgreich eingeloggt!', 'success')
                return redirect(url_for('user_dashboard'))
            else:
                flash('Ungültige Anmeldedaten.', 'danger')
                return render_template('login.html')
        except Exception as e:
            print(f"Error: {e}")
            flash('Es gab ein Problem mit der Anmeldung. Bitte versuchen Sie es erneut.', 'danger')
            return render_template('login.html')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Erfolgreich ausgeloggt.', 'success')
    return redirect(url_for('login'))

@app.route('/user_dashboard')
def user_dashboard():
    if 'user_id' not in session:
        flash('Bitte melden Sie sich an, um fortzufahren.', 'danger')
        return redirect(url_for('login'))

    user_id = session['user_id']

    try:
        conn = connect_db()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT DISTINCT ps.sensor_id, ps.location
            FROM pir_sensors ps
            JOIN user_pir_assignments upa ON ps.sensor_id = upa.sensor_id
            WHERE upa.user_id = %s
        """, (user_id,))
        sensors = cursor.fetchall()

        cursor.execute("""
            SELECT ps.sensor_id, ps.location, sd.timestamp, sd.movement_detected
            FROM sensor_data sd
            JOIN pir_sensors ps ON sd.sensor_id = ps.sensor_id
            WHERE ps.sensor_id IN (
                SELECT sensor_id
                FROM user_pir_assignments
                WHERE user_id = %s
            )
            ORDER BY sd.timestamp DESC
            LIMIT 100
        """, (user_id,))
        movement_data = cursor.fetchall()
        
        cursor.close()
        conn.close()

        return render_template('user_dashboard.html', sensors=sensors, movement_data=movement_data)
    except Exception as e:
        print(f"Error: {e}")
        flash('Es gab ein Problem beim Abrufen der Sensordaten. Bitte versuchen Sie es erneut.', 'danger')
        return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
