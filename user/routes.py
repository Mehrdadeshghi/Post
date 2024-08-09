from flask import render_template, session, redirect, url_for, flash
from . import user_bp
import psycopg2
from psycopg2.extras import RealDictCursor
import matplotlib.pyplot as plt
import io
import base64

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

        # Data for the graph
        timestamps = [data['timestamp'] for data in movement_data]
        movements = [data['movement_detected'] for data in movement_data]

        # Generate the graph
        plt.figure(figsize=(10, 5))
        plt.plot(timestamps, movements, marker='o')
        plt.title('Bewegungserkennung über Zeit')
        plt.xlabel('Zeit')
        plt.ylabel('Bewegung erkannt')
        plt.grid(True)

        # Save the plot to a PNG image in memory
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        graph_url = base64.b64encode(img.getvalue()).decode('utf8')
        plt.close()

        cursor.close()
        conn.close()

        return render_template('user/dashboard.html', movement_data=movement_data, graph_url=graph_url)
    except Exception as e:
        print(f"Error: {e}")
        flash('Es gab ein Problem beim Abrufen der Sensordaten. Bitte versuchen Sie es erneut.', 'danger')
        return redirect(url_for('auth.login'))
