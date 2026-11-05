def test_health_check_api_prefix(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["version"] == "4.0.0"
    assert "capabilities" in data
    assert "multimodal_vlm_audit" in data["capabilities"]
    assert "autonomous_shopping_research" in data["capabilities"]


def test_health_check_root(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"


def test_root_index(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["app"] == "Honest AI"
    assert data["status"] == "online"
