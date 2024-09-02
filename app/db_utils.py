import database
from security import get_password_hash
from models import User


def register(username: str, password: str):
    db = database.SessionLocal()
    hashed_password = get_password_hash(password)
    new_user = User(username=username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()

