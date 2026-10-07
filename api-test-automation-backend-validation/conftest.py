from __future__ import annotations

from pathlib import Path
import json

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.dependencies import get_current_user
from app.main import app
from app.database import get_db
from app.models import User
from utils.ai_failure_analyzer import analyze_failure
from utils.api_client import ApiClient
from utils.assertions import assert_status

TEST_DB_URL = "sqlite://"
test_engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


@pytest.fixture()
def db():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db: Session):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture()
def api(client: TestClient):
    return ApiClient(client)


@pytest.fixture()
def primary_user(api: ApiClient):
    payload = {
        "name": "Aarav Mehta",
        "email": "aarav@example.com",
        "password": "StrongPass123",
    }
    response = api.post("/auth/register", json=payload)
    assert_status(response, 201)
    api.login(payload["email"], payload["password"])
    return response.json()


@pytest.fixture()
def second_user(api: ApiClient):
    payload = {
        "name": "Riya Sharma",
        "email": "riya@example.com",
        "password": "StrongPass456",
    }
    response = api.post("/auth/register", json=payload)
    assert_status(response, 201)
    return response.json()


@pytest.fixture()
def second_user_api(api: ApiClient, second_user):
    api.login("riya@example.com", "StrongPass456")
    return api


@pytest.fixture()
def project(api: ApiClient, primary_user):
    response = api.post(
        "/projects",
        json={
            "name": "Mobile Checkout",
            "description": "Regression coverage for checkout workflow",
        },
    )
    assert_status(response, 201)
    return response.json()


@pytest.fixture()
def testcase(api: ApiClient, project):
    response = api.post(
        f"/projects/{project['id']}/testcases",
        json={
            "title": "Valid login",
            "description": "Verify a valid user can authenticate successfully.",
            "priority": "high",
        },
    )
    assert_status(response, 201)
    return response.json()


@pytest.fixture()
def multiple_users(api: ApiClient):
    primary = {
        "name": "Aarav Mehta",
        "email": "aarav@example.com",
        "password": "StrongPass123",
    }
    second = {
        "name": "Riya Sharma",
        "email": "riya@example.com",
        "password": "StrongPass456",
    }
    assert_status(api.post("/auth/register", json=primary), 201)
    assert_status(api.post("/auth/register", json=second), 201)
    api.login(primary["email"], primary["password"])
    return primary, second


def _failure_context(item, call):
    api_client = item.funcargs.get("api")
    exchange = api_client.last_exchange if api_client else None
    traceback_text = getattr(call.excinfo, "exconly", lambda: "")()
    try:
        path = analyze_failure(item.nodeid, exchange, traceback_text)
        return path
    except Exception:
        return None


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        _failure_context(item, call)


def pytest_configure(config):
    for path in (
        Path("reports"),
        Path("artifacts/logs"),
        Path("artifacts/failures"),
        Path("artifacts/failure_analysis"),
    ):
        path.mkdir(parents=True, exist_ok=True)
