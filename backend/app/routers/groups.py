from fastapi import APIRouter, Depends, HTTPException, status, Response 
from sqlalchemy.orm import Session
from ..db import get_db
from .. import schemas, models
from ..utils import require_roles

router = APIRouter(
    prefix="/groups",
    tags=["Groups"]
)

# Criar um novo grupo acadêmico.
# Requer perfil de administrador.
@router.post("/", response_model=schemas.AcademicGroupResponse, status_code=status.HTTP_201_CREATED)
def create_group(group: schemas.AcademicGroupCreate, db: Session = Depends(get_db), current_user: models.User = Depends(require_roles(["admin"]))):

    db_group = models.AcademicGroup(**group.dict())
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return db_group

# Listar todos os grupos acadêmicos.
# Requer perfil de administrador ou coordenador.
@router.get("/", response_model=list[schemas.AcademicGroupResponse])
def get_all_groups(db: Session = Depends(get_db), current_user: models.User = Depends(require_roles(["admin", "coordinator"]))):
   
    return db.query(models.AcademicGroup).all()

# Obter os detalhes de um grupo, incluindo a lista de membros.
# Requer perfil de administrador, coordenador ou professor.
@router.get("/{group_id}", response_model=schemas.AcademicGroupDetailResponse)
def get_group_details(group_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(require_roles(["admin", "coordinator", "teacher"]))):
   
    db_group = db.query(models.AcademicGroup).filter(models.AcademicGroup.id == group_id).first()
    if not db_group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grupo não encontrado")
    return db_group

# Atualizar um grupo acadêmico.
# Requer perfil de administrador.
@router.patch("/{group_id}", response_model=schemas.AcademicGroupResponse)
def update_group(group_id: int, group_update: schemas.AcademicGroupUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(require_roles(["admin"]))):

    db_group = db.query(models.AcademicGroup).filter(models.AcademicGroup.id == group_id).first()
    if not db_group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grupo não encontrado")
    
    update_data = group_update.dict(exclude_unset=True) 
    for key, value in update_data.items():
        setattr(db_group, key, value)
        
    db.commit()
    db.refresh(db_group)
    return db_group

# Deletar uma grupo acadêmico.
# Requer perfil de administrador.
@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_group(group_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(require_roles(["admin"]))):

    db_group = db.query(models.AcademicGroup).filter(models.AcademicGroup.id == group_id).first()
    if not db_group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grupo não encontrado")
    
    db.delete(db_group)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# Adicionar um utilizador a um grupo.
# Requer perfil de administrador ou coordenador.
@router.post("/{group_id}/users/{user_id}", status_code=status.HTTP_201_CREATED, response_model=schemas.AcademicGroupDetailResponse)
def add_user_to_group(group_id: int, user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(require_roles(["admin", "coordinator"]))):

    db_group = db.query(models.AcademicGroup).filter(models.AcademicGroup.id == group_id).first()
    if not db_group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grupo não encontrado")
    
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilizador não encontrado")

    if db_user in db_group.users:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Utilizador já pertence a este grupo")

    db_group.users.append(db_user)
    db.commit()
    db.refresh(db_group)
    return db_group

# Remove um utilizador de um grupo.
# Requer perfil de administrador ou coordenador.
@router.delete("/{group_id}/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_user_from_group(group_id: int, user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(require_roles(["admin", "coordinator"]))):
    db_group = db.query(models.AcademicGroup).filter(models.AcademicGroup.id == group_id).first()
    if not db_group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grupo não encontrado")
    
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilizador não encontrado")

    if db_user not in db_group.users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilizador não pertence a este grupo")

    db_group.users.remove(db_user)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)