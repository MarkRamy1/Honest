def test_reviews_listing_and_stats(client):
    res = client.get("/api/reviews")
    assert res.status_code == 200
    assert "max-age=" in res.headers.get("Cache-Control", "")
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


def test_supabase_composite_indexes_and_pooling_config():
    from app.db.base import Base
    from app.db import session as db_session

    reviews_table = Base.metadata.tables["reviews"]
    stores_table = Base.metadata.tables["stores_reputation"]

    review_index_names = {idx.name for idx in reviews_table.indexes}
    store_index_names = {idx.name for idx in stores_table.indexes}

    assert "ix_reviews_product_tier_created" in review_index_names
    assert "ix_reviews_created_at_id" in review_index_names
    assert "ix_stores_trust_platform" in store_index_names
    assert getattr(db_session, "POSTGRES_POOL_CONFIG", {}).get("pool_pre_ping") is True


def test_review_delete_enforces_user_ownership(client):
    # Register User A & User B
    user_a = client.post("/api/auth/register", json={
        "name": "Owner A",
        "email": "owner_a_rls@honest.ai",
        "password": "Password123!"
    }).json()["token"]
    user_b = client.post("/api/auth/register", json={
        "name": "Intruder B",
        "email": "intruder_b_rls@honest.ai",
        "password": "Password123!"
    }).json()["token"]

    # User A creates a review
    create_res = client.post(
        "/api/reviews",
        json={
            "product_name": "Apple AirPods Pro 2",
            "tier": "original",
            "rating": 5,
            "material_accuracy_rating": 5,
            "price_paid": 249.0,
            "comment": "Verified authentic Apple H2 chip and ANC.",
            "store_purchased_from": "Amazon Egypt"
        },
        headers={"Authorization": f"Bearer {user_a}"}
    )
    assert create_res.status_code == 201
    rev_id = create_res.json()["review"]["id"]

    # User B tries to delete User A's review -> Must be 403 Forbidden
    forbidden_res = client.delete(
        f"/api/reviews/{rev_id}",
        headers={"Authorization": f"Bearer {user_b}"}
    )
    assert forbidden_res.status_code == 403

    # User A deletes their own review -> Must be 200 OK
    ok_res = client.delete(
        f"/api/reviews/{rev_id}",
        headers={"Authorization": f"Bearer {user_a}"}
    )
    assert ok_res.status_code == 200
    assert ok_res.json()["success"] is True

