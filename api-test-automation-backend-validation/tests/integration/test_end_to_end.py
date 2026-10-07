import pytest

from utils.assertions import assert_status
from utils.db_validator import project_by_id, result_by_id, get_testcase_by_id


@pytest.mark.integration
@pytest.mark.smoke
@pytest.mark.database
def test_complete_qa_management_workflow(api, db):
    register = api.post(
        "/auth/register",
        json={
            "name": "Workflow User",
            "email": "workflow@example.com",
            "password": "WorkflowPass123",
        },
    )
    assert_status(register, 201)

    login = api.login("workflow@example.com", "WorkflowPass123")
    assert_status(login, 200)

    project_response = api.post(
        "/projects",
        json={
            "name": "Checkout Release",
            "description": "Release validation project",
        },
    )
    assert_status(project_response, 201)
    project = project_response.json()

    testcase_response = api.post(
        f"/projects/{project['id']}/testcases",
        json={
            "title": "Successful checkout",
            "description": "Verify checkout completes successfully.",
            "priority": "high",
        },
    )
    assert_status(testcase_response, 201)
    testcase = testcase_response.json()

    result_response = api.post(
        f"/testcases/{testcase['id']}/results",
        json={
            "status": "passed",
            "execution_time": 2.31,
            "notes": "Release validation passed.",
        },
    )
    assert_status(result_response, 201)
    result = result_response.json()

    assert project_by_id(db, project["id"]) is not None
    assert get_testcase_by_id(db, testcase["id"]) is not None
    assert result_by_id(db, result["id"]) is not None


@pytest.mark.integration
@pytest.mark.regression
def test_failed_login_does_not_grant_protected_access(api, primary_user):
    response = api.login("aarav@example.com", "incorrect-password")
    assert_status(response, 401)

    protected = api.get("/auth/me")
    assert_status(protected, 401)
