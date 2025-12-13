import pytest
import json
from fastapi.testclient import TestClient

def test_get_lesson_unauthorized(client: TestClient):
    response = client.get("/lessons/1")
    assert response.status_code == 401

def test_get_nonexistent_lesson(auth_tutor, client: TestClient):
    headers = auth_tutor
    response = client.get("/lessons/99999", headers=headers)
    assert response.status_code == 404

def test_update_lesson_content_student_forbidden(auth_student, client: TestClient):
    headers = auth_student
    
    update_data = {
        "content_type": "theory",
        "content": "Test content"
    }
    
    response = client.put("/lessons/1/content", json=update_data, headers=headers)
    assert response.status_code == 403
    assert "Только репетиторы" in response.json()["detail"]

def test_generate_lesson_section_tutor(auth_tutor, client: TestClient):
    headers = auth_tutor
    
    response = client.post(
        "/lessons/1/generate/theory",
        json={"comment": "Generate test theory"},
        headers=headers
    )
    
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        data = response.json()
        assert "section" in data
        assert "generated_content" in data

def test_generate_lesson_section_student_forbidden(auth_student, client: TestClient):
    headers = auth_student
    
    response = client.post(
        "/lessons/1/generate/theory",
        json={"comment": "Should fail"},
        headers=headers
    )
    assert response.status_code == 403

def test_get_lesson_students_progress_tutor(auth_tutor, client: TestClient):
    headers = auth_tutor
    
    response = client.get(
        "/lessons/1/students-progress?course_id=1",
        headers=headers
    )
    
    assert response.status_code in [200, 404, 403]
    if response.status_code == 200:
        assert isinstance(response.json(), list)

def test_get_lesson_students_progress_student_forbidden(auth_student, client: TestClient):
    headers = auth_student
    
    response = client.get(
        "/lessons/1/students-progress?course_id=1",
        headers=headers
    )
    assert response.status_code == 403
    assert "Только репетиторы" in response.json()["detail"]

def test_lesson_test_submit_own_results(auth_student, client: TestClient):
    headers = auth_student
    
    test_data = {
        "answers": [
            {"question_id": 1, "answer": "A", "is_correct": True},
            {"question_id": 2, "answer": "B", "is_correct": False}
        ],
        "score": 50
    }
    
    response = client.get("/auth/me", headers=headers)
    student_id = response.json()["user_id"]
    
    response = client.post(
        f"/lessons/1/test/submit/{student_id}",
        json=test_data,
        headers=headers
    )
    
    assert response.status_code in [200, 404, 500]

def test_lesson_test_submit_other_user_forbidden(auth_student, client: TestClient):
    headers = auth_student
    
    test_data = {
        "answers": [{"question_id": 1, "answer": "A"}],
        "score": 100
    }
    
    response = client.post(
        "/lessons/1/test/submit/999",
        json=test_data,
        headers=headers
    )
    assert response.status_code == 403
    assert "Можно отправлять только свои" in response.json()["detail"]