from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Project, TestCase, User
from app.schemas import TestCaseCreate, TestCaseRead, TestCaseUpdate

router = APIRouter(tags=["Test Cases"])


def _owned_project(db: Session, project_id: int, owner_id: int) -> Project:
    project = db.scalar(
        select(Project).where(
            Project.id == project_id,
            Project.owner_id == owner_id,
        )
    )
    if project is None:
        exists = db.get(Project, project_id)
        if exists:
            raise HTTPException(status_code=403, detail="You do not have access to this project.")
        raise HTTPException(status_code=404, detail="Project not found.")
    return project


def _owned_testcase(db: Session, testcase_id: int, owner_id: int) -> TestCase:
    testcase = db.get(TestCase, testcase_id)
    if testcase is None:
        raise HTTPException(status_code=404, detail="Test case not found.")
    if testcase.project.owner_id != owner_id:
        raise HTTPException(status_code=403, detail="You do not have access to this test case.")
    return testcase


@router.post(
    "/projects/{project_id}/testcases",
    response_model=TestCaseRead,
    status_code=status.HTTP_201_CREATED,
)
def create_testcase(
    project_id: int,
    payload: TestCaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _owned_project(db, project_id, current_user.id)

    testcase = TestCase(
        project_id=project_id,
        title=payload.title,
        description=payload.description,
        priority=payload.priority,
    )
    db.add(testcase)
    db.commit()
    db.refresh(testcase)
    return testcase


@router.get("/projects/{project_id}/testcases", response_model=list[TestCaseRead])
def list_testcases(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _owned_project(db, project_id, current_user.id)
    return list(
        db.scalars(
            select(TestCase)
            .where(TestCase.project_id == project_id)
            .order_by(TestCase.id)
        ).all()
    )


@router.get("/testcases/{testcase_id}", response_model=TestCaseRead)
def get_testcase(
    testcase_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _owned_testcase(db, testcase_id, current_user.id)


@router.put("/testcases/{testcase_id}", response_model=TestCaseRead)
def update_testcase(
    testcase_id: int,
    payload: TestCaseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    testcase = _owned_testcase(db, testcase_id, current_user.id)

    if payload.title is not None:
        testcase.title = payload.title
    if payload.description is not None:
        testcase.description = payload.description
    if payload.priority is not None:
        testcase.priority = payload.priority
    if payload.status is not None:
        testcase.status = payload.status

    db.commit()
    db.refresh(testcase)
    return testcase


@router.delete("/testcases/{testcase_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_testcase(
    testcase_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    testcase = _owned_testcase(db, testcase_id, current_user.id)
    db.delete(testcase)
    db.commit()
