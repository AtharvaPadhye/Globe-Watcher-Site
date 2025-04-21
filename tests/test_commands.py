from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_execute_command():
    response = client.post("/commands/", json={
        "command_name": "test_command",
        "parameters": {"key": "value"},
        "timestamp": "2023-01-01T00:00:00"
    })
    assert response.status_code == 200
    assert response.json()["status"] == "Command executed"
