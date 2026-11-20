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


def test_google_signup_and_signin_flow(client):
    # 1. First-time Google Sign-Up auto-creates the account
    google_payload = {
        "email": "nour.elmasry@gmail.com",
        "name": "Nour El-Masry"
    }
    res1 = client.post("/api/auth/google", json=google_payload)
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["success"] is True
    assert data1["is_new_user"] is True
    assert data1["user"]["email"] == "nour.elmasry@gmail.com"
    assert data1["user"]["name"] == "Nour El-Masry"
    assert "token" in data1

    # 2. Subsequent Google Sign-In logs in the existing user without duplicating
    res2 = client.post("/api/auth/google", json=google_payload)
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["success"] is True
    assert data2["is_new_user"] is False
    assert data2["user"]["id"] == data1["user"]["id"]
