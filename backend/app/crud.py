from sqlalchemy.orm import Session
from . import models, schemas
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _normalize_bcrypt_password(password: str) -> str:
    password_bytes = password.encode("utf-8")
    safe_bytes = password_bytes[:72]
    return safe_bytes.decode("utf-8", errors="ignore")

# User CRUD
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    # Bcrypt has a strict 72-byte input limit (bytes, not characters)
    password_to_hash = _normalize_bcrypt_password(user.password)
    hashed_password = pwd_context.hash(password_to_hash)
    db_user = models.User(
        name=user.name,
        email=user.email,
        password=hashed_password,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def verify_password(plain_password, hashed_password):
    password_to_verify = _normalize_bcrypt_password(plain_password)
    return pwd_context.verify(password_to_verify, hashed_password)

# Project CRUD
def get_projects(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Project).offset(skip).limit(limit).all()

def get_project(db: Session, project_id: int):
    return db.query(models.Project).filter(models.Project.id == project_id).first()

def create_project(db: Session, project: schemas.ProjectCreate, owner_id: int):
    db_project = models.Project(**project.dict(), owner_id=owner_id)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

def update_project(db: Session, project_id: int, project_update: dict):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if db_project:
        for key, value in project_update.items():
            if value is not None:
                setattr(db_project, key, value)
        db.commit()
        db.refresh(db_project)
    return db_project

def delete_project(db: Session, project_id: int):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if db_project:
        db.delete(db_project)
        db.commit()
        return True
    return False

def add_project_member(db: Session, project_id: int, user_id: int):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if db_project and user_id not in db_project.members:
        # Properly update the array to trigger SQLAlchemy change detection
        db_project.members = db_project.members + [user_id]
        db.commit()
        db.refresh(db_project)
    return db_project

def remove_project_member(db: Session, project_id: int, user_id: int):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if db_project and user_id in db_project.members:
        # Properly update the array to trigger SQLAlchemy change detection
        db_project.members = [m for m in db_project.members if m != user_id]
        # Unassign tasks from the removed member
        tasks = db.query(models.Task).filter(
            models.Task.project_id == project_id,
            models.Task.assigned_to == user_id
        ).all()
        for task in tasks:
            task.assigned_to = None
        db.commit()
        db.refresh(db_project)
    return db_project

# Task CRUD
def get_tasks(db: Session, skip: int = 0, limit: int = 100, project_id: int = None):
    query = db.query(models.Task)
    if project_id:
        query = query.filter(models.Task.project_id == project_id)
    return query.offset(skip).limit(limit).all()

def get_task(db: Session, task_id: int):
    return db.query(models.Task).filter(models.Task.id == task_id).first()

def create_task(db: Session, task: schemas.TaskCreate):
    db_task = models.Task(**task.dict())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def update_task(db: Session, task_id: int, task_update: schemas.TaskUpdate):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task:
        update_data = task_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_task, key, value)
        db.commit()
        db.refresh(db_task)
    return db_task

def delete_task(db: Session, task_id: int):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task:
        db.delete(db_task)
        db.commit()
        return True
    return False