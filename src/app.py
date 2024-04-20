# app.py
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from database.database import SessionLocal
from models.utente import Utente
from models.progetto import Progetto
from models.task import Task
import sys

# Stampa e imposta il limite di ricorsione per identificare problemi di ricorsione infinita
print(sys.getrecursionlimit())  # Print the current recursion limit
sys.setrecursionlimit(100)  # Set a lower limit to catch infinite recursion earlier


app = Flask(__name__)

app.secret_key = 'a_very_secure_secret_key'
# Initialize login manager for Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Set the view that handles login

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        # Imposta il valore di _is_active in base alla politica del tuo sito
        is_active = True  # o False, se richiedi la verifica dell'email

        if not name or not email or not password:
            flash('Please fill in all fields', 'danger')
            return render_template('register.html')

        db = SessionLocal()
        try:
            hashed_password = generate_password_hash(password)
            new_user = Utente(nome=name, email=email, password_hash=hashed_password, _is_active=is_active)
            db.add(new_user)
            db.commit()
            flash('Registration completed successfully!', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.rollback()
            flash(str(e), 'danger')
        finally:
            db.close()
    return render_template('register.html')



@app.route('/dashboard')
@login_required
def dashboard():
    # Assuming you have a Progetto table and a Task table in your database
    db = SessionLocal()
    # Example of how to obtain a user's projects
    user_projects = db.query(Progetto).filter_by(user_id=current_user.id).all()
    # Example of how to obtain a user's tasks
    user_tasks = db.query(Task).filter_by(user_id=current_user.id).all()
    
    db.close()

    return render_template('dashboard.html', projects=user_projects, tasks=user_tasks)

@login_manager.user_loader
def load_user(user_id):
    db = SessionLocal()
    try:
        user = db.query(Utente).get(int(user_id))
        return user
    finally:
        db.close()


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        db = SessionLocal()
        user = db.query(Utente).filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have logged out.', 'success')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
