from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from database.database import SessionLocal
from models.utente import Utente
from models.progetto import Progetto
from models.task import Task
from models.assegnazione import Assegnazione  # Importa correttamente il modello Assegnazione
from sqlalchemy.orm import joinedload
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

# Function to get the current database session
def get_db_session():
    db = SessionLocal()
    return db

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
        db_session = get_db_session()
        db_session.add(new_user)
        db_session.commit()
        login_user(new_user)  # Assicurati che l'utente sia persistito prima di fare login
        db_session.close()
        flash('Registration completed successfully!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    db_session = get_db_session()
    user_projects = db_session.query(Progetto).options(
        joinedload(Progetto.responsabile),
        joinedload(Progetto.tasks)  # Carica anche i task associati ai progetti
    ).filter_by(id_responsabile=current_user.id).all()
    user_tasks = db_session.query(Task).join(Assegnazione).filter(Assegnazione.id_utente == current_user.id).all()
    db_session.close()
    return render_template('dashboard.html', projects=user_projects, tasks=user_tasks)

@app.route('/add_project', methods=['POST'])
@login_required
def add_project():
    project_name = request.form.get('project_name')
    project_description = request.form.get('project_description')
    project_deadline = request.form.get('project_deadline')

    new_project = Progetto(
        nome_progetto=project_name,
        descrizione=project_description,
        scadenza=project_deadline,
        id_responsabile=current_user.id
    )
    
    db_session = get_db_session()
    db_session.add(new_project)
    db_session.commit()
    db_session.close()
    
    flash('Project added successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/add_task', methods=['POST'])
@login_required
def add_task():
    task_description = request.form.get('task_description')
    task_status = request.form.get('task_status')
    task_priority = request.form.get('task_priority')
    project_id = request.form.get('project_id')
    
    new_task = Task(
        descrizione=task_description,
        stato=task_status,
        priorita=task_priority,
        id_progetto=project_id
    )
    
    db_session = get_db_session()
    db_session.add(new_task)
    db_session.commit()
    db_session.close()
    
    flash('Task added successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/delete_project/<int:project_id>', methods=['POST'])
@login_required
def delete_project(project_id):
    db_session = get_db_session()
    project = db_session.query(Progetto).filter_by(id=project_id, id_responsabile=current_user.id).first()
    if project:
        db_session.delete(project)
        db_session.commit()
        flash('Project deleted successfully!', 'success')
    else:
        flash('Project not found or not authorized.', 'danger')
    db_session.close()
    return redirect(url_for('dashboard'))

@app.route('/delete_task/<int:task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
    db_session = get_db_session()
    task = db_session.query(Task).join(Assegnazione).filter(Task.id==task_id, Assegnazione.id_utente==current_user.id).first()
    if task:
        db_session.delete(task)
        db_session.commit()
        flash('Task deleted successfully!', 'success')
    else:
        flash('Task not found or not authorized.', 'danger')
    db_session.close()
    return redirect(url_for('dashboard'))

@login_manager.user_loader
def load_user(user_id):
    db_session = get_db_session()
    user = db_session.query(Utente).get(int(user_id))
    db_session.close()
    return user

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        db_session = get_db_session()
        user = db_session.query(Utente).filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            db_session.close()
            flash('Login successful!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        else:
            db_session.close()
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
