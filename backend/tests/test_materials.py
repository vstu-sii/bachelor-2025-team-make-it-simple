import pytest
import io
from fastapi.testclient import TestClient

def test_get_materials_unauthorized(client: TestClient):
    response = client.get("/materials/")
    assert response.status_code == 401

def test_get_materials_authorized(auth_student, client: TestClient):
    headers = auth_student
    response = client.get("/materials/", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_upload_material_tutor(auth_tutor, client: TestClient):
    headers = auth_tutor
    
    file_content = b"%PDF-1.4 test pdf content"
    files = {
        "file": ("test.pdf", io.BytesIO(file_content), "application/pdf")
    }
    
    response = client.post("/materials/upload/", files=files, headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert "material_id" in data
    assert "file_path" in data
    assert data["file_path"].endswith(".pdf")

def test_upload_material_student_forbidden(auth_student, client: TestClient):
    headers = auth_student
    
    file_content = b"test content"
    files = {
        "file": ("test.pdf", io.BytesIO(file_content), "application/pdf")
    }
    
    response = client.post("/materials/upload/", files=files, headers=headers)
    assert response.status_code == 403
    assert "Только репетиторы" in response.json()["detail"]

def test_upload_non_pdf_file(auth_tutor, client: TestClient):
    headers = auth_tutor
    
    file_content = b"test txt content"
    files = {
        "file": ("test.txt", io.BytesIO(file_content), "text/plain")
    }
    
    response = client.post("/materials/upload/", files=files, headers=headers)
    assert response.status_code == 400
    assert "Поддерживается только PDF" in response.json()["detail"]

def test_delete_material_tutor(auth_tutor, client: TestClient):
    headers = auth_tutor
    
    file_content = b"%PDF-1.4 to delete"
    files = {
        "file": ("delete_me.pdf", io.BytesIO(file_content), "application/pdf")
    }
    
    response = client.post("/materials/upload/", files=files, headers=headers)
    material_id = response.json()["material_id"]
    
    response = client.delete(f"/materials/{material_id}", headers=headers)
    assert response.status_code == 200
    assert "успешно удален" in response.json()["message"]
    
    response = client.get(f"/materials/{material_id}", headers=headers)
    assert response.status_code == 404

def test_search_materials(auth_tutor, client: TestClient):
    headers = auth_tutor
    
    file_content = b"%PDF-1.4 searchable content"
    files = {
        "file": ("search_test.pdf", io.BytesIO(file_content), "application/pdf")
    }
    
    client.post("/materials/upload/", files=files, headers=headers)
    
    response = client.get("/materials/search/?filename=search", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)