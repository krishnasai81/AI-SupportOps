import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database.connection import Base, get_db


@pytest.fixture
def client():

    # Create a separate in-memory SQLite database
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine
    )

    # Create tables in the test database
    Base.metadata.create_all(bind=test_engine)

    # Override production database dependency
    def override_get_db():

        db = TestingSessionLocal()

        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    # No TestClient context manager here:
    # this avoids triggering the application's production
    # database startup hook during these tests.
    with TestClient(app) as test_client:
        yield test_client

    # Clean up
    app.dependency_overrides.clear()

    Base.metadata.drop_all(bind=test_engine)

    test_engine.dispose()