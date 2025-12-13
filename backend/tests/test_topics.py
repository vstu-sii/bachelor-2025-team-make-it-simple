import pytest
from fastapi.testclient import TestClient

def test_get_topics_unauthorized(client: TestClient):
    response = client.get("/topics/")
    assert response.status_code == 401

def test_get_topics_authorized(auth_student, client: TestClient):
    headers = auth_student
    response = client.get("/topics/", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_topic_tutor(auth_tutor, client: TestClient):
    headers = auth_tutor
    
    topic_data = {
        "title": "Test Topic",
        "description_text": "Test description for topic"
    }
    
    response = client.post("/topics/", json=topic_data, headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["title"] == "Test Topic"
    assert data["description_text"] == "Test description for topic"
    assert "topic_id" in data

def test_create_topic_student_forbidden(auth_student, client: TestClient):
    headers = auth_student
    
    topic_data = {
        "title": "Should Fail Topic",
        "description_text": "This should fail"
    }
    
    response = client.post("/topics/", json=topic_data, headers=headers)
    assert response.status_code == 403
    assert "Только репетиторы" in response.json()["detail"]

def test_create_topic_empty_title(auth_tutor, client: TestClient):
    headers = auth_tutor
    
    topic_data = {
        "title": "",
        "description_text": "Empty title test"
    }
    
    response = client.post("/topics/", json=topic_data, headers=headers)
    assert response.status_code == 400
    assert "не может быть пустым" in response.json()["detail"]

def test_get_topic_by_id(auth_tutor, client: TestClient):
    headers = auth_tutor
    
    topic_data = {"title": "Topic to Get"}
    response = client.post("/topics/", json=topic_data, headers=headers)
    topic_id = response.json()["topic_id"]
    
    response = client.get(f"/topics/{topic_id}", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["topic_id"] == topic_id
    assert data["title"] == "Topic to Get"

def test_update_topic_tutor(auth_tutor, client: TestClient):
    headers = auth_tutor
    
    topic_data = {"title": "Topic to Update"}
    response = client.post("/topics/", json=topic_data, headers=headers)
    topic_id = response.json()["topic_id"]
    
    update_data = {
        "title": "Updated Topic Title",
        "description_text": "Updated description"
    }
    
    response = client.put(f"/topics/{topic_id}", json=update_data, headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["title"] == "Updated Topic Title"
    assert data["description_text"] == "Updated description"

def test_update_topic_student_forbidden(auth_student, client: TestClient):
    headers = auth_student
    
    update_data = {"title": "Should Fail Update"}
    response = client.put("/topics/1", json=update_data, headers=headers)
    assert response.status_code == 403

def test_delete_topic_tutor(auth_tutor, client: TestClient):
    headers = auth_tutor
    
    topic_data = {"title": "Topic to Delete"}
    response = client.post("/topics/", json=topic_data, headers=headers)
    topic_id = response.json()["topic_id"]
    
    response = client.delete(f"/topics/{topic_id}", headers=headers)
    assert response.status_code == 200
    assert "успешно удалена" in response.json()["message"]
    
    response = client.get(f"/topics/{topic_id}", headers=headers)
    assert response.status_code == 404

def test_search_topics(auth_tutor, client: TestClient):
    headers = auth_tutor
    
    topics = [
        {"title": "Present Simple"},
        {"title": "Past Continuous"},
        {"title": "Future Perfect"}
    ]
    
    for topic in topics:
        client.post("/topics/", json=topic, headers=headers)
    
    response = client.get("/topics/search/?title=Present", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    assert any("Present" in topic["title"] for topic in data)