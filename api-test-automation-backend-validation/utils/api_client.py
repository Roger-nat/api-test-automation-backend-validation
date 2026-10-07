from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from fastapi.testclient import TestClient

from utils.logger import get_logger

LOGGER = get_logger(__name__)


@dataclass
class Exchange:
    method: str
    url: str
    request_body: Any
    status_code: int
    response_body: Any


class ApiClient:
    """Small reusable wrapper around FastAPI TestClient used by the test suite."""

    def __init__(self, client: TestClient):
        self.client = client
        self.token: str | None = None
        self.last_exchange: Exchange | None = None

    def _headers(self, headers: dict[str, str] | None = None) -> dict[str, str]:
        merged = dict(headers or {})
        if self.token:
            merged["Authorization"] = f"Bearer {self.token}"
        return merged

    def _record(self, method: str, path: str, body: Any, response):
        try:
            response_body = response.json()
        except ValueError:
            response_body = response.text

        self.last_exchange = Exchange(
            method=method,
            url=path,
            request_body=body,
            status_code=response.status_code,
            response_body=response_body,
        )

        LOGGER.info("%s %s -> %s", method, path, response.status_code)
        return response

    def get(self, path: str, **kwargs):
        response = self.client.get(path, headers=self._headers(kwargs.pop("headers", None)), **kwargs)
        return self._record("GET", path, None, response)

    def post(self, path: str, json: Any = None, data: Any = None, **kwargs):
        response = self.client.post(
            path,
            json=json,
            data=data,
            headers=self._headers(kwargs.pop("headers", None)),
            **kwargs,
        )
        return self._record("POST", path, json if json is not None else data, response)

    def put(self, path: str, json: Any = None, **kwargs):
        response = self.client.put(
            path,
            json=json,
            headers=self._headers(kwargs.pop("headers", None)),
            **kwargs,
        )
        return self._record("PUT", path, json, response)

    def delete(self, path: str, **kwargs):
        response = self.client.delete(
            path,
            headers=self._headers(kwargs.pop("headers", None)),
            **kwargs,
        )
        return self._record("DELETE", path, None, response)

    def login(self, email: str, password: str):
        # A failed login must never leave a previous bearer token active.
        self.token = None
        response = self.post(
            "/auth/login",
            data={"username": email, "password": password},
        )
        if response.status_code == 200:
            self.token = response.json()["access_token"]
        return response
