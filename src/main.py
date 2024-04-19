from users.user_service import get_user

def main():
    user_id = 1  # ID dell'utente che vuoi recuperare
    user = get_user(user_id)
    if user:
        print(f"Nome utente: {user.name}")
    else:
        print("Utente non trovato.")

if __name__ == "__main__":
    main()
