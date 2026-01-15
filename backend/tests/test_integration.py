"""Integration tests for health and intake endpoints using TestClient.

These tests run the FastAPI app in-process so they don't require a running
server. They intentionally avoid endpoints that need external DB/LLM calls.
"""


def test_health_and_intake_endpoints(client):
    """Call `/api/chat/health` and `/api/chat/intake` via TestClient.

    The intake endpoint performs basic validation and returns an `intake_id`.
    This test asserts the expected behavior without requiring DB or LLM.
    """
    # Health check
    r = client.get("/api/chat/health")
    assert r.status_code == 200
    body = r.json()
    assert isinstance(body, dict)
    assert body.get("status") == "healthy"

    # Valid intake submission
    intake_data = {"skin_type": "oily", "sensitive": "no", "concerns": ["acne"]}
    r = client.post("/api/chat/intake", json=intake_data)
    assert r.status_code == 200
    body = r.json()
    assert body.get("status") == "success"
    assert "intake_id" in body

    # Invalid intake (missing required field) -> 400
    bad_intake = {"sensitive": "no"}
    r = client.post("/api/chat/intake", json=bad_intake)
    assert r.status_code == 400
