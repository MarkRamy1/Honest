def test_register_and_login_flow(client):
    # 1. Register new user
    reg_payload = {
        "name": "Sarah Connor",
        "email": "sarah@cyberdyne.com",
        "password": "resistance123"
    }
    res = client.post("/api/auth/register", json=reg_payload)
    assert res.status_code == 201
    data = res.json()
    assert data["success"] is True
    assert data["user"]["email"] == "sarah@cyberdyne.com"
    assert "token" in data
    token = data["token"]

    # 2. Check /api/auth/me with Bearer token
    me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["authenticated"] is True
    assert me_data["user"]["name"] == "Sarah Connor"

    # 3. Prevent duplicate email registration
    dup_res = client.post("/api/auth/register", json=reg_payload)
    assert dup_res.status_code == 422

    # 4. Login with correct password
    login_res = client.post("/api/auth/login", json={
        "email": "sarah@cyberdyne.com",
        "password": "resistance123"
    })
    assert login_res.status_code == 200
    assert login_res.json()["success"] is True

    # 5. Reject wrong password
    bad_login = client.post("/api/auth/login", json={
        "email": "sarah@cyberdyne.com",
        "password": "wrongpassword"
    })
    assert bad_login.status_code == 401


def test_seeded_demo_user_login(client):
    # Default seeded shopper: shopper@honestai.com / password123
    login_res = client.post("/api/auth/login", json={
        "email": "shopper@honestai.com",
        "password": "password123"
    })
    assert login_res.status_code == 200
    data = login_res.json()
    assert data["success"] is True
    assert data["user"]["name"] == "Honest Verified Buyer"


def test_logout(client):
    res = client.post("/api/auth/logout")
    assert res.status_code == 200
    assert res.json()["success"] is True
