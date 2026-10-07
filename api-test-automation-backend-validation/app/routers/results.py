from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import TestCase, TestResult, User
from app.schemas import TestResultCreate, TestResultRead

router = APIRouter(tags=["Test Results"])


def _owned_testcase(db: Session, testcase_id: int, owner_id: int) -> TestCase:
    testcase = db.get(TestCase, testcase_id)
    if testcase is None:
        raise HTTPException(status_code=404, detail="Test case not found.")
    if testcase.project.owner_id != owner_id:
        raise HTTPException(status_code=403, detail="You do not have access to this test case.")
    return testcase


@router.post(
    "/testcases/{testcase_id}/results",
    response_model=TestResultRead,
    status_code=status.HTTP_201_CREATED,
)
def create_result(
    testcase_id: int,
    payload: TestResultCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _owned_testcase(db, testcase_id, current_user.id)

    result = TestResult(
        testcase_id=testcase_id,
        status=payload.status,
        execution_time=payload.execution_time,
        notes=payload.notes,
    )
    db.add(result)
    db.commit()
    db.refresh(result)
    return result


@router.get("/testcases/{testcase_id}/results", response_model=list[TestResultRead])
def list_results(
    testcase_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _owned_testcase(db, testcase_id, current_user.id)
    return list(
        db.scalars(
            select(TestResult)
            .where(TestResult.testcase_id == testcase_id)
            .order_by(TestResult.id)
        ).all()
    )
