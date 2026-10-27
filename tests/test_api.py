from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()

def test_ask_returns_disclaimer():
    response = client.post("/ask", json={"question": "Tell me about education scheme eligibility"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["answer"]
    assert payload["disclaimer"]
    assert "sources" in payload
