from fastapi import APIRouter, Depends, HTTPException, status, Response, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..db import get_db
from .. import schemas, models
from ..utils import require_roles, get_current_active_user
from .notifications import notify_new_announcement

router = APIRouter(prefix="/posts", tags=["Publications"])

@router.post("/", response_model=schemas.PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    post: schemas.PostCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles(["teacher", "coordinator", "admin"]))
):
    new_post = models.Post(
        title=post.title,
        content=post.content,
        type=post.type,
        authorId=current_user.id
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    
    await notify_new_announcement(new_post.id, post.title, current_user.name, db)
    
    return new_post

@router.get("/", response_model=List[schemas.PostResponse])
def get_all_posts(
    post_type: Optional[str] = Query(None, description="Filtrar por tipo: announcement ou notice"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    query = db.query(models.Post)
    
    if post_type:
        try:
            type_enum = models.PostType(post_type)
            query = query.filter(models.Post.type == type_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tipo inválido. Use 'announcement' ou 'notice'"
            )
    
    posts = query.order_by(models.Post.date.desc()).offset(skip).limit(limit).all()
    return posts

@router.get("/{post_id}", response_model=schemas.PostResponse)
def get_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Publicação não encontrada"
        )
    return post

@router.patch("/{post_id}", response_model=schemas.PostResponse)
def update_post(
    post_id: int,
    post_update: schemas.PostUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles(["teacher", "coordinator", "admin"]))
):
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not db_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Publicação não encontrada"
        )

    is_author = db_post.authorId == current_user.id
    is_privileged = current_user.role in [models.UserRole.coordinator, models.UserRole.admin]

    if not is_author and not is_privileged:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para editar"
        )
    
    update_data = post_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_post, key, value)
    
    db.commit()
    db.refresh(db_post)
    return db_post

@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles(["teacher", "coordinator", "admin"]))
):
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not db_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Publicação não encontrada"
        )
    
    is_author = db_post.authorId == current_user.id
    is_privileged = current_user.role in [models.UserRole.coordinator, models.UserRole.admin]

    if not is_author and not is_privileged:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para deletar"
        )

    db.delete(db_post)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.get("/stats/count")
def get_posts_count(
    post_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    query = db.query(models.Post)
    
    if post_type:
        try:
            type_enum = models.PostType(post_type)
            query = query.filter(models.Post.type == type_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tipo inválido"
            )
    
    total = query.count()
    announcements = query.filter(models.Post.type == models.PostType.announcement).count()
    notices = query.filter(models.Post.type == models.PostType.notice).count()
    
    return {
        "total": total,
        "announcements": announcements,
        "notices": notices
    }
