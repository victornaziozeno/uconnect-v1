from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas, utils
from ..db import get_db

router = APIRouter(prefix="/subchannels", tags=["Subchannels"])
get_current_user = utils.get_current_user


@router.get("/channel/{channel_id}", response_model=List[schemas.Subchannel])
def list_subchannels(channel_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    Lista todos os subcanais de um canal.
    """
    channel = db.query(models.Channel).filter(models.Channel.id == channel_id).first()
    if not channel:
        raise HTTPException(status_code=404, detail="Canal não encontrado")

    subchannels = db.query(models.Subchannel).filter(models.Subchannel.parentChannelId == channel.id).all()
    return subchannels


@router.post("/channel/{channel_id}", response_model=schemas.Subchannel, status_code=status.HTTP_201_CREATED)
def create_subchannel(channel_id: int, data: schemas.SubchannelCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    Cria um subcanal dentro de um canal.
    """
    channel = db.query(models.Channel).filter(models.Channel.id == channel_id).first()
    if not channel:
        raise HTTPException(status_code=404, detail="Canal não encontrado")

    existing = db.query(models.Subchannel).filter(
        models.Subchannel.parentChannelId == channel.id,
        models.Subchannel.name == data.name
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Já existe um subcanal com este nome neste canal")

    new_sub = models.Subchannel(name=data.name, parentChannelId=channel.id)
    db.add(new_sub)
    db.commit()
    db.refresh(new_sub)
    return new_sub


@router.put("/{subchannel_id}", response_model=schemas.Subchannel)
def update_subchannel(subchannel_id: int, data: schemas.SubchannelCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    Edita um subcanal.
    """
    sub = db.query(models.Subchannel).filter(models.Subchannel.id == subchannel_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Subcanal não encontrado")

    channel = db.query(models.Channel).filter(models.Channel.id == sub.parentChannelId).first()
    if not channel:
        raise HTTPException(status_code=404, detail="Canal pai não encontrado")

    if channel.creatorId != current_user.id and current_user.role != "coordenador":
        raise HTTPException(status_code=403, detail="Sem permissão para editar este subcanal")

    sub.name = data.name
    db.commit()
    db.refresh(sub)
    return sub


@router.delete("/{subchannel_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subchannel(subchannel_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    Exclui um subcanal.
    """
    sub = db.query(models.Subchannel).filter(models.Subchannel.id == subchannel_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Subcanal não encontrado")

    channel = db.query(models.Channel).filter(models.Channel.id == sub.parentChannelId).first()
    if channel.creatorId != current_user.id and current_user.role != "coordenador":
        raise HTTPException(status_code=403, detail="Sem permissão para excluir este subcanal")

    db.delete(sub)
    db.commit()
