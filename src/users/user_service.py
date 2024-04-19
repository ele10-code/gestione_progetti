from database.database import SessionLocal  # Assumi che questo percorso sia corretto
from models.utente import Utente  # Assumi che il modello sia definito in models/utente.py

def get_user(user_id):
    db = SessionLocal()  # Crea una sessione del database
    try:
        user = db.query(Utente).filter(Utente.id == user_id).first()
        return user
    except Exception as e:
        print(f"An error occurred: {e}")  # Stampa l'errore se qualcosa va storto
    finally:
        db.close()  # Assicurati che la sessione venga chiusa indipendentemente dal risultato



from models.utente import Utente

def add_user(nome, email):
    # Crea una sessione del database
    db = SessionLocal()
    try:
        # Crea un nuovo utente
        new_user = Utente(nome=nome, email=email)
        db.add(new_user)  # Aggiunge il nuovo utente alla sessione
        db.commit()  # Esegue il commit delle modifiche
        print(f"Utente aggiunto: {new_user.id}, {new_user.nome}")
        return new_user
    except Exception as e:
        print(f"An error occurred: {e}")
        db.rollback()  # Annulla tutte le modifiche se ci sono stati problemi
    finally:
        db.close()  # Chiude la sessione del database

# Esempio di utilizzo della funzione
add_user("Mario Rossi", "mario.rossi@example.com")