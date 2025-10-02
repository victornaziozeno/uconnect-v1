from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..db import get_db
from .. import models, schemas, utils
from datetime import datetime

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.registration == user.registration).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuário já cadastrado")
    hashed_password = utils.get_password_hash(user.password)
    db_user = models.User(
        registration=user.registration,
        name=user.name,
        email=user.email,
        passwordHash=hashed_password,
        role=user.role,
        accessStatus=models.AccessStatus.active
    )
    db.add(db_user); db.commit(); db.refresh(db_user)
    return db_user

@router.get("/", response_model=list[schemas.UserResponse])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
               current_user: models.User = Depends(utils.get_current_active_user)):
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users

@router.get("/me", response_model=schemas.UserResponse)
def read_own_profile(current_user: models.User = Depends(utils.get_current_active_user)):
    return current_user

@router.put("/me", response_model=schemas.UserResponse)
def update_profile(user_update: schemas.UserUpdate, db: Session = Depends(get_db),
                   current_user: models.User = Depends(utils.get_current_active_user)):
    update_data = user_update.dict(exclude_unset=True)
    update_data.pop("role", None)
    update_data.pop("accessStatus", None)
    for field, value in update_data.items():
        setattr(current_user, field, value)
    db.commit(); db.refresh(current_user)
    return current_user

@router.put("/{user_id}", response_model=schemas.UserResponse)
def update_user(user_id: int, user_update: schemas.UserUpdate, db: Session = Depends(get_db),
                current_user: models.User = Depends(utils.require_roles(["admin", "contract"]))):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)
    db.commit(); db.refresh(db_user)
    return db_user

@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db),
                current_user: models.User = Depends(utils.require_roles(["admin", "contract"]))):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    db.query(models.Session).filter(models.Session.userId == db_user.id).delete()
    db.delete(db_user)
    db.commit()
    return {"message": "Usuário deletado com sucesso"}
