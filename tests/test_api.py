from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get_all_requests():
    response = client.get("/api/v1/requests/")
    assert response.status_code == 200
    assert len(response.json()) >= 2


def test_get_single_request():
    response = client.get("/api/v1/requests/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["inventory_number"] == "INV-2026-0010"


def test_get_not_found():
    response = client.get("/api/v1/requests/999")
    assert response.status_code == 404


def test_create_request():
    payload = {
        "inventory_number": "INV-2026-0099",
        "lab_room": "Ауд. 401",
        "fault_description": "Перегорел предохранитель осциллографа",
        "applicant_name": "Тестовый Лаборант",
        "priority": 1
    }
    response = client.post("/api/v1/requests/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 3
    assert data["status"] == "Новая"


def test_delete_request():
    response = client.delete("/api/v1/requests/1")
    assert response.status_code == 200

    # Проверяем, что после удаления возвращается 404
    get_res = client.get("/api/v1/requests/1")
    assert get_res.status_code == 404