from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_diagnose_with_valid_symptoms():
    response = client.post(
        "/api/diagnose",
        data={"symptoms": "burning discharge"}
    )
    assert response.status_code == 200
    json_data = response.json()
    assert "type" in json_data
    assert "recommendation" in json_data
    assert json_data["type"] != "Unknown"
    print("✅ test_diagnose_with_valid_symptoms passed.")

def test_diagnose_with_unknown_symptoms():
    response = client.post(
        "/api/diagnose",
        data={"symptoms": "gibberishsymptom123"}
    )
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["type"] == "Unknown"
    assert "consult a doctor" in json_data["recommendation"].lower()
    print("✅ test_diagnose_with_unknown_symptoms passed.")

def test_diagnose_with_file_and_symptoms():
    # Simulate file and form upload
    with open("data/urethritis_data.csv", "rb") as file:
        response = client.post(
            "/api/diagnose",
            data={"symptoms": "pain urination"},
            files={"file": ("urethritis_data.csv", file, "text/csv")}
        )
    assert response.status_code == 200
    json_data = response.json()
    assert "type" in json_data
    assert "recommendation" in json_data
    print("✅ test_diagnose_with_file_and_symptoms passed.")
