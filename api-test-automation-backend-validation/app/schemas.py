from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    email: EmailStr | None = None


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    role: str
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ProjectCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    description: str | None = Field(default=None, max_length=500)


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    description: str | None = Field(default=None, max_length=500)


class ProjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    owner_id: int
    created_at: datetime


class TestCaseCreate(BaseModel):
    title: str = Field(min_length=3, max_length=160)
    description: str = Field(min_length=5, max_length=1000)
    priority: str = Field(default="medium", pattern="^(low|medium|high|critical)$")


class TestCaseUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=160)
    description: str | None = Field(default=None, min_length=5, max_length=1000)
    priority: str | None = Field(default=None, pattern="^(low|medium|high|critical)$")
    status: str | None = Field(default=None, pattern="^(active|archived)$")


class TestCaseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    title: str
    description: str
    priority: str
    status: str
    created_at: datetime


class TestResultCreate(BaseModel):
    status: str = Field(pattern="^(passed|failed|blocked|skipped)$")
    execution_time: float = Field(ge=0)
    notes: str | None = Field(default=None, max_length=1000)


class TestResultRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    testcase_id: int
    status: str
    execution_time: float
    notes: str | None
    created_at: datetime
