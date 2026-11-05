def test_catalog_search(client):
    res = client.get("/api/catalog/search?q=Sony")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["count"] >= 1
    product = data["products"][0]
    assert "Sony WH-1000XM5" in product["name"]
    assert product["original_msrp"] == 399.99
    assert "carbon-fiber" in product["authentic_materials"].lower()


def test_catalog_stores(client):
    res = client.get("/api/catalog/stores")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert len(data["stores"]) >= 3
    first_store = data["stores"][0]
    assert first_store["trust_score"] >= 90
