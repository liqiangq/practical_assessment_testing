from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_round_trip_tokenize_detokenize():
    payload = [
        "4111-1111-1111-1111",
        "4444-3333-2222-1111",
        "4444-1111-2222-3333",
    ]

    tokenize_response = client.post("/tokenize", json=payload)
    assert tokenize_response.status_code == 200

    tokens = tokenize_response.json()
    assert len(tokens) == 3
    assert all(len(token) == 32 for token in tokens)

    detokenize_response = client.post("/detokenize", json=tokens)
    assert detokenize_response.status_code == 200
    assert detokenize_response.json() == payload


def test_same_account_returns_same_token():
    payload = ["4111-1111-1111-1111"]

    response1 = client.post("/tokenize", json=payload)
    response2 = client.post("/tokenize", json=payload)

    assert response1.status_code == 200
    assert response2.status_code == 200
    assert response1.json()[0] == response2.json()[0]


def test_detokenize_invalid_format():
    response = client.post("/detokenize", json=["bad-token"])
    assert response.status_code == 400
    body = response.json()
    assert body["message"] == "Invalid token format. Expected 32 characters in [0-9A-Za-z]."


def test_detokenize_not_found():
    response = client.post("/detokenize", json=["A" * 32])
    assert response.status_code == 404
    body = response.json()
    assert body["message"] == "Token not found"
