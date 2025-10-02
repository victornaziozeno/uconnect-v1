from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime 
from .. import models, schemas
from ..db import get_db
from ..utils import require_roles 

User = models.User 

router = APIRouter(
    prefix="/events",
    tags=["Events"]
)


@router.get("/", response_model=List[schemas.EventResponse])
def list_events(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """Lista todos os eventos com paginação - rota pública para o calendário"""
    events = db.query(models.Event).offset(skip).limit(limit).all()
    return events


@router.get("/{event_id}", response_model=schemas.EventResponse)
def get_event(
    event_id: int, 
    db: Session = Depends(get_db)
):
    """Obtém um evento específico pelo seu ID"""
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    return event


@router.post("/", response_model=schemas.EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(
    event_data: schemas.EventCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles(["admin", "coordinator", "teacher"]))
):
    start_time_str = "00:00:00"
    if event_data.hora:
        start_time_str = event_data.hora.split(" - ")[0]
    
    # Combina a data e a hora em um único objeto datetime
    timestamp_obj = datetime.combine(event_data.date, datetime.strptime(start_time_str, "%H:%M").time())
    
    # Cria o objeto do banco de dados
    new_event_db = models.Event(
        title=event_data.title,
        description=event_data.description,
        timestamp=timestamp_obj, # Salva o timestamp combinado
        academicGroupId=event_data.academicGroupId,
        creatorId=current_user.id
    )

    db.add(new_event_db)
    db.commit()
    db.refresh(new_event_db)
    return new_event_db

@router.put("/{event_id}", response_model=schemas.EventResponse)
def update_event(
    event_id: int,
    event_update: schemas.EventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "coordinator", "teacher"]))
):
    """Atualiza um evento existente - requer permissão"""
    event_query = db.query(models.Event).filter(models.Event.id == event_id)
    db_event = event_query.first()
    
    if not db_event:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    
    # CORREÇÃO DE SEGURANÇA: Regra de permissão adicionada
    # Apenas o criador original do evento ou um 'admin' podem atualizá-lo.
    if db_event.creatorId != current_user.id and current_user.role != models.UserRole.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permissão negada para editar este evento")
    
    update_data = event_update.model_dump(exclude_unset=True)
    event_query.update(update_data, synchronize_session=False)
    
    db.commit()
    db.refresh(db_event)
    return db_event


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "coordinator", "teacher"]))
):
    """Remove um evento - requer permissão"""
    event_query = db.query(models.Event).filter(models.Event.id == event_id)
    db_event = event_query.first()

    if not db_event:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    
    # CORREÇÃO DE SEGURANÇA: Regra de permissão adicionada
    # Apenas o criador original do evento ou um 'admin' podem excluí-lo.
    if db_event.creatorId != current_user.id and current_user.role != models.UserRole.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permissão negada para excluir este evento")
    
    event_query.delete(synchronize_session=False)
    db.commit()
    
    # Retorna uma resposta vazia com status 204, que é a melhor prática para DELETE.
    return Response(status_code=status.HTTP_204_NO_CONTENT)