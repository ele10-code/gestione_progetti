from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from database.database import SessionLocal
from models.utente import Utente

app = Flask(__name__)
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
        hashed_password = generate_password_hash(password)
        new_user = Utente(nome=nome, email=email, password_hash=hashed_password)
        db.add(new_user)
        db.commit()
        db.close()
        
        flash('Registrazione completata con successo!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

# Configurazione di Flask-Login
login_manager = LoginManager(app)
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

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Hai effettuato il logout.', 'success')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
