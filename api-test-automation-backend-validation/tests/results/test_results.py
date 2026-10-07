import pytest

from utils.assertions import assert_status
from utils.db_validator import result_by_id


@pytest.mark.functional
@pytest.mark.database
def test_submit_passing_result(api, testcase, db):
    response = api.post(
        f"/testcases/{testcase['id']}/results",
        json={
            "status": "passed",
            "execution_time": 1.42,
            "notes": "Regression run completed successfully.",
        },
    )
    assert_status(response, 201)
    result = response.json()

    stored = result_by_id(db, result["id"])
    assert stored is not None
    assert stored.status == "passed"


@pytest.mark.functional
def test_submit_failing_result(api, testcase):
    response = api.post(
        f"/testcases/{testcase['id']}/results",
        json={
            "status": "failed",
            "execution_time": 2.05,
            "notes": "Expected checkout confirmation, received validation error.",
        },
    )
    assert_status(response, 201)
    assert response.json()["status"] == "failed"


@pytest.mark.regression
def test_get_execution_history(api, testcase):
    for status in ("passed", "failed"):
        response = api.post(
            f"/testcases/{testcase['id']}/results",
            json={
                "status": status,
                "execution_time": 1.0,
                "notes": f"{status} execution",
            },
        )
        assert_status(response, 201)

    response = api.get(f"/testcases/{testcase['id']}/results")
    assert_status(response, 200)
    assert [item["status"] for item in response.json()] == ["passed", "failed"]
