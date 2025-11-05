# ---------------- ROTAS DE CHAT (VERSÃO COMPATÍVEL) ---------------- #
"""
Rotas de chat ajustadas para a estrutura:
Conversation → Channel → Subchannel → Message
"""
# app/routes/chat_routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, func
from typing import List
from datetime import datetime
import asyncio

from .. import models, schemas, utils
from ..db import get_db

# import broadcast func (ajuste import relativo conforme projeto)
from .chat_ws import _broadcast_to_chat

router = APIRouter(prefix="/chats", tags=["Chat"])
get_current_user = utils.get_current_user

@router.get("/", response_model=List[schemas.Chat])
def get_user_conversations(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    Lista todas as conversas do usuário atual com a última mensagem.
    Query única + joinedload(participants).
    """
    # Subquery: última timestamp por conversationId (através de Channel->Subchannel->Message)
    last_ts_subq = (
        db.query(
            models.Channel.conversationId.label("conv_id"),
            func.max(models.Message.timestamp).label("last_ts"),
        )
        .join(models.Subchannel, models.Subchannel.parentChannelId == models.Channel.id)
        .join(models.Message, models.Message.subchannelId == models.Subchannel.id)
        .group_by(models.Channel.conversationId)
        .subquery()
    )

    rows = (
        db.query(models.Conversation, models.Message, models.User.name.label("author_name"))
        .options(joinedload(models.Conversation.participants))
        .filter(models.Conversation.participants.any(id=current_user.id))
        .outerjoin(models.Channel, models.Channel.conversationId == models.Conversation.id)
        .outerjoin(models.Subchannel, models.Subchannel.parentChannelId == models.Channel.id)
        .outerjoin(last_ts_subq, last_ts_subq.c.conv_id == models.Conversation.id)
        .outerjoin(
            models.Message,
            and_(models.Message.subchannelId == models.Subchannel.id, models.Message.timestamp == last_ts_subq.c.last_ts),
        )
        .outerjoin(models.User, models.User.id == models.Message.authorId)
        .order_by(models.Conversation.updatedAt.desc())
        .distinct(models.Conversation.id)
        .all()
    )

    result = []
    seen = set()
    for conv, msg, author_name in rows:
        if conv.id in seen:
            continue
        seen.add(conv.id)
        participants = [schemas.UserSimple(id=p.id, name=p.name) for p in (conv.participants or [])]

        last_msg_schema = None
        if msg is not None:
            last_msg_schema = schemas.Message(
                id=msg.id,
                content=msg.content,
                timestamp=msg.timestamp,
                authorId=msg.authorId,
                authorName=author_name,
            )

        result.append(schemas.Chat(id=conv.id, title=conv.title or "Sem título", participants=participants, last_message=last_msg_schema))
    return result


@router.get("/{chat_id}/messages", response_model=List[schemas.Message])
def get_chat_messages(chat_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    Obtém todas as mensagens de uma conversa específica.
    """
    chat = db.query(models.Conversation).filter(models.Conversation.id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversa não encontrada")

    participant_ids = [p.id for p in chat.participants]
    if current_user.id not in participant_ids:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado a esta conversa")

    channel = db.query(models.Channel).filter(models.Channel.conversationId == chat_id).first()
    if not channel:
        return []

    subchannel = db.query(models.Subchannel).filter(models.Subchannel.parentChannelId == channel.id).first()
    if not subchannel:
        return []

    rows = (
        db.query(models.Message, models.User.name.label("author_name"))
        .outerjoin(models.User, models.User.id == models.Message.authorId)
        .filter(models.Message.subchannelId == subchannel.id)
        .order_by(models.Message.timestamp.asc())
        .all()
    )

    messages = [
        schemas.Message(id=m.id, content=m.content, timestamp=m.timestamp, authorId=m.authorId, authorName=author_name)
        for (m, author_name) in rows
    ]

    # marca como lidas somente se houver atualizações
    updated = db.query(models.Message).filter(
        models.Message.subchannelId == subchannel.id,
        models.Message.authorId != current_user.id,
        models.Message.isRead == False
    ).update({"isRead": True})
    if updated:
        db.commit()

    return messages


@router.post("/{chat_id}/messages", response_model=schemas.Message, status_code=status.HTTP_201_CREATED)
def send_message(chat_id: int, message: schemas.MessageCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    Envia nova mensagem, grava no DB e dispara broadcast via WebSocket (background).
    """
    chat = db.query(models.Conversation).filter(models.Conversation.id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversa não encontrada")

    participant_ids = [p.id for p in chat.participants]
    if current_user.id not in participant_ids:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Você não pode enviar mensagens para esta conversa")

    channel = db.query(models.Channel).filter(models.Channel.conversationId == chat_id).first()
    if not channel:
        channel = models.Channel(name=f"Channel-{chat_id}", conversationId=chat_id)
        db.add(channel)
        db.flush()

    subchannel = db.query(models.Subchannel).filter(models.Subchannel.parentChannelId == channel.id).first()
    if not subchannel:
        subchannel = models.Subchannel(name="Geral", parentChannelId=channel.id)
        db.add(subchannel)
        db.flush()

    new_message = models.Message(content=message.content, subchannelId=subchannel.id, authorId=current_user.id, timestamp=datetime.utcnow(), isRead=False)
    db.add(new_message)

    chat.updatedAt = datetime.utcnow()

    db.commit()
    db.refresh(new_message)

    # payload para clientes
    payload = {
        "type": "message:new",
        "chat_id": chat_id,
        "message": {
            "id": new_message.id,
            "content": new_message.content,
            "timestamp": new_message.timestamp.isoformat(),
            "authorId": new_message.authorId,
            "authorName": current_user.name,
        },
    }

    # broadcast em background
    try:
        asyncio.create_task(_broadcast_to_chat(chat_id, payload))
    except Exception:
        pass

    return schemas.Message(id=new_message.id, content=new_message.content, timestamp=new_message.timestamp, authorId=new_message.authorId, authorName=current_user.name)


@router.post("/{chat_id}/read", status_code=status.HTTP_204_NO_CONTENT)
def mark_messages_as_read(chat_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    conversation = db.query(models.Conversation).filter(models.Conversation.id == chat_id).first()
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversa não encontrada")

    participant_ids = [p.id for p in conversation.participants]
    if current_user.id not in participant_ids:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado a esta conversa")

    channel = db.query(models.Channel).filter(models.Channel.conversationId == chat_id).first()
    if not channel:
        return

    subchannel = db.query(models.Subchannel).filter(models.Subchannel.parentChannelId == channel.id).first()
    if not subchannel:
        return

    updated = db.query(models.Message).filter(models.Message.subchannelId == subchannel.id, models.Message.authorId != current_user.id, models.Message.isRead == False).update({"isRead": True})
    if updated:
        db.commit()
    return
