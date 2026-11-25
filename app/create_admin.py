"""Create the first administrator interactively: python -m app.create_admin."""
from getpass import getpass

from app.database.connection import Base, SessionLocal, engine
from app.database.models import User
from app.security import hash_password


def main():
    Base.metadata.create_all(bind=engine)
    email = input("Administrator email: ").strip().lower()
    password = getpass("Password (minimum 10 characters): ")
    confirm = getpass("Confirm password: ")
    if len(password) < 10 or password != confirm:
        raise SystemExit("Passwords must match and contain at least 10 characters.")
    db = SessionLocal()
    try:
        if db.query(User).filter(User.email == email).first():
            raise SystemExit("That user already exists. Do not overwrite an existing role.")
        db.add(User(email=email, password_hash=hash_password(password), role="admin", is_active=True))
        db.commit()
        print(f"Created administrator account for {email}.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
