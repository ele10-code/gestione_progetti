from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import mysql.connector
from mysql.connector import Error
from contextlib import contextmanager
from models.utente import Utente  # Importa il modello Utente
import datetime

app = Flask(__name__)
app.secret_key = 'a_very_secure_secret_key'

# Configurazione del database
db_config = {
    'user': 'admin',
    'password': 'admin_password',
    'host': 'localhost',
    'database': 'GestioneProgetti'
}

@contextmanager
def get_db_connection():
    conn = None
    try:
        conn = mysql.connector.connect(**db_config)
        yield conn
    except Error as e:
        print(f"Error: {e}")
        if conn:
            conn.close()
    finally:
        if conn and conn.is_connected():
            conn.close()

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
        with get_db_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    'INSERT INTO utenti (nome, email, password_hash) VALUES (%s, %s, %s)',
                    (name, email, hashed_password)
                )
                conn.commit()
                cursor.execute('SELECT * FROM utenti WHERE email = %s', (email,))
                user_data = cursor.fetchone()
                user = Utente(
                    id=user_data[0],
                    nome=user_data[1],
                    email=user_data[2],
                    password_hash=user_data[3],
                    _is_active=user_data[4]
                )
                login_user(user)
                flash('Registration completed successfully!', 'success')
                return redirect(url_for('dashboard'))
            except mysql.connector.Error as err:
                flash(f"Error: {err}", 'danger')
            finally:
                cursor.close()
    return render_template('register.html')

def project_to_dict(project):
    return {
        'id': project[0],
        'nome_progetto': project[1],
        'descrizione': project[2],
        'scadenza': project[3].strftime('%Y-%m-%d') if project[3] else None,
        'responsabile': {
            'id': project[4],
            'nome': project[5]
        } if project[4] else None,
        'tasks': []
    }

@app.route('/dashboard')
@login_required
def dashboard():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            '''
            SELECT p.id, p.nome_progetto, p.descrizione, p.scadenza, u.id, u.nome
            FROM progetti p
            LEFT JOIN utenti u ON p.id_responsabile = u.id
            WHERE p.id_responsabile = %s
            ''',
            (current_user.id,)
        )
        user_projects = cursor.fetchall()
        cursor.execute(
            '''
            SELECT t.id, t.descrizione, t.stato, t.priorita, t.scadenza
            FROM tasks t
            JOIN assegnazioni a ON t.id = a.id_task
            WHERE a.id_utente = %s
            ''',
            (current_user.id,)
        )
        user_tasks = cursor.fetchall()
        cursor.close()
    projects_dict = [project_to_dict(project) for project in user_projects]
    tasks_dict = [
        {
            'id': task[0],
            'descrizione': task[1],
            'stato': task[2],
            'priorita': task[3],
            'scadenza': task[4].strftime('%Y-%m-%d') if task[4] else None
        } for task in user_tasks
    ]
    return render_template('dashboard.html', projects=projects_dict, tasks=tasks_dict)

@app.route('/add_project', methods=['POST'])
# @login_required
def add_project():
    project_name = request.form.get('project_name')
    project_description = request.form.get('project_description')
    project_deadline = request.form.get('project_deadline')

    if not project_name:
        flash("Il nome del progetto deve esserci", 'danger')
        return redirect(url_for('dashboard'))
    
    if not project_description:
        flash("La descrizione del progetto deve esserci", 'danger')
        return redirect(url_for('dashboard'))
    
    if project_deadline:
        try:
            project_deadline = datetime.datetime.strptime(project_deadline, '%Y-%m-%d')
            if project_deadline <= datetime.datetime.now():
                flash("Scadenza progetto deve essere maggiore di oggi", 'danger')
                return redirect(url_for('dashboard'))
        except ValueError:
            flash("Formato data non valido. Utilizza YYYY-MM-DD", 'danger')
            return redirect(url_for('dashboard'))

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''
                INSERT INTO progetti (nome_progetto, descrizione, scadenza, id_responsabile)
                VALUES (%s, %s, %s, %s)
                ''',
                (project_name, project_description, project_deadline, current_user.id)
            )
            conn.commit()
            cursor.close()
    except Exception as e:
        flash(f"Si è verificato un errore durante l'aggiunta del progetto: {str(e)}", 'danger')
        return redirect(url_for('dashboard'))

    flash('Progetto aggiunto con successo!', 'success')
    return redirect(url_for('dashboard'))

def add_project(project_name, project_description, project_deadline):
    # Implementazione della funzione add_project
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            '''
            INSERT INTO progetti (nome_progetto, descrizione, scadenza)
            VALUES (%s, %s, %s)
            ''',
            (project_name, project_description, project_deadline)
        )
        conn.commit()
        cursor.close()

@app.route('/add_task', methods=['POST'])
@login_required
def add_task():
    task_description = request.form.get('task_description')
    task_status = request.form.get('task_status')
    task_priority = request.form.get('task_priority')
    task_deadline = request.form.get('task_deadline')
    project_id = request.form.get('project_id')

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            '''
            INSERT INTO tasks (descrizione, stato, priorita, scadenza, id_progetto)
            VALUES (%s, %s, %s, %s, %s)
            ''',
            (task_description, task_status, task_priority, task_deadline, project_id)
        )
        conn.commit()
        cursor.close()

    flash('Task added successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/delete_project/<int:project_id>', methods=['POST'])
@login_required
def delete_project(project_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'DELETE FROM progetti WHERE id = %s AND id_responsabile = %s',
            (project_id, current_user.id)
        )
        conn.commit()
        cursor.close()
    
    flash('Project deleted successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/delete_task/<int:task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id_progetto FROM tasks WHERE id = %s', (task_id,))
        task_project_id = cursor.fetchone()[0]
        if task_project_id:
            cursor.execute('SELECT id_responsabile FROM progetti WHERE id = %s', (task_project_id,))
            project_responsabile_id = cursor.fetchone()[0]
            if project_responsabile_id == current_user.id:
                cursor.execute('DELETE FROM tasks WHERE id = %s', (task_id,))
                conn.commit()
                flash('Task deleted successfully!', 'success')
            else:
                flash('User not authorized to delete this task.', 'danger')
        else:
            flash('Task not found.', 'danger')
        cursor.close()

    return redirect(url_for('dashboard'))

@app.route('/get_project_tasks/<int:project_id>', methods=['GET'])
@login_required
def get_project_tasks(project_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            '''
            SELECT t.id, t.descrizione, t.stato, t.priorita, t.scadenza
            FROM tasks t
            WHERE t.id_progetto = %s
            ''',
            (project_id,)
        )
        tasks = cursor.fetchall()
        cursor.close()
    tasks_dict = [
        {
            'id': task[0],
            'descrizione': task[1],
            'stato': task[2],
            'priorita': task[3],
            'scadenza': task[4].strftime('%Y-%m-%d') if task[4] else None
        } for task in tasks
    ]
    return {'tasks': tasks_dict}

@login_manager.user_loader
def load_user(user_id):
    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM utenti WHERE id = %s', (user_id,))
        user_data = cursor.fetchone()
        if user_data:
            user = Utente(
                id=user_data['id'],
                nome=user_data['nome'],
                email=user_data['email'],
                password_hash=user_data['password_hash'],
                _is_active=user_data['_is_active']
            )
            cursor.close()
            return user
        cursor.close()
    return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute('SELECT * FROM utenti WHERE email = %s', (email,))
            user_data = cursor.fetchone()
            if user_data and check_password_hash(user_data['password_hash'], password):
                user = Utente(
                    id=user_data['id'],
                    nome=user_data['nome'],
                    email=user_data['email'],
                    password_hash=user_data['password_hash'],
                    _is_active=user_data['_is_active']
                )
                login_user(user)
                flash('Login successful!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid email or password.', 'danger')
    return render_template('login.html')

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    flash('You have logged out.', 'success')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
