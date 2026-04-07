import json


def test_chat_endpoint_success(client):
    payload = {"message": "I feel anxious today", "user_id": "u1"}
    res = client.post("/api/chat", data=json.dumps(payload), content_type="application/json")
    assert res.status_code == 200
    data = res.get_json()
    assert "response" in data
    assert "sentiment" in data
    assert "risk" in data


def test_analyze_requires_text(client):
    res = client.post("/api/analyze", data=json.dumps({}), content_type="application/json")
    assert res.status_code == 400


def test_emergency_endpoint(client):
    res = client.get("/api/emergency")
    assert res.status_code == 200
    data = res.get_json()
    assert "helplines" in data
    assert isinstance(data["helplines"], list)
