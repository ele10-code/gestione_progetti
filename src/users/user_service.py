from ..database.database import SessionLocal, Base


# Dentro una funzione o un metodo dove necessiti di accedere al database
def get_user(user_id):
    db = SessionLocal()
    try:
        user = db.query(Utente).filter(Utente.id == user_id).first()
        return user
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        db.close()


