from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas, utils
from ..db import get_db

router = APIRouter(prefix="/channels", tags=["Channels"])
get_current_user = utils.get_current_user


@router.get("/", response_model=List[schemas.Channel])
def list_channels(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Lista todos os canais disponíveis.
    """
    return db.query(models.Channel).all()


@router.post("/", response_model=schemas.Channel, status_code=status.HTTP_201_CREATED)
def create_channel(
    data: schemas.ChannelCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Cria um novo canal.
    """
    existing_channel = db.query(models.Channel).filter(
        models.Channel.name == data.name
    ).first()

    if existing_channel:
        raise HTTPException(status_code=400, detail="Canal já existe")

    new_channel = models.Channel(
        name=data.name,
        classGroup=data.classGroup,
        description=data.description if hasattr(data, "description") else None,
        creatorId=current_user.id
    )
    db.add(new_channel)
    db.commit()
    db.refresh(new_channel)
    return new_channel


@router.put("/{channel_id}", response_model=schemas.Channel)
def update_channel(
    channel_id: int,
    data: schemas.ChannelCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Edita um canal existente. Apenas criador ou coordenador pode editar.
    """
    channel = db.query(models.Channel).filter(models.Channel.id == channel_id).first()
    if not channel:
        raise HTTPException(status_code=404, detail="Canal não encontrado")

    if channel.creatorId != current_user.id and current_user.role != "coordenador":
        raise HTTPException(status_code=403, detail="Sem permissão para editar este canal")

    channel.name = data.name
    channel.classGroup = data.classGroup
    if hasattr(data, "description"):
        channel.description = data.description

    db.commit()
    db.refresh(channel)
    return channel


@router.delete("/{channel_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_channel(
    channel_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Exclui um canal. Apenas criador ou coordenador pode excluir.
    """
    channel = db.query(models.Channel).filter(models.Channel.id == channel_id).first()
    if not channel:
        raise HTTPException(status_code=404, detail="Canal não encontrado")

    if channel.creatorId != current_user.id and current_user.role != "coordenador":
        raise HTTPException(status_code=403, detail="Sem permissão para excluir este canal")

    db.delete(channel)
    db.commit()
    