from database.database import SessionLocal
from models.utente import Utente

def add_user(nome, email):
    db = SessionLocal()
    try:
        new_user = Utente(nome=nome, email=email)
        db.add(new_user)
        db.commit()
        print(f"Utente aggiunto: {new_user.id}, {new_user.nome}")
        return new_user
    except Exception as e:
        print(f"An error occurred: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == '__main__':
    # Aggiungi un utente al database
    add_user("Mario Rossi", "mario.rossi@example.com")
