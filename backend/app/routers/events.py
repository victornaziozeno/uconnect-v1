from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, time as dt_time
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
    
    # Converter time objects para strings
    result = []
    for event in events:
        start_time_str = None
        end_time_str = None
        
        if event.startTime:
            start_time_str = event.startTime.strftime("%H:%M:%S") if hasattr(event.startTime, 'strftime') else str(event.startTime)
        
        if event.endTime:
            end_time_str = event.endTime.strftime("%H:%M:%S") if hasattr(event.endTime, 'strftime') else str(event.endTime)
        
        event_dict = {
            "id": event.id,
            "title": event.title,
            "description": event.description,
            "timestamp": event.timestamp,
            "eventDate": event.eventDate,
            "startTime": start_time_str,
            "endTime": end_time_str,
            "academicGroupId": event.academicGroupId,
            "creatorId": event.creatorId,
        }
        result.append(event_dict)
    
    return result


@router.get("/{event_id}", response_model=schemas.EventResponse)
def get_event(
    event_id: int, 
    db: Session = Depends(get_db)
):
    """Obtém um evento específico pelo seu ID"""
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    
    # Converter time objects para strings
    return {
        "id": event.id,
        "title": event.title,
        "description": event.description,
        "timestamp": event.timestamp,
        "eventDate": event.eventDate,
        "startTime": str(event.startTime) if event.startTime else None,
        "endTime": str(event.endTime) if event.endTime else None,
        "academicGroupId": event.academicGroupId,
        "creatorId": event.creatorId,
    }


@router.post("/", response_model=schemas.EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(
    event_data: schemas.EventCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles(["admin", "coordinator", "teacher"]))
):
    """Cria um novo evento"""
    
    # Processar hora (formato: "HH:MM" ou "HH:MM - HH:MM")
    start_time = None
    end_time = None
    
    if event_data.hora:
        hora_parts = event_data.hora.split(" - ")
        try:
            start_time = datetime.strptime(hora_parts[0].strip(), "%H:%M").time()
            if len(hora_parts) > 1:
                end_time = datetime.strptime(hora_parts[1].strip(), "%H:%M").time()
        except ValueError:
            raise HTTPException(
                status_code=400, 
                detail="Formato de hora inválido. Use HH:MM ou HH:MM - HH:MM"
            )
    
    # Criar timestamp completo (para ordenação e auditoria)
    if start_time:
        timestamp_obj = datetime.combine(event_data.date, start_time)
    else:
        timestamp_obj = datetime.combine(event_data.date, dt_time(0, 0))
    
    # Criar evento
    new_event_db = models.Event(
        title=event_data.title,
        description=event_data.description,
        timestamp=timestamp_obj,
        eventDate=event_data.date,
        startTime=start_time,
        endTime=end_time,
        academicGroupId=event_data.academicGroupId or event_data.local,
        creatorId=current_user.id
    )

    db.add(new_event_db)
    db.commit()
    db.refresh(new_event_db)
    
    # Converter time objects para strings
    return {
        "id": new_event_db.id,
        "title": new_event_db.title,
        "description": new_event_db.description,
        "timestamp": new_event_db.timestamp,
        "eventDate": new_event_db.eventDate,
        "startTime": str(new_event_db.startTime) if new_event_db.startTime else None,
        "endTime": str(new_event_db.endTime) if new_event_db.endTime else None,
        "academicGroupId": new_event_db.academicGroupId,
        "creatorId": new_event_db.creatorId,
    }


@router.put("/{event_id}", response_model=schemas.EventResponse)
def update_event(
    event_id: int,
    event_update: schemas.EventCreate,  # Mudou de EventUpdate para EventCreate
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "coordinator", "teacher"]))
):
    """Atualiza um evento existente - requer permissão"""
    event_query = db.query(models.Event).filter(models.Event.id == event_id)
    db_event = event_query.first()
    
    if not db_event:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    
    # Verificar permissão
    if db_event.creatorId != current_user.id and current_user.role != models.UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Permissão negada para editar este evento"
        )
    
    # Processar hora (formato: "HH:MM" ou "HH:MM - HH:MM")
    start_time = None
    end_time = None
    
    if event_update.hora:
        hora_parts = event_update.hora.split(" - ")
        try:
            start_time = datetime.strptime(hora_parts[0].strip(), "%H:%M").time()
            if len(hora_parts) > 1:
                end_time = datetime.strptime(hora_parts[1].strip(), "%H:%M").time()
        except ValueError:
            raise HTTPException(
                status_code=400, 
                detail="Formato de hora inválido. Use HH:MM ou HH:MM - HH:MM"
            )
    
    # Criar timestamp completo
    if start_time:
        timestamp_obj = datetime.combine(event_update.date, start_time)
    else:
        timestamp_obj = datetime.combine(event_update.date, dt_time(0, 0))
    
    # Atualizar evento
    db_event.title = event_update.title
    db_event.description = event_update.description
    db_event.timestamp = timestamp_obj
    db_event.eventDate = event_update.date
    db_event.startTime = start_time
    db_event.endTime = end_time
    db_event.academicGroupId = event_update.academicGroupId or event_update.local
    
    db.commit()
    db.refresh(db_event)
    
    # Converter time objects para strings (garantir conversão correta)
    start_time_str = None
    end_time_str = None
    
    if db_event.startTime:
        if isinstance(db_event.startTime, str):
            start_time_str = db_event.startTime
        else:
            start_time_str = db_event.startTime.strftime("%H:%M:%S")
    
    if db_event.endTime:
        if isinstance(db_event.endTime, str):
            end_time_str = db_event.endTime
        else:
            end_time_str = db_event.endTime.strftime("%H:%M:%S")
    
    return {
        "id": db_event.id,
        "title": db_event.title,
        "description": db_event.description,
        "timestamp": db_event.timestamp,
        "eventDate": db_event.eventDate,
        "startTime": start_time_str,
        "endTime": end_time_str,
        "academicGroupId": db_event.academicGroupId,
        "creatorId": db_event.creatorId,
    }


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
    
    # Verificar permissão
    if db_event.creatorId != current_user.id and current_user.role != models.UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Permissão negada para excluir este evento"
        )
    
    event_query.delete(synchronize_session=False)
    db.commit()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)