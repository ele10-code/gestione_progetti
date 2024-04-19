from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from database.database import SessionLocal
from models.utente import Utente
from models.progetto import Progetto
from models.task import Task

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


app = Flask(__name__)

# # Configurazione della connessione al database
# DATABASE_URL = "mysql+mysqlconnector://root:password@localhost/GestioneProgetti"
# app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL

# # Crea l'engine SQLAlchemy per la connessione al database
# engine = create_engine(DATABASE_URL)
# db = scoped_session(sessionmaker(bind=engine))

app.secret_key = 'una_chiave_segreta_molto_sicura'
# Inizializzazione del gestore di login per Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Imposta la vista che gestisce il login
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        password = request.form['password']

        db = SessionLocal()
        try:
            hashed_password = generate_password_hash(password)
            new_user = Utente(nome=nome, email=email, password_hash=hashed_password)
            db.add(new_user)
            db.commit()
            flash('Registrazione completata con successo!', 'success')
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
    # Supponendo che tu abbia una tabella Progetto e una tabella Task nel tuo database
    db = SessionLocal()
    # Esempio di come ottenere i progetti di un utente
    progetti_utente = db.query(Progetto).filter_by(utente_id=current_user.id).all()
    # Esempio di come ottenere i task di un utente
    task_utente = db.query(Task).filter_by(utente_id=current_user.id).all()
    # Altri dati che potresti voler passare
    # ...
    db.close()

    return render_template('dashboard.html', progetti=progetti_utente, task=task_utente)


# Configurazione di Flask-Login
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    db = SessionLocal()
    user = db.query(Utente).get(int(user_id))
    db.close()
    return user

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        db = SessionLocal()
        user = db.query(Utente).filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Login effettuato con successo!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Email o password non validi.', 'danger')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Hai effettuato il logout.', 'success')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
