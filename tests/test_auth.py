def register_user(client, email="customer@example.com", extra=None):
    payload = {
        "name": "Test Customer",
        "email": email,
        "password": "StrongPassword!123",
    }
    if extra:
        payload.update(extra)
    return client.post("/api/v1/auth/register", json=payload)


def test_customer_registration_and_login(client):
    response = register_user(client)
    assert response.status_code == 201
    assert response.json()["user"]["role"] == "customer"
    login = client.post("/api/v1/auth/login", json={
        "email": "customer@example.com",
        "password": "StrongPassword!123",
    })
    assert login.status_code == 200
    assert login.json()["access_token"]


def test_customer_cannot_self_assign_admin_role(client):
    response = register_user(client, extra={"role": "admin"})
    assert response.status_code == 201
    assert response.json()["user"]["role"] == "customer"


def test_customer_cannot_access_approvals(client):
    token = register_user(client).json()["access_token"]
    pending = client.get(
        "/api/v1/approvals/pending",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert pending.status_code == 403


def test_ticket_endpoints_require_authentication(client):
    response = client.get("/api/v1/tickets/", headers={"Authorization": "Bearer invalid-token"})
    assert response.status_code == 401


def test_customer_cannot_view_another_customers_ticket(client):
    first = register_user(client, "first@example.com").json()
    created = client.post(
        "/api/v1/tickets/",
        headers={"Authorization": f"Bearer {first['access_token']}"},
        json={
            "subject": "My network connection fails",
            "description": "The internet disconnects several times every day.",
            "preferred_language": "en",
        },
    )
    assert created.status_code == 201
    ticket_id = created.json()["id"]

    second = register_user(client, "second@example.com").json()
    response = client.get(
        f"/api/v1/tickets/{ticket_id}",
        headers={"Authorization": f"Bearer {second['access_token']}"},
    )
    assert response.status_code == 404


def test_admin_can_create_support_account(client):
    response = client.post(
        "/api/v1/admin/users/support",
        json={"email": "agent@example.com", "password": "SupportPassword!123"},
    )
    assert response.status_code == 201
    assert response.json()["role"] == "support"

    login = client.post(
        "/api/v1/auth/login",
        json={"email": "agent@example.com", "password": "SupportPassword!123"},
    )
    assert login.status_code == 200
    assert login.json()["user"]["role"] == "support"
