from uuid import uuid4

from fastapi.testclient import TestClient
import pytest
from demo_target.app import app

def test_underage_resgistration_does_not_save_user():
    email = f"underage-{uuid4()}@example.test"

    with TestClient(app) as client:
        response = client.post("/users", json={"email": email, "age": 17})
        assert response.status_code == 422

        # Ensure the user was not saved
        lookup = client.get("/users", params={"email": email})
        assert lookup.status_code == 200
        assert lookup.json() == {"items": []}

def test_valid_registration_saves_user():
    email = f"valid-{uuid4()}@example.test"

    with TestClient(app) as client:
        response = client.post("/users", json={"email": email, "age": 18})
        assert response.status_code == 201

        # Ensure the user was saved
        lookup = client.get("/users", params={"email": email})
        assert lookup.status_code == 200
        assert lookup.json() == {"items": [{"email": email, "age": 18, "id": lookup.json()["items"][0]["id"]}]}

def test_duplicate_registration_fails():
    email = f"duplicate-{uuid4()}@example.test"

    with TestClient(app) as client:
        response = client.post("/users", json={"email": email, "age": 18})
        assert response.status_code == 201

        # Attempt to register the same email again
        response = client.post("/users", json={"email": email, "age": 18})
        assert response.status_code == 409
        assert response.json() == {"detail": "Email already registered"}
        # Ensure the user was not duplicated
        lookup = client.get("/users", params={"email": email})
        assert lookup.status_code == 200
        assert len(lookup.json()["items"]) == 1
        assert lookup.json()["items"][0]["email"] == email
        assert lookup.json()["items"][0]["age"] == 18

@pytest.mark.parametrize("missing_field", ["email", "age"])
def test_missing_required_field_is_rejected(missing_field):
    email = f"missing-{uuid4()}@example.test"
    payload = {"email": email, "age": 18}
    del payload[missing_field]

    with TestClient(app) as client:
        response = client.post("/users", json=payload)

        assert response.status_code == 422
        assert any(
            error["loc"] == ["body", missing_field]
            and error["type"] == "missing"
            for error in response.json()["detail"]
        )

        # When email was supplied, verify no user was saved under it.
        if missing_field == "age":
            lookup = client.get("/users", params={"email": email})
            assert lookup.status_code == 200
            assert lookup.json() == {"items": []}

def test_cleanup_removes_user_and_can_be_repeated():
    email = f"cleanup-{uuid4()}@example.test"

    with TestClient(app) as client:
        created = client.post(
            "/users",
            json={"email": email, "age": 18},
        )
        assert created.status_code == 201

        deleted = client.delete(
            "/test-support/users",
            params={"email": email},
        )
        assert deleted.status_code == 204

        lookup = client.get("/users", params={"email": email})
        assert lookup.status_code == 200
        assert lookup.json() == {"items": []}

        # Repeating cleanup must also succeed.
        repeated = client.delete(
            "/test-support/users",
            params={"email": email},
        )
        assert repeated.status_code == 204

   