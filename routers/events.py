from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from ..db import get_db
from ..models import Event, User
from ..schemas import EventCreate, EventUpdate, EventResponse
from ..dependencies import get_current_user, require_roles

router = APIRouter(prefix="/events", tags=["events"])

@router.get("/", response_model=List[EventResponse])
def list_events(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Lista todos os eventos - rota pública para o calendário"""
    events = db.query(Event).offset(skip).limit(limit).all()
    return events

@router.get("/{event_id}", response_model=EventResponse)
def get_event(
    event_id: int,
    db: Session = Depends(get_db)
):
    """Obtém um evento específico"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    return event

@router.post("/", response_model=EventResponse)
def create_event(
    event: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "coordinator", "teacher"]))
):
    """Cria um novo evento - requer permissão"""
    new_event = Event(
        **event.model_dump(),
        creatorId=current_user.id
    )
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    return new_event

@router.put("/{event_id}", response_model=EventResponse)
def update_event(
    event_id: int,
    event_update: EventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "coordinator", "teacher"]))
):
    """Atualiza um evento existente"""
    db_event = db.query(Event).filter(Event.id == event_id).first()
    if not db_event:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    
    # Update only provided fields
    update_data = event_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_event, field, value)
    
    db.commit()
    db.refresh(db_event)
    return db_event

@router.delete("/{event_id}")
def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "coordinator"]))
):
    """Remove um evento"""
    db_event = db.query(Event).filter(Event.id == event_id).first()
    if not db_event:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    
    db.delete(db_event)
    db.commit()
    return {"message": "Evento removido com sucesso"}
