from flask import Flask, request, render_template, redirect, url_for, flash
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import generate_password_hash

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004)
