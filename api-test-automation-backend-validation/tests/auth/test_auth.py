import pytest

from utils.assertions import assert_error, assert_json_keys, assert_status


@pytest.mark.smoke
@pytest.mark.functional
def test_register_valid_user(api):
    response = api.post(
        "/auth/register",
        json={
            "name": "Aarav Mehta",
            "email": "aarav@example.com",
            "password": "StrongPass123",
        },
    )
    assert_status(response, 201)
    body = assert_json_keys(response, "id", "name", "email", "role")
    assert body["email"] == "aarav@example.com"
    assert "password" not in body
    assert "password_hash" not in body


@pytest.mark.regression
@pytest.mark.functional
def test_register_duplicate_email(api, primary_user):
    response = api.post(
        "/auth/register",
        json={
            "name": "Another User",
            "email": "aarav@example.com",
            "password": "StrongPass999",
        },
    )
    assert_error(response, 409, "already exists")


@pytest.mark.parametrize(
    "email",
    ["not-an-email", "missing-domain@", "@missing-user.com"],
)
@pytest.mark.regression
@pytest.mark.functional
def test_register_invalid_email(api, email):
    response = api.post(
        "/auth/register",
        json={
            "name": "Bad User",
            "email": email,
            "password": "StrongPass123",
        },
    )
    assert_status(response, 422)


@pytest.mark.regression
@pytest.mark.functional
def test_register_missing_required_field(api):
    response = api.post(
        "/auth/register",
        json={
            "email": "missing-name@example.com",
            "password": "StrongPass123",
        },
    )
    assert_status(response, 422)


@pytest.mark.smoke
@pytest.mark.functional
def test_login_valid_credentials(api, primary_user):
    response = api.login("aarav@example.com", "StrongPass123")
    assert_status(response, 200)
    body = assert_json_keys(response, "access_token", "token_type")
    assert body["token_type"] == "bearer"


@pytest.mark.regression
@pytest.mark.functional
def test_login_invalid_password(api, primary_user):
    response = api.login("aarav@example.com", "WrongPassword123")
    assert_error(response, 401, "Invalid email or password")


@pytest.mark.regression
@pytest.mark.functional
def test_login_unknown_email(api):
    response = api.login("unknown@example.com", "StrongPass123")
    assert_error(response, 401, "Invalid email or password")


@pytest.mark.smoke
@pytest.mark.functional
def test_access_protected_endpoint_with_valid_token(api, primary_user):
    response = api.get("/auth/me")
    assert_status(response, 200)
    assert response.json()["email"] == "aarav@example.com"


@pytest.mark.regression
@pytest.mark.functional
def test_access_protected_endpoint_without_token(client):
    response = client.get("/auth/me")
    assert_status(response, 401)


@pytest.mark.regression
@pytest.mark.functional
def test_access_protected_endpoint_with_invalid_token(api):
    api.token = "not-a-real-jwt"
    response = api.get("/auth/me")
    assert_error(response, 401, "Invalid or expired access token")


def test_health_endpoint(client):
    response = client.get("/health")
    assert_status(response, 200)
    assert response.json()["status"] == "ok"
