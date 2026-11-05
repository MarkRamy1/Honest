import os
import sys

# Define path for test SQLite database
TEST_DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "test_runner.db"))
TEST_DATABASE_URL = f"sqlite:///{TEST_DB_PATH}"

# Set test environment and database URL BEFORE any app imports
os.environ["APP_ENV"] = "testing"
os.environ["DATABASE_URL"] = TEST_DATABASE_URL
os.environ["SECRET_KEY"] = "test_secret_key_for_honest_ai_shopping_platform"

# Ensure app is discoverable by pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db.session import get_db
from app.db.seed import seed_database
from app.main import app

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except OSError:
            pass

    Base.metadata.create_all(bind=test_engine)
    with TestingSessionLocal() as db:
        seed_database(db)

    yield

    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except OSError:
            pass


@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
