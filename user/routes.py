from flask_socketio import SocketIO, emit
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import io
import base64

socketio = SocketIO(app)

@user_bp.route('/dashboard')
def user_dashboard():
    if 'user_id' not in session:
        flash('Bitte melden Sie sich an, um fortzufahren.', 'danger')
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    username = session.get('username', 'Nutzer')
    
    try:
        conn = connect_db()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Fetch the user's location (replace with actual query if location is stored)
        location = "Unknown"  # Placeholder, replace with actual data fetching logic

        # Fetch last 10 movements
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
            LIMIT 10
        """, (user_id,))
        last_movements = cursor.fetchall()

        # Fetch movement count in the last 30 days
        cursor.execute("""
            SELECT COUNT(*) as movement_count
            FROM sensor_data sd
            JOIN pir_sensors ps ON sd.sensor_id = ps.sensor_id
            WHERE ps.sensor_id IN (
                SELECT sensor_id
                FROM user_pir_assignments
                WHERE user_id = %s
            )
            AND sd.timestamp > %s
        """, (user_id, datetime.now() - timedelta(days=30)))
        movement_count_30_days = cursor.fetchone()['movement_count']

        cursor.close()
        conn.close()

        return render_template('user/dashboard.html', username=username, location=location, 
                               last_movements=last_movements, movement_count_30_days=movement_count_30_days)
    except Exception as e:
        print(f"Error: {e}")
        flash('Es gab ein Problem beim Abrufen der Sensordaten. Bitte versuchen Sie es erneut.', 'danger')
        return redirect(url_for('auth.login'))

@socketio.on('request_data')
def handle_request_data():
    # Fetch the latest data from the database and send it to the client
    conn = connect_db()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("""
        SELECT ps.sensor_id, sd.timestamp, sd.movement_detected
        FROM sensor_data sd
        JOIN pir_sensors ps ON sd.sensor_id = ps.sensor_id
        WHERE ps.sensor_id IN (
            SELECT sensor_id
            FROM user_pir_assignments
            WHERE user_id = %s
        )
        ORDER BY sd.timestamp DESC
        LIMIT 1
    """, (session['user_id'],))
    latest_data = cursor.fetchone()
    cursor.close()
    conn.close()
    emit('update_graph', latest_data)
