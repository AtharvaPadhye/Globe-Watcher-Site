from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_send_telemetry():
    response = client.post("/telemetry/", json={
        "satellite_id": "sat-123",
        "data": {"temperature": 22.5}
    })
    assert response.status_code == 200
    assert response.json()["status"] == "Telemetry received"
