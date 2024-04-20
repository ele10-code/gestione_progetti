# app.py
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from database.database import SessionLocal
from database import db_session 
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
        if not name or not email or not password:
            flash('Please fill in all fields', 'danger')
            return render_template('register.html')
        hashed_password = generate_password_hash(password)
        new_user = Utente(nome=name, email=email, password_hash=hashed_password)
        db_session.add(new_user)
        db_session.commit()
        login_user(new_user)  # Assicurati che l'utente sia persistito prima di fare login
        flash('Registration completed successfully!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    user_projects = db_session.query(Progetto).filter_by(id_responsabile=current_user.id).all()
    user_tasks = db_session.query(Task).filter_by(id_responsabile=current_user.id).all()
    return render_template('dashboard.html', projects=user_projects, tasks=user_tasks)

@login_manager.user_loader
def load_user(user_id):
    return db_session.query(Utente).get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = db_session.query(Utente).filter_by(email=email).first()
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