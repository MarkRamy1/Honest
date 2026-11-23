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
    assert "max-age=" in res.headers.get("Cache-Control", "")
    data = res.json()
    assert data["success"] is True
    assert len(data["stores"]) >= 3
    first_store = data["stores"][0]
    assert first_store["trust_score"] >= 90


def test_catalog_pagination_limits_and_cache_headers(client):
    search_res = client.get("/api/catalog/search?limit=2")
    assert search_res.status_code == 200
    assert "max-age=" in search_res.headers.get("Cache-Control", "")
    assert len(search_res.json()["products"]) <= 2

    stores_res = client.get("/api/catalog/stores?limit=2")
    assert stores_res.status_code == 200
    assert len(stores_res.json()["stores"]) == 2

