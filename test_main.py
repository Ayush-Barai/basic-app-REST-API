from fastapi.testclient import TestClient
from main import app 

client = TestClient(app)

def test_view_all_patients():
    response = client.get("/patients")
    assert response.status_code == 200
    assert isinstance(response.json(), dict)

def test_view_single_patient():
    # First, create a patient to ensure it exists
    patient_data = {
        "id": "P021",
        "name": "Ayush Barai",
        "age": 30,
        "hospital": "City Hospital",
        "weight": 70.5,
        "height": 175.0
    }
    client.post("/patients", json=patient_data)

    response = client.get("/patients/P021")
    assert response.status_code == 200
    assert response.json()["hospital"] == "City Hospital"

def test_update_patient():
    update_data = {
        "age": 31,
        "weight": 72.0
    }
    response = client.put("/patients/P021", json=update_data)
    assert response.status_code == 200
    assert response.json()["message"] == "Patient updated successfully"


def test_delete_patient():
    response = client.delete("/patients/P021")
    assert response.status_code == 200
    assert response.json()["message"] == "Patient deleted successfully"