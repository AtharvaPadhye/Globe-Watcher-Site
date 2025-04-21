import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}  # Adjust based on your actual response

def test_some_endpoint():
    response = client.post("/some-endpoint", json={"key": "value"})
    assert response.status_code == 201
    assert response.json() == {"result": "success"}  # Adjust based on your actual response

# Add more tests as needed for your application logic