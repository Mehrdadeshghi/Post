from flask import request, jsonify, render_template, redirect, url_for, flash
from . import management_bp
import psycopg2
from psycopg2.extras import RealDictCursor

def connect_db():
    return psycopg2.connect(
        dbname="post",
        user="myuser",
        password="mypassword",
        host="localhost"
    )

@management_bp.route('/register', methods=['POST'])
def register_raspberry_pi():
    data = request.json
    serial_number = data.get('serial_number')
    model = data.get('model')
    os_version = data.get('os_version')
    firmware_version = data.get('firmware_version')
    ip_address = data.get('ip_address')
    
    if not serial_number:
        return jsonify({"error": "Serial number is required"}), 400

    try:
        conn = connect_db()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Prüfen, ob der Raspberry Pi bereits registriert ist
        cursor.execute("SELECT * FROM raspberry_pis WHERE serial_number = %s", (serial_number,))
        raspberry_pi = cursor.fetchone()

        if raspberry_pi:
            cursor.close()
            conn.close()
            return jsonify({"raspberry_id": raspberry_pi['raspberry_id']}), 200
        
        # Neuen Raspberry Pi registrieren
        cursor.execute("""
            INSERT INTO raspberry_pis (serial_number, model, os_version, firmware_version, ip_address)
            VALUES (%s, %s, %s, %s, %s) RETURNING raspberry_id
        """, (serial_number, model, os_version, firmware_version, ip_address))
        raspberry_id = cursor.fetchone()['raspberry_id']
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"raspberry_id": raspberry_id}), 201
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

@management_bp.route('/get_raspberry_id', methods=['GET'])
def get_raspberry_id():
    serial_number = request.args.get('serial_number')
    
    if not serial_number:
        return jsonify({"error": "Serial number is required"}), 400

    try:
        conn = connect_db()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("SELECT raspberry_id FROM raspberry_pis WHERE serial_number = %s", (serial_number,))
        raspberry_pi = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if raspberry_pi:
            return jsonify({"raspberry_id": raspberry_pi['raspberry_id']}), 200
        else:
            return jsonify({"error": "Serial number not found"}), 404
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

@management_bp.route('/add_sensor', methods=['POST'])
def add_sensor():
    data = request.json
    raspberry_id = data.get('raspberry_id')
    location = data.get('location')

    if not raspberry_id or not location:
        return jsonify({"error": "Raspberry ID and location are required"}), 400

    try:
        conn = connect_db()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            INSERT INTO pir_sensors (raspberry_id, location)
            VALUES (%s, %s) RETURNING sensor_id
        """, (raspberry_id, location))
        sensor_id = cursor.fetchone()['sensor_id']

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"sensor_id": sensor_id}), 201
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

@management_bp.route('/check_sensor', methods=['GET'])
def check_sensor():
    raspberry_id = request.args.get('raspberry_id')
    location = request.args.get('location')

    if not raspberry_id or not location:
        return jsonify({"error": "Raspberry ID and location are required"}), 400

    try:
        conn = connect_db()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT sensor_id FROM pir_sensors WHERE raspberry_id = %s AND location = %s
        """, (raspberry_id, location))
        sensor = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if sensor:
            return jsonify({"sensor_id": sensor['sensor_id']}), 200
        else:
            return jsonify({"error": "Sensor not found"}), 404
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

@management_bp.route('/pir_data', methods=['POST'])
def receive_pir_data():
    data = request.json
    sensor_id = data.get('sensor_id')
    movement_detected = data.get('movement_detected')

    if not sensor_id or movement_detected is None:
        return jsonify({"error": "Sensor ID and movement detected status are required"}), 400

    try:
        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO sensor_data (sensor_id, movement_detected)
            VALUES (%s, %s)
        """, (sensor_id, movement_detected))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Data received successfully"}), 201
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

@management_bp.route('/raspberrys')
def raspberry_list():
    try:
        conn = connect_db()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT rp.*, loc.street, loc.house_number, loc.postal_code, loc.city, loc.state, loc.country
            FROM raspberry_pis rp
            LEFT JOIN locations loc ON rp.location_id = loc.location_id
        """)
        raspberrys = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('management/raspberry_list.html', raspberrys=raspberrys)
    except Exception as e:
        print(f"Error: {e}")
        flash('Es gab ein Problem beim Abrufen der Raspberry Pis. Bitte versuchen Sie es erneut.', 'danger')
        return redirect(url_for('auth.login'))

@management_bp.route('/raspberry/<int:raspberry_id>/pirs')
def view_pirs(raspberry_id):
    try:
        conn = connect_db()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT * FROM pir_sensors WHERE raspberry_id = %s
        """, (raspberry_id,))
        pirs = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('management/pir_list.html', pirs=pirs, raspberry_id=raspberry_id)
    except Exception as e:
        print(f"Error: {e}")
        flash('Es gab ein Problem beim Abrufen der PIR-Sensoren. Bitte versuchen Sie es erneut.', 'danger')
        return redirect(url_for('management.raspberry_list'))

@management_bp.route('/raspberry/<int:raspberry_id>/assign_location', methods=['GET', 'POST'])
def assign_location(raspberry_id):
    if request.method == 'POST':
        street = request.form['street']
        house_number = request.form['house_number']
        postal_code = request.form['postal_code']
        city = request.form['city']
        state = request.form['state']
        country = request.form['country']

        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO locations (street, house_number, postal_code, city, state, country)
                VALUES (%s, %s, %s, %s, %s, %s) RETURNING location_id
            """, (street, house_number, postal_code, city, state, country))
            location_id = cursor.fetchone()[0]
            cursor.execute("""
                UPDATE raspberry_pis SET location_id = %s WHERE raspberry_id = %s
            """, (location_id, raspberry_id))
            conn.commit()
            cursor.close()
            conn.close()
            flash('Standort erfolgreich zugewiesen.', 'success')
            return redirect(url_for('management.raspberry_list'))
        except Exception as e:
            print(f"Error: {e}")
            flash('Es gab ein Problem beim Zuweisen des Standorts. Bitte versuchen Sie es erneut.', 'danger')
            return redirect(url_for('management.assign_location', raspberry_id=raspberry_id))
    
    return render_template('management/assign_location.html', raspberry_id=raspberry_id)

@management_bp.route('/pir/<int:sensor_id>/assign_user', methods=['GET', 'POST'])
def assign_user(sensor_id):
    if request.method == 'POST':
        user_id = request.form['user_id']
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE pir_sensors SET user_id = %s WHERE sensor_id = %s
            """, (user_id, sensor_id))
            conn.commit()
            cursor.close()
            conn.close()
            flash('Postfach zugewiesen.', 'success')
            return redirect(url_for('management.raspberry_list'))
        except Exception as e:
            print(f"Error: {e}")
            flash('Es gab ein Problem beim Zuweisen des Postfachs. Bitte versuchen Sie es erneut.', 'danger')
            return redirect(url_for('management.assign_user', sensor_id=sensor_id))
    
    try:
        conn = connect_db()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT user_id, username FROM users")
        users = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('management/assign_user.html', sensor_id=sensor_id, users=users)
    except Exception as e:
        print(f"Error: {e}")
        flash('Es gab ein Problem beim Abrufen der Benutzer. Bitte versuchen Sie es erneut.', 'danger')
        return redirect(url_for('management.raspberry_list'))

@management_bp.route('/overview')
def management_overview():
    try:
        conn = connect_db()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Get Raspberry Pis data
        cursor.execute("SELECT * FROM raspberry_pis")
        raspberrys = cursor.fetchall()

        # Get Sensors data
        cursor.execute("SELECT * FROM pir_sensors")
        sensors = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template('management/management_overview.html', raspberrys=raspberrys, sensors=sensors)
    except Exception as e:
        print(f"Error: {e}")
        flash('Es gab ein Problem beim Abrufen der Übersichtsdaten. Bitte versuchen Sie es erneut.', 'danger')
        return redirect(url_for('management.raspberry_list'))
