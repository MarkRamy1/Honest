def test_reviews_listing_and_stats(client):
    res = client.get("/api/reviews")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert len(data["reviews"]) >= 1
    assert data["stats"]["total_reviews"] >= 1
    assert data["stats"]["avg_rating"] > 0


def test_submit_and_upvote_review(client):
    new_rev = {
        "product_name": "Sony WH-1000XM5 Wireless Noise-Cancelling Headphones",
        "user_name": "AudioTester",
        "tier": "original",
        "rating": 5,
        "material_accuracy_rating": 5,
        "price_paid": 329.00,
        "comment": "Superb authentic audio gear with verified soft synthetic leather.",
        "store_purchased_from": "Amazon Prime"
    }
    create_res = client.post("/api/reviews", json=new_rev)
    assert create_res.status_code == 201
    created_data = create_res.json()
    assert created_data["success"] is True
    rev_id = created_data["review"]["id"]
    assert created_data["review"]["upvotes"] == 0

    # Upvote review
    upvote_res = client.post(f"/api/reviews/{rev_id}/upvote")
    assert upvote_res.status_code == 200
    assert upvote_res.json()["upvotes"] == 1
