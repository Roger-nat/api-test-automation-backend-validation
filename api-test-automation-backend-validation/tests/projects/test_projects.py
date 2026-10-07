import pytest

from utils.assertions import assert_error, assert_status
from utils.db_validator import project_by_id, project_count_for_owner


@pytest.mark.smoke
@pytest.mark.functional
@pytest.mark.database
def test_create_project_persists_to_database(api, primary_user, db):
    response = api.post(
        "/projects",
        json={
            "name": "Checkout Regression",
            "description": "Mobile checkout regression suite",
        },
    )
    assert_status(response, 201)
    project = response.json()

    stored = project_by_id(db, project["id"])
    assert stored is not None
    assert stored.name == "Checkout Regression"
    assert stored.owner_id == primary_user["id"]


@pytest.mark.regression
def test_project_requires_name(api, primary_user):
    response = api.post("/projects", json={"description": "No name"})
    assert_status(response, 422)


@pytest.mark.regression
def test_duplicate_project_is_rejected(api, project):
    response = api.post(
        "/projects",
        json={"name": project["name"], "description": "duplicate"},
    )
    assert_error(response, 409, "already have")


@pytest.mark.functional
def test_list_projects_returns_only_current_users_projects(api, project, db):
    response = api.get("/projects")
    assert_status(response, 200)
    assert len(response.json()) == project_count_for_owner(db, project["owner_id"])
    assert response.json()[0]["name"] == project["name"]


@pytest.mark.functional
def test_get_project(api, project):
    response = api.get(f"/projects/{project['id']}")
    assert_status(response, 200)
    assert response.json()["id"] == project["id"]


@pytest.mark.regression
def test_get_missing_project(api, primary_user):
    response = api.get("/projects/9999")
    assert_error(response, 404, "not found")


@pytest.mark.functional
@pytest.mark.database
def test_update_project_persists_changes(api, project, db):
    response = api.put(
        f"/projects/{project['id']}",
        json={"name": "Checkout Regression Updated"},
    )
    assert_status(response, 200)
    assert response.json()["name"] == "Checkout Regression Updated"

    stored = project_by_id(db, project["id"])
    assert stored is not None
    assert stored.name == "Checkout Regression Updated"


@pytest.mark.regression
def test_other_user_cannot_access_project(api, project, second_user_api):
    second_user_api.token = api.token
    # Replace token with actual second user's token.
    second_user_api.login("riya@example.com", "StrongPass456")
    response = second_user_api.get(f"/projects/{project['id']}")
    assert_status(response, 403)


@pytest.mark.database
def test_delete_project_removes_it(api, project, db):
    response = api.delete(f"/projects/{project['id']}")
    assert_status(response, 204)
    assert project_by_id(db, project["id"]) is None
