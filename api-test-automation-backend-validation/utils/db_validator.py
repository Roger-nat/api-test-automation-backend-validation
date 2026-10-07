from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Project, TestCase, TestResult, User


def user_by_id(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)


def project_by_id(db: Session, project_id: int) -> Project | None:
    return db.get(Project, project_id)


def get_testcase_by_id(db: Session, testcase_id: int) -> TestCase | None:
    return db.get(TestCase, testcase_id)


def result_by_id(db: Session, result_id: int) -> TestResult | None:
    return db.get(TestResult, result_id)


def project_count_for_owner(db: Session, owner_id: int) -> int:
    return len(db.scalars(select(Project).where(Project.owner_id == owner_id)).all())
