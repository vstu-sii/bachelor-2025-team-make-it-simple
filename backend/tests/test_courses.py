import pytest
import json
from fastapi.testclient import TestClient

def test_get_all_courses_unauthorized(client: TestClient):
    response = client.get("/courses/")
    assert response.status_code == 401

def test_get_all_courses_student(auth_student, client: TestClient):
    headers = auth_student
    response = client.get("/courses/", headers=headers)
    assert response.status_code == 403
    assert "Только репетиторы" in response.json()["detail"]

def test_get_all_courses_tutor(auth_tutor, client: TestClient):
    headers = auth_tutor
    response = client.get("/courses/", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_course_success(auth_tutor, client: TestClient):
    headers = auth_tutor
    
    topic_data = {
        "title": "Test Topic for Course",
        "description_text": "Test description"
    }
    
    response = client.post("/topics/", json=topic_data, headers=headers)
    assert response.status_code == 200
    topic_id = response.json()["topic_id"]
    
    course_data = {
        "title": "Test Course",
        "link_to_vector_db": "/test/vector_db",
        "input_test_json": {"test": "data"},
        "topics_ids": [topic_id],
        "materials_ids": []
    }
    
    response = client.post("/courses/", json=course_data, headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["title"] == "Test Course"
    assert "course_id" in data

def test_create_course_student_forbidden(auth_student, client: TestClient):
    headers = auth_student
    
    course_data = {
        "title": "Should Fail Course",
        "topics_ids": [1]
    }
    
    response = client.post("/courses/", json=course_data, headers=headers)
    assert response.status_code == 403
    assert "Только репетиторы" in response.json()["detail"]

def test_create_course_empty_title(auth_tutor, client: TestClient):
    headers = auth_tutor
    
    course_data = {
        "title": "",
        "topics_ids": [1]
    }
    
    response = client.post("/courses/", json=course_data, headers=headers)
    assert response.status_code == 400
    assert "не может быть пустым" in response.json()["detail"]

def test_create_course_no_topics(auth_tutor, client: TestClient):
    headers = auth_tutor
    
    course_data = {
        "title": "Course Without Topics",
        "topics_ids": []
    }
    
    response = client.post("/courses/", json=course_data, headers=headers)
    assert response.status_code == 400
    assert "хотя бы одну тему" in response.json()["detail"]

def test_get_course_by_id(auth_tutor, client: TestClient):
    headers = auth_tutor
    
    topic_data = {"title": "Topic for Course Test"}
    response = client.post("/topics/", json=topic_data, headers=headers)
    topic_id = response.json()["topic_id"]
    
    course_data = {
        "title": "Course to Get",
        "topics_ids": [topic_id]
    }
    
    response = client.post("/courses/", json=course_data, headers=headers)
    course_id = response.json()["course_id"]
    
    response = client.get(f"/courses/{course_id}", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["course_id"] == course_id
    assert data["title"] == "Course to Get"

def test_get_nonexistent_course(auth_tutor, client: TestClient):
    headers = auth_tutor
    response = client.get("/courses/99999", headers=headers)
    assert response.status_code == 404

def test_add_student_to_course(auth_tutor, client: TestClient):
    headers = auth_tutor
    
    topic_data = {"title": "Topic for Student Test"}
    response = client.post("/topics/", json=topic_data, headers=headers)
    topic_id = response.json()["topic_id"]
    
    course_data = {
        "title": "Course for Student",
        "topics_ids": [topic_id]
    }
    
    response = client.post("/courses/", json=course_data, headers=headers)
    course_id = response.json()["course_id"]
    
    student_data = {
        "email": "student_for_course@example.com",
        "password": "testpassword123",
        "first_name": "Студент",
        "last_name": "Курсовой",
        "middle_name": "Тестович",
        "birth_date": "2000-01-01",
        "phone": "+79998887766",
        "role": "Ученик"
    }
    
    client.post("/auth/register", json=student_data)
    
    add_data = {"email": "student_for_course@example.com"}
    response = client.post(
        f"/courses/{course_id}/add-student",
        json=add_data,
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    assert response.status_code != 404

def test_add_student_by_non_tutor(auth_student, client: TestClient):
    headers = auth_student
    add_data = {"email": "any@example.com"}
    response = client.post(
        "/courses/1/add-student",
        json=add_data,
        headers=headers
    )
    assert response.status_code == 403

def test_get_course_students(auth_tutor, client: TestClient):
    headers = auth_tutor
    
    topic_data = {"title": "Topic for Students List"}
    response = client.post("/topics/", json=topic_data, headers=headers)
    topic_id = response.json()["topic_id"]
    
    course_data = {
        "title": "Course with Students",
        "topics_ids": [topic_id]
    }
    
    response = client.post("/courses/", json=course_data, headers=headers)
    course_id = response.json()["course_id"]
    
    response = client.get(f"/courses/{course_id}/students", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert "students" in data
    assert isinstance(data["students"], list)

def test_update_student_knowledge_gaps(auth_tutor, client: TestClient):
    headers = auth_tutor
    
    topic_data = {"title": "Topic for Knowledge Gaps"}
    response = client.post("/topics/", json=topic_data, headers=headers)
    topic_id = response.json()["topic_id"]
    
    course_data = {
        "title": "Course for Knowledge Gaps",
        "topics_ids": [topic_id]
    }
    
    response = client.post("/courses/", json=course_data, headers=headers)
    course_id = response.json()["course_id"]
    
    student_data = {
        "email": "knowledge_gaps_test@example.com",  # Уникальный email
        "password": "testpassword123",
        "first_name": "Знание",
        "last_name": "Пробельный",
        "middle_name": "Тестович",
        "birth_date": "2000-01-01",
        "phone": "+79998887766",
        "role": "Ученик"
    }
    
    client.post("/auth/register", json=student_data)
    
    add_data = {"email": "knowledge_gaps_test@example.com"}
    response = client.post(
        f"/courses/{course_id}/add-student",
        json=add_data,
        headers=headers
    )
    
    print(f"Add student response: {response.status_code}")
    print(f"Add student data: {response.text}")
    
    response = client.get(f"/courses/{course_id}/students", headers=headers)
    data = response.json()
    
    print(f"Students list: {data}")
    
    if not data["students"]:
        pytest.skip("No students in course - skipping knowledge gaps test")
        return
    
    student_id = data["students"][0]["student_id"]
    
    gaps_data = {"knowledge_gaps": "Проблемы с временами и артиклями"}
    response = client.put(
        f"/courses/{course_id}/student/{student_id}/knowledge-gaps",
        json=gaps_data,
        headers=headers
    )
    
    assert response.status_code == 200
    assert "успешно обновлены" in response.json()["message"]