import pytest
from fastapi.testclient import TestClient

def test_register_user(client: TestClient):
    user_data = {
        "email": "test@example.com",
        "password": "testpassword123",
        "first_name": "Иван",
        "last_name": "Иванов",
        "middle_name": "Иванович",
        "birth_date": "2000-01-01",
        "phone": "+79998887766",
        "role": "Ученик"
    }
    
    response = client.post("/auth/register", json=user_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["first_name"] == user_data["first_name"]
    assert data["last_name"] == user_data["last_name"]
    assert "password" not in data

def test_register_duplicate_email(client: TestClient):
    user_data = {
        "email": "duplicate@example.com",
        "password": "testpassword123",
        "first_name": "Иван",
        "last_name": "Иванов",
        "middle_name": "Иванович",
        "birth_date": "2000-01-01",
        "phone": "+79998887766",
        "role": "Ученик"
    }
    
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 200
    
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 400
    assert "уже существует" in response.json()["detail"]

def test_login_success(client: TestClient):
    user_data = {
        "email": "login_test@example.com",
        "password": "testpassword123",
        "first_name": "Петр",
        "last_name": "Петров",
        "middle_name": "Петрович",
        "birth_date": "2000-01-01",
        "phone": "+79998887766",
        "role": "Ученик"
    }
    
    client.post("/auth/register", json=user_data)
    
    login_data = {
        "email": "login_test@example.com",
        "password": "testpassword123"
    }
    
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client: TestClient):
    user_data = {
        "email": "wrong_pass@example.com",
        "password": "correct123",
        "first_name": "Анна",
        "last_name": "Сидорова",
        "middle_name": "Петровна",
        "birth_date": "2000-01-01",
        "phone": "+79998887766",
        "role": "Ученик"
    }
    
    client.post("/auth/register", json=user_data)
    
    login_data = {
        "email": "wrong_pass@example.com",
        "password": "wrongpassword"
    }
    
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 401
    assert "Неверный логин или пароль" in response.json()["detail"]

def test_login_nonexistent_user(client: TestClient):
    login_data = {
        "email": "nonexistent@example.com",
        "password": "anypassword"
    }
    
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 401
    assert "Неверный логин или пароль" in response.json()["detail"]

def test_get_me_unauthorized(client: TestClient):
    response = client.get("/auth/me")
    assert response.status_code == 401

def test_get_me_authorized(auth_student, client: TestClient):
    headers = auth_student
    response = client.get("/auth/me", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "email" in data
    assert "first_name" in data
    assert "last_name" in data
    assert "role" in data
    assert "student_test@example.com" in data["email"]

def test_get_user_by_id(auth_tutor, client: TestClient):
    headers = auth_tutor
    
    response = client.get("/auth/me", headers=headers)
    user_id = response.json()["user_id"]
    
    response = client.get(f"/auth/{user_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == user_id
    assert data["email"] == "tutor_test@example.com"

def test_update_own_profile(auth_student, client: TestClient):
    headers = auth_student
    
    response = client.get("/auth/me", headers=headers)
    user_id = response.json()["user_id"]
    
    update_data = {
        "first_name": "ОбновленноеИмя",
        "last_name": "ОбновленнаяФамилия",
        "phone": "+79998887766"
    }
    
    response = client.put(f"/auth/{user_id}", json=update_data, headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["first_name"] == "ОбновленноеИмя"
    assert data["last_name"] == "ОбновленнаяФамилия"
    assert data["phone"] == "+79998887766"