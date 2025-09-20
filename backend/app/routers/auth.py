from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from ..db import get_db
from .. import models, utils

router = APIRouter(prefix="/auth", tags=["authentication"])

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
async def login(
    login_data: LoginRequest, 
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(
        models.User.registration == login_data.username
    ).first()
    
    if not user or not utils.verify_password(login_data.password, user.passwordHash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Matrícula ou senha incorretas",
        )
    
    if not user.accessStatus:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso inativo",
        )
    
    access_token = utils.create_access_token(data={"sub": user.registration})
    return {"access_token": access_token, "token_type": "bearer"}