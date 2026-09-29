import os

os.environ["MOCK_AI"] = "true"

from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200

    assert response.json()["status"] == "healthy"


def test_generate():
    response = client.post(
        "/generate",
        json={
            "document_type": "Service Agreement",
            "parties": "Company and Client",
            "terms": "Payment; Confidentiality",
            "dates": "2026-01-01",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["document_type"] == (
        "Service Agreement"
    )

    assert data["content"]

    assert data["generated_by"] == "Mock AI"


def test_generate_rejects_empty_terms():
    response = client.post(
        "/generate",
        json={
            "document_type": "Agreement",
            "parties": "Company and Client",
            "terms": "",
            "dates": "2026-01-01",
        },
    )

    assert response.status_code == 422