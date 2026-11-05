def test_vlm_audit(client):
    res = client.post("/api/vlm/audit", json={
        "productName": "Oversized Wool Blend Trench Coat",
        "category": "Women's Apparel & Outerwear"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "audit" in data
    assert "authenticity_score" in data["audit"]
    assert "analysis_breakdown" in data["audit"]


def test_vlm_generate_reality(client):
    res = client.post("/api/vlm/generate-reality", json={
        "prompt": "Authentic trench coat under living room lamp",
        "lighting": "apartment"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "prompt" in data
    assert data["lighting"] == "apartment"
