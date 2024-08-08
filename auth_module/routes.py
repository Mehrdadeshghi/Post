from flask import render_template, redirect, url_for, flash, session, request
from werkzeug.security import generate_password_hash, check_password_hash
from . import auth_bp
import psycopg2
from psycopg2.extras import RealDictCursor

def connect_db():
    return psycopg2.connect(
        dbname="post",
        user="myuser",
        password="mypassword",
        host="localhost"
    )

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if not all([email, password]):
            flash('Bitte füllen Sie alle Felder aus.', 'danger')
            return render_template('templates/auth/login.html')

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
                return redirect(url_for('user.user_dashboard'))
            else:
                flash('Ungültige Anmeldedaten.', 'danger')
                return render_template('templates/auth/login.html')
        except Exception as e:
            print(f"Error: {e}")
            flash('Es gab ein Problem mit der Anmeldung. Bitte versuchen Sie es erneut.', 'danger')
            return render_template('templates/auth/login.html')
    return render_template('templates/auth/login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Erfolgreich ausgeloggt.', 'success')
    return redirect(url_for('auth.login'))
