
def create_sample_ticket(client):
    """Helper function to create a sample support ticket."""

    response = client.post(
        "/api/v1/tickets/",
        json={
            "customer_name": "Rahul Sharma",
            "customer_email": "rahul@example.com",
            "subject": "Duplicate subscription payment",
            "description": "I was charged twice for my monthly subscription."
        }
    )

    return response


def test_health_check(client):
    """Test whether the API is running."""

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_create_ticket(client):
    """Test creating a new support ticket."""

    response = create_sample_ticket(client)

    assert response.status_code == 201

    data = response.json()

    assert data["subject"] == "Duplicate subscription payment"
    assert data["status"] == "open"
    assert data["priority"] == "medium"
    assert data["category"] == "general"


def test_get_all_tickets(client):
    """Test retrieving all support tickets."""

    create_sample_ticket(client)

    response = client.get("/api/v1/tickets/")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["subject"] == "Duplicate subscription payment"


def test_get_ticket_by_id(client):
    """Test retrieving a ticket using its ID."""

    create_response = create_sample_ticket(client)

    ticket_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/tickets/{ticket_id}"
    )

    assert response.status_code == 200
    assert response.json()["id"] == ticket_id


def test_update_ticket(client):
    """Test updating ticket status and priority."""

    create_response = create_sample_ticket(client)

    ticket_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/tickets/{ticket_id}",
        json={
            "status": "in_progress",
            "priority": "high"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "in_progress"
    assert data["priority"] == "high"


def test_ticket_not_found(client):
    """Test retrieving a nonexistent ticket."""

    response = client.get("/api/v1/tickets/9999")

    assert response.status_code == 404


def test_invalid_ticket_input(client):
    """Test validation of invalid ticket data."""

    response = client.post(
        "/api/v1/tickets/",
        json={
            "customer_name": "R",
            "customer_email": "invalid-email",
            "subject": "Bug",
            "description": "Help"
        }
    )

    assert response.status_code == 422
