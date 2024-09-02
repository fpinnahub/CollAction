import database
from security import get_password_hash
from models import User, Witness, Collation


def delete_user(username: str):
    db = database.SessionLocal()

    # Trova l'utente nel database
    user = db.query(User).filter(User.username == username).first()

    if not user:
        raise Exception("Utente non trovato!")

    # Cancella tutti i testimoni associati all'utente
    db.query(Witness).filter(Witness.owner_id == user.id).delete()

    # Cancella tutte le collazioni associate all'utente
    db.query(Collation).filter(Collation.owner_id == user.id).delete()

    # Cancella l'utente stesso
    db.delete(user)

    # Conferma le modifiche
    db.commit()


def register(username: str, password: str):
    db = database.SessionLocal()
    hashed_password = get_password_hash(password)
    new_user = User(username=username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
