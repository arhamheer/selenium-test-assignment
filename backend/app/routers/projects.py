from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas, models
from ..database import get_db
from ..auth import get_current_user

router = APIRouter(
    prefix="/projects",
    tags=["projects"]
)

@router.post("/", response_model=schemas.Project)
def create_project(
    project: schemas.ProjectCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Create project with current user as owner
    return crud.create_project(db=db, project=project, owner_id=current_user.id)

@router.get("/", response_model=List[schemas.Project])
def read_projects(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Return only projects where user is owner or member
    projects = crud.get_projects(db, skip=skip, limit=limit)
    return [p for p in projects if p.owner_id == current_user.id or current_user.id in p.members]

@router.get("/{project_id}", response_model=schemas.Project)
def read_project(
    project_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_project = crud.get_project(db, project_id=project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if user is owner or member
    if db_project.owner_id != current_user.id and current_user.id not in db_project.members:
        raise HTTPException(status_code=403, detail="Not authorized to view this project")
    
    return db_project

@router.post("/{project_id}/members/{user_id}", response_model=schemas.Project)
def add_project_member(
    project_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_project = crud.get_project(db, project_id=project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Only owner can add members
    if db_project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only owner can add members")
    
    # Check if user exists
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return crud.add_project_member(db, project_id, user_id)

@router.delete("/{project_id}/members/{user_id}", response_model=schemas.Project)
def remove_project_member(
    project_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_project = crud.get_project(db, project_id=project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Only owner can remove members
    if db_project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only owner can remove members")
    
    return crud.remove_project_member(db, project_id, user_id)