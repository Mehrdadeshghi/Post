from flask import Flask, request, render_template, redirect, url_for, flash, session
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import check_password_hash, generate_password_hash
import os

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
        cursor.close()
        conn.close()

        print("DEBUG: Sensors fetched from database:", sensors)  # Debugging-Ausgabe

        return render_template('user_dashboard.html', sensors=sensors)
    except Exception as e:
        print(f"Error: {e}")
        flash('Es gab ein Problem beim Abrufen der Sensordaten. Bitte versuchen Sie es erneut.', 'danger')
        return redirect(url_for('login'))


@app.route('/assign_user/<int:sensor_id>', methods=['GET', 'POST'])
def assign_user(sensor_id):
    if request.method == 'POST':
        user_id = request.form['user_id']
        raspberry_id = request.form['raspberry_id']
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO user_pir_assignments (user_id, sensor_id)
                VALUES (%s, %s)
            """, (user_id, sensor_id))
            conn.commit()
            cursor.close()
            conn.close()
            flash('Postfach zugewiesen', 'success')
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
