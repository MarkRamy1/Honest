def test_agent_models(client):
    res = client.get("/api/agent/models")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert len(data["models"]) >= 3


def test_agent_ask_product_audit(client):
    res = client.post("/api/agent/ask", json={
        "question": "Sony WH-1000XM5 Wireless Headphones",
        "tier": "all"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "material_verdict" in data
    assert "price_matrix" in data
    assert "best_price" in data
    assert data["price_matrix"]["original"]["price"]


def test_agent_ask_recommendation(client):
    res = client.post("/api/agent/ask", json={
        "question": "What is the best laptop for gaming under $1000?"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["is_recommendation"] is True
    assert "recommendation" in data
    assert "price_matrix" in data


def test_agent_compare_in_cart(client):
    res = client.post("/api/agent/compare-in-cart", json={
        "productTitle": "Cheap Knockoff Headphones",
        "currentPrice": 45.00
    })
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "top_alternative" in data
    assert "comparison" in data
    assert data["comparison"]["verdict_headline"]


def test_agent_autonomous_research_workflow(client):
    res = client.post("/api/agent/research", json={
        "query": "Sony WH-1000XM5",
        "destination_country": "US"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert len(data["workflow_steps"]) >= 4
    assert data["recommendation"]["top_value_pick"] is not None
