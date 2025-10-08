from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timedelta
from ..db import get_db
from .. import models, utils

router = APIRouter(prefix="/auth", tags=["authentication"])

# Define o modelo de dados para a requisição de login.
class LoginRequest(BaseModel):
    registration: str
    password: str

# Define o modelo da resposta de login.
class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_at: datetime

#Login de usuários
@router.post("/login", response_model=TokenResponse)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    
    # Remove espaços em branco da matrícula e da senha.
    user_registration = login_data.registration.strip()
    user_password = login_data.password.strip()

    # Valida se o usuário existe e se a senha está correta.
    # Se a validação falhar, retorna um erro de não autorizado (401).
    user = db.query(models.User).filter(models.User.registration == user_registration).first()

    if not user or not utils.verify_password(user_password, user.passwordHash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Matrícula ou senha incorretas"
        )

    # Valida se o status da conta do usuário é 'ativo'.
    # Se não for, retorna um erro de acesso proibido (403).
    if user.accessStatus != models.AccessStatus.active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Acesso inativo"
        )

    # Cria um novo token de acesso (JWT) e a data de expiração.
    token, expire = utils.create_access_token(data={"sub": user.registration})
    db_session = models.Session(token=token, userId=user.id, startDate=datetime.utcnow(), expirationDate=expire)
    db.add(db_session)
    db.commit()
    
    # Retorna o token de acesso e a data de expiração.
    return {"access_token": token, "token_type": "bearer", "expires_at": expire}

# Encerra a sessão do usuário.
@router.post("/logout")
def logout(token: str = Depends(utils.oauth2_scheme), db: Session = Depends(get_db)):

    # Busca a sessão no banco de dados.
    # Se a sessão for encontrada, a deleta.
    session = db.query(models.Session).filter(models.Session.token == token).first()
    if session:
        db.delete(session)
        db.commit()
    return {"message": "Sessão encerrada"}

# Verifica se uma sessão é válida.
@router.get("/validate")
def validate_session(token: str = Depends(utils.oauth2_scheme), db: Session = Depends(get_db)):

    # Busca a sessão no banco.
    session = db.query(models.Session).filter(models.Session.token == token).first()

    # Se a sessão não existir, retorna erro de sessão inválida.
    # Se a sessão existir, mas estiver expirada, a deleta e retorna erro.
    # Se a sessão for válida, retorna sucesso.
    if not session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sessão inválida")
    if session.expirationDate < datetime.utcnow():
        db.delete(session); db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sessão expirada")
    return {"valid": True, "expires_at": session.expirationDate}
