from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..db import get_db
from .. import models, schemas, utils
from datetime import datetime

router = APIRouter(prefix="/users", tags=["users"])

# Cadatro de usuários.
# Retirado validação de papeis (admin).
# TODO: Colocar validação de papeis no parametrizador de acesso. 
@router.post("/", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):

    # Verifica se já existe um usuário.
    # Se a matrícula já existe, retorna um erro 400.
    existing_user = db.query(models.User).filter(models.User.registration == user.registration).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuário já cadastrado")

    # Criptografa a senha antes de salvar.
    hashed_password = utils.get_password_hash(user.password)

    db_user = models.User(
        registration=user.registration,
        name=user.name,
        email=user.email,
        passwordHash=hashed_password,
        role=user.role,
        accessStatus=models.AccessStatus.active
    )

    # Adiciona o novo usuário.
    db.add(db_user); db.commit(); db.refresh(db_user)
    return db_user

# Lista todos os usuários.
# Requer perfil de administrador.
@router.get("/", response_model=list[schemas.UserResponse])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
               current_user: models.User = Depends(utils.require_roles(["admin"]))):

    # Busca todos os usuários.
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users

# Visualizar próprio perfil.
# Requer usuário com status ativo.
@router.get("/me", response_model=schemas.UserResponse)
def read_own_profile(current_user: models.User = Depends(utils.get_current_active_user)):
    return current_user

# Atualizar próprio perfil.
# Requer usuário com status ativo.
@router.put("/me", response_model=schemas.UserResponse)
def update_profile(user_update: schemas.UserUpdate, db: Session = Depends(get_db),
                   current_user: models.User = Depends(utils.get_current_active_user)):
    update_data = user_update.dict(exclude_unset=True)
    update_data.pop("role", None)
    update_data.pop("accessStatus", None)

    # Atualiza o objeto do usuário.
    for field, value in update_data.items():
        setattr(current_user, field, value)

    # Salva as alterações no banco de dados.
    db.commit(); db.refresh(current_user)
    return current_user

# Atualizar outros usuários.
# Requer perfil de administrador.
@router.put("/{user_id}", response_model=schemas.UserResponse)
def update_user(user_id: int, user_update: schemas.UserUpdate, db: Session = Depends(get_db),
                current_user: models.User = Depends(utils.require_roles(["admin"]))):

    # Busca o usuário pelo ID.
    # Retorna um erro 404 se o usuário não for encontrado.
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    update_data = user_update.dict(exclude_unset=True)

    # Atualiza o objeto do usuário.
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    # Salva as alterações no banco.
    db.commit(); db.refresh(db_user)
    return db_user

# Deletar um usuário.
# Requer perfil de administrador.
@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db),
                current_user: models.User = Depends(utils.require_roles(["admin"]))):
    
    # Busca o usuário pelo ID.
    # Retorna um erro 404 se o usuário não for encontrado.
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    # Deleta as sessões ativas do usuário.
    db.query(models.Session).filter(models.Session.userId == db_user.id).delete()

    # Deleta o usuário e salva alterações.
    db.delete(db_user)
    db.commit()
    return {"message": "Usuário deletado com sucesso"}

# Atualizar o status de acesso de um usuário (active, inactive, suspended).
# Requer perfil de administrador.
@router.patch("/{user_id}/status", response_model=schemas.UserResponse)
def update_user_status(user_id: int, status_update: schemas.UserStatusUpdate, db: Session = Depends(get_db),
                       current_user: models.User = Depends(utils.require_roles(["admin"]))): # <<< CORREÇÃO AQUI
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    if db_user.id == current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Não é permitido alterar o próprio status por esta rota.")

    db_user.accessStatus = status_update.accessStatus
    db.commit()
    db.refresh(db_user)
    return db_user

# Atualizar o perfil (role) de um usuário.
# Requer perfil de administrador ou coordenador.
@router.patch("/{user_id}/role", response_model=schemas.UserResponse)
def update_user_role(user_id: int, role_update: schemas.UserRoleUpdate, db: Session = Depends(get_db),
                     current_user: models.User = Depends(utils.require_roles(["admin", "coordinator"]))): # <<< CORREÇÃO AQUI

    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    if db_user.id == current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Não é permitido alterar o próprio papel.")
    if db_user.role == models.UserRole.admin: # Usar o Enum é mais seguro que a string 'admin'
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Não é permitido alterar o papel de um administrador.")

    # Valida a lista completa de papéis
    valid_roles = [role.value for role in models.UserRole]
    if role_update.role not in valid_roles:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"O papel '{role_update.role}' não é válido.")

    if current_user.role == models.UserRole.coordinator:
        if role_update.role in [models.UserRole.admin.value, models.UserRole.coordinator.value]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Coordenadores não têm permissão para atribuir papéis de administrador ou coordenador."
            )
    
    db_user.role = role_update.role
    db.commit()
    db.refresh(db_user)
    return db_user
    