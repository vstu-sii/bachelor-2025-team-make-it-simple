import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
import os

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        Base.metadata.create_all(bind=engine)
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c

@pytest.fixture
def test_tutor():
    return {
        "email": "tutor_test@example.com",
        "password": "testpassword123",
        "first_name": "Тест",
        "last_name": "Репетитор",
        "middle_name": "Тестович",
        "birth_date": "1990-01-01",
        "phone": "+79998887766",
        "role": "Репетитор"
    }

@pytest.fixture
def test_student():
    return {
        "email": "student_test@example.com",
        "password": "testpassword123",
        "first_name": "Тест",
        "last_name": "Ученик",
        "middle_name": "Тестович",
        "birth_date": "2000-01-01",
        "phone": "+79998887766",
        "role": "Ученик"
    }

@pytest.fixture
def auth_tutor(client, test_tutor):
    response = client.post("/auth/register", json=test_tutor)
    assert response.status_code == 200
    
    login_data = {
        "email": test_tutor["email"],
        "password": test_tutor["password"]
    }
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 200
    
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def auth_student(client, test_student):
    response = client.post("/auth/register", json=test_student)
    assert response.status_code == 200
    
    login_data = {
        "email": test_student["email"],
        "password": test_student["password"]
    }
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 200
    
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture(autouse=True)
def clean_db():
    yield
    for table in reversed(Base.metadata.sorted_tables):
        with engine.begin() as conn:
            conn.execute(table.delete())