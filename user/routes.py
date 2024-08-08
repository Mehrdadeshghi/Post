from flask import render_template, session, redirect, url_for, flash
from . import user_bp
import psycopg2
from psycopg2.extras import RealDictCursor

def connect_db():
    return psycopg2.connect(
        dbname="post",
        user="myuser",
        password="mypassword",
        host="localhost"
    )

@user_bp.route('/dashboard')
def user_dashboard():
    if 'user_id' not in session:
        flash('Bitte melden Sie sich an, um fortzufahren.', 'danger')
        return redirect(url_for('auth.login'))

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

        return render_template('user/dashboard.html', sensors=sensors, movement_data=movement_data)
    except Exception as e:
        print(f"Error: {e}")
        flash('Es gab ein Problem beim Abrufen der Sensordaten. Bitte versuchen Sie es erneut.', 'danger')
        return redirect(url_for('auth.login'))
