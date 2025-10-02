from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timedelta
from ..db import get_db
from .. import models, utils

router = APIRouter(prefix="/auth", tags=["authentication"])

class LoginRequest(BaseModel):
    registration: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_at: datetime

@router.post("/login", response_model=TokenResponse)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    
    user_registration = login_data.registration.strip()
    user_password = login_data.password.strip()

    user = db.query(models.User).filter(models.User.registration == user_registration).first()

    if not user or not utils.verify_password(user_password, user.passwordHash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Matrícula ou senha incorretas"
        )

    if user.accessStatus != models.AccessStatus.active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Acesso inativo"
        )

    token, expire = utils.create_access_token(data={"sub": user.registration})
    db_session = models.Session(token=token, userId=user.id, startDate=datetime.utcnow(), expirationDate=expire)
    db.add(db_session)
    db.commit()

    return {"access_token": token, "token_type": "bearer", "expires_at": expire}

@router.post("/logout")
def logout(token: str = Depends(utils.oauth2_scheme), db: Session = Depends(get_db)):
    session = db.query(models.Session).filter(models.Session.token == token).first()
    if session:
        db.delete(session)
        db.commit()
    return {"message": "Sessão encerrada"}

@router.get("/validate")
def validate_session(token: str = Depends(utils.oauth2_scheme), db: Session = Depends(get_db)):
    session = db.query(models.Session).filter(models.Session.token == token).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sessão inválida")
    if session.expirationDate < datetime.utcnow():
        db.delete(session); db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sessão expirada")
    return {"valid": True, "expires_at": session.expirationDate}
