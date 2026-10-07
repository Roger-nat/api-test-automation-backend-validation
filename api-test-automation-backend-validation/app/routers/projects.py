from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Project, User
from app.schemas import ProjectCreate, ProjectRead, ProjectUpdate

router = APIRouter(prefix="/projects", tags=["Projects"])


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


@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    duplicate = db.scalar(
        select(Project).where(
            Project.owner_id == current_user.id,
            Project.name == payload.name,
        )
    )
    if duplicate:
        raise HTTPException(status_code=409, detail="You already have a project with this name.")

    project = Project(
        name=payload.name,
        description=payload.description,
        owner_id=current_user.id,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("", response_model=list[ProjectRead])
def list_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list(
        db.scalars(
            select(Project)
            .where(Project.owner_id == current_user.id)
            .order_by(Project.id)
        ).all()
    )


@router.get("/{project_id}", response_model=ProjectRead)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _owned_project(db, project_id, current_user.id)


@router.put("/{project_id}", response_model=ProjectRead)
def update_project(
    project_id: int,
    payload: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = _owned_project(db, project_id, current_user.id)

    if payload.name and payload.name != project.name:
        duplicate = db.scalar(
            select(Project).where(
                Project.owner_id == current_user.id,
                Project.name == payload.name,
            )
        )
        if duplicate:
            raise HTTPException(status_code=409, detail="You already have a project with this name.")
        project.name = payload.name

    if payload.description is not None:
        project.description = payload.description

    db.commit()
    db.refresh(project)
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = _owned_project(db, project_id, current_user.id)
    db.delete(project)
    db.commit()
