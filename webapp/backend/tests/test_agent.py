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


def test_agent_stepped_price_history_and_fake_discount_detector(client):
    # 1. Verified product should include 90-day stepped price history watermarks & stock status
    res = client.post("/api/agent/ask", json={
        "question": "Sony WH-1000XM5 Wireless Headphones",
        "tier": "all"
    })
    assert res.status_code == 200
    orig = res.json()["price_matrix"]["original"]
    assert orig["stock_status"] == "IN_STOCK"
    ph = orig["price_history"]
    assert ph is not None
    assert len(ph["points"]) == 6
    assert ph["lowest_usd"].startswith("$")
    assert ph["highest_usd"].startswith("$")
    assert ph["avg_90d_usd"].startswith("$")
    assert ph["discount_verdict"] in ("REAL_DROP", "INFLATED_MSRP", "FAIR_MARKET")

    # 2. Unverified product must never fabricate price history
    unverified_res = client.post("/api/agent/ask", json={
        "question": "NonExistentQuantumPhone9999XYZ",
        "tier": "all"
    })
    assert unverified_res.status_code == 200
    assert unverified_res.json()["price_matrix"]["original"].get("price_history") is None
