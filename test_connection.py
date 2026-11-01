
from sqlalchemy import text
from app.database.connection import engine


def test_connection():
    try:
        with engine.connect() as connection:
            result = connection.execute(
                text("SELECT current_database(), version()")
            )

            row = result.fetchone()

            print("Database:", row[0])
            print("PostgreSQL connection successful!")

    except Exception as error:
        print("Database connection failed!")
        print(type(error).__name__)
        print(error)


if __name__ == "__main__":
    test_connection()
