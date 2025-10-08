# backend/app/dependencies.py

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from . import models
from .db import get_db
from .utils import decode_token # Importa a nova função

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_token(token)
    if payload is None:
        raise credentials_exception

    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    user = db.query(models.User).filter(models.User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(current_user: models.User = Depends(get_current_user)) -> models.User:
    if current_user.accessStatus != models.AccessStatus.active:
        raise HTTPException(status_code=400, detail="Usuário inativo")
    return current_user


def require_roles(allowed_roles: list[str]):
    async def role_checker(current_user: models.User = Depends(get_current_active_user)):
        if current_user.role.value not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permissão negada. Acesso não autorizado."
            )
        return current_user
    return role_checker