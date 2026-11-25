def register_user(client, email="customer@example.com"):
    return client.post("/api/v1/auth/register", json={
        "name": "Test Customer",
        "email": email,
        "password": "StrongPassword!123"
    })


def test_customer_registration_and_login(client):
    response = register_user(client)
    assert response.status_code == 201
    assert response.json()["user"]["role"] == "customer"
    login = client.post("/api/v1/auth/login", json={
        "email": "customer@example.com",
        "password": "StrongPassword!123"
    })
    assert login.status_code == 200
    assert login.json()["access_token"]


def test_customer_cannot_access_approvals(client):
    response = register_user(client)
    token = response.json()["access_token"]
    pending = client.get(
        "/api/v1/approvals/admin/pending",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert pending.status_code == 403


def test_ticket_endpoints_require_auth(client):
    response = client.get("/api/v1/tickets/")
    assert response.status_code == 401
