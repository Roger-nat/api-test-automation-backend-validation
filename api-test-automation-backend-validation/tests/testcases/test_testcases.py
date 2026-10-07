import pytest

from utils.assertions import assert_error, assert_status
from utils.db_validator import get_testcase_by_id


@pytest.mark.functional
@pytest.mark.database
def test_create_testcase(api, project, db):
    response = api.post(
        f"/projects/{project['id']}/testcases",
        json={
            "title": "Checkout with valid card",
            "description": "Verify checkout succeeds with a valid card.",
            "priority": "high",
        },
    )
    assert_status(response, 201)
    testcase = response.json()

    stored = get_testcase_by_id(db, testcase["id"])
    assert stored is not None
    assert stored.project_id == project["id"]
    assert stored.priority == "high"


@pytest.mark.regression
def test_create_invalid_testcase(api, project):
    response = api.post(
        f"/projects/{project['id']}/testcases",
        json={
            "title": "x",
            "description": "ok",
        },
    )
    assert_status(response, 422)


@pytest.mark.regression
def test_create_testcase_for_missing_project(api, primary_user):
    response = api.post(
        "/projects/9999/testcases",
        json={
            "title": "Missing project",
            "description": "This project does not exist.",
        },
    )
    assert_error(response, 404, "not found")


@pytest.mark.functional
def test_list_project_testcases(api, testcase, project):
    response = api.get(f"/projects/{project['id']}/testcases")
    assert_status(response, 200)
    assert response.json()[0]["id"] == testcase["id"]


@pytest.mark.functional
@pytest.mark.database
def test_update_testcase(api, testcase, db):
    response = api.put(
        f"/testcases/{testcase['id']}",
        json={"priority": "critical", "status": "archived"},
    )
    assert_status(response, 200)
    assert response.json()["priority"] == "critical"
    assert response.json()["status"] == "archived"

    stored = get_testcase_by_id(db, testcase["id"])
    assert stored is not None
    assert stored.priority == "critical"


@pytest.mark.regression
def test_delete_testcase(api, testcase, db):
    response = api.delete(f"/testcases/{testcase['id']}")
    assert_status(response, 204)
    assert get_testcase_by_id(db, testcase["id"]) is None
