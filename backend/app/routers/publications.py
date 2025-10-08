from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List
from ..db import get_db
from .. import schemas, models
from ..utils import require_roles

router = APIRouter(
    prefix="/posts",
    tags=["Publications"]
)

# Criar uma nova publicação global.
# Requer perfil de administrador, coordenador ou professor.
@router.post("/", response_model=schemas.PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db),
                current_user: models.User = Depends(require_roles(["teacher", "coordinator", "admin"]))):

    new_post = models.Post(title=post.title, content=post.content, authorId=current_user.id)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

# Listar todas as publicações do sistema.
@router.get("/", response_model=List[schemas.PostResponse])
def get_all_posts(db: Session = Depends(get_db),
                  current_user: models.User = Depends(require_roles(["student", "teacher", "coordinator", "admin"]))):
    
    posts = db.query(models.Post).order_by(models.Post.date.desc()).all()
    return posts

# Editar uma publicação.
# Requer perfil de administrador, coordenador ou professor.
@router.patch("/{post_id}", response_model=schemas.PostResponse)
def update_post(post_id: int, post_update: schemas.PostUpdate, db: Session = Depends(get_db),
                current_user: models.User = Depends(require_roles(["teacher", "coordinator", "admin"]))):
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Publicação não encontrada")

    is_author = db_post.authorId == current_user.id
    is_privileged = current_user.role in [models.UserRole.coordinator, models.UserRole.admin]

    if not is_author and not is_privileged:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Não tem permissão para editar esta publicação")
    
    update_data = post_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_post, key, value)
    
    db.commit()
    db.refresh(db_post)
    return db_post

# Deletar uma publicação.
# Requer perfil de administrador, coordenador ou professor.
@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, db: Session = Depends(get_db),
                current_user: models.User = Depends(require_roles(["teacher", "coordinator", "admin"]))):
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Publicação não encontrada")
    
    is_author = db_post.authorId == current_user.id
    is_privileged = current_user.role in [models.UserRole.coordinator, models.UserRole.admin]

    if not is_author and not is_privileged:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Não tem permissão para deletar esta publicação")

    db.delete(db_post)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)