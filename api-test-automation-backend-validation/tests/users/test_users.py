import pytest

from utils.assertions import assert_error, assert_status
from utils.db_validator import user_by_id


@pytest.mark.smoke
@pytest.mark.functional
def test_authenticated_user_can_list_users(api, primary_user):
    response = api.get("/users")
    assert_status(response, 200)
    assert any(user["id"] == primary_user["id"] for user in response.json())


@pytest.mark.functional
def test_get_user_by_id(api, primary_user):
    response = api.get(f"/users/{primary_user['id']}")
    assert_status(response, 200)
    assert response.json()["email"] == "aarav@example.com"


@pytest.mark.regression
def test_get_missing_user(api, primary_user):
    response = api.get("/users/9999")
    assert_error(response, 404, "not found")


@pytest.mark.regression
def test_update_own_profile(api, primary_user):
    response = api.put(
        f"/users/{primary_user['id']}",
        json={"name": "Aarav Updated"},
    )
    assert_status(response, 200)
    assert response.json()["name"] == "Aarav Updated"


@pytest.mark.parametrize(
    "payload",
    [
        {"name": "x"},
        {"name": ""},
        {"email": "not-valid"},
    ],
)
@pytest.mark.regression
def test_update_user_rejects_invalid_data(api, primary_user, payload):
    response = api.put(f"/users/{primary_user['id']}", json=payload)
    assert_status(response, 422)


@pytest.mark.regression
def test_user_cannot_modify_another_account(multiple_users, api):
    primary, second = multiple_users
    response = api.put(
        "/users/2",
        json={"name": "Hijack Attempt"},
    )
    # IDs are deterministic in an empty test DB: first user=1, second user=2.
    assert_status(response, 403)


@pytest.mark.regression
def test_delete_own_user(api, primary_user, db):
    response = api.delete(f"/users/{primary_user['id']}")
    assert_status(response, 204)
    assert user_by_id(db, primary_user["id"]) is None
