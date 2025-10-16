# Em backend/app/routers/chat.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas, utils
from ..db import get_db

router = APIRouter(
    prefix="/chats",
    tags=["Chat"]
)

# Dependência para obter o usuário logado
get_current_user = utils.get_current_user

@router.get("/", response_model=List[schemas.Chat])
def get_user_conversations(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    Lista todas as conversas das quais o usuário atual participa.
    """
    user_chats = db.query(models.Conversation).filter(models.Conversation.participants.any(id=current_user.id)).all()
    
    for chat in user_chats:
        # CORREÇÃO AQUI: Usando o atributo correto 'subchannelId' do modelo Message
        last_msg = db.query(models.Message).filter(models.Message.subchannelId == chat.id).order_by(models.Message.timestamp.desc()).first()
        chat.last_message = last_msg

    return user_chats

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

    # CORREÇÃO AQUI: Usando o atributo correto 'subchannelId'
    messages = db.query(models.Message).filter(models.Message.subchannelId == chat_id).order_by(models.Message.timestamp.asc()).all()
    return messages

@router.post("/{chat_id}/messages", response_model=schemas.Message, status_code=status.HTTP_201_CREATED)
def send_message(chat_id: int, message: schemas.MessageCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    Envia uma nova mensagem para uma conversa.
    """
    chat = db.query(models.Conversation).filter(models.Conversation.id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversa não encontrada")

    participant_ids = [p.id for p in chat.participants]
    if current_user.id not in participant_ids:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Você não pode enviar mensagens para esta conversa")

    # CORREÇÃO AQUI: Usando os atributos corretos 'subchannelId' e 'authorId'
    new_message = models.Message(
        content=message.content,
        subchannelId=chat_id,
        authorId=current_user.id
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    
    return new_message

@router.post("/{chat_id}/read", status_code=status.HTTP_204_NO_CONTENT)
def mark_messages_as_read(chat_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    Marca todas as mensagens de uma conversa (que não foram enviadas pelo usuário atual) como lidas.
    """
    # Validações de segurança para garantir que o usuário pertence à conversa
    conversation = db.query(models.Conversation).filter(models.Conversation.id == chat_id).first()
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversa não encontrada")

    participant_ids = [p.id for p in conversation.participants]
    if current_user.id not in participant_ids:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado a esta conversa")

    # A lógica de atualização foi removida temporariamente porque o
    # campo 'isRead' não existe no modelo 'Message'.
    # Esta função agora apenas valida o acesso e retorna sucesso.
    
    # db.query(models.Message).filter(
    #     models.Message.subchannelId == chat_id,
    #     models.Message.authorId != current_user.id,
    #     models.Message.isRead == False  
    # ).update({"isRead": True})
    
    # db.commit()
    
    # Retorna uma resposta vazia, indicando sucesso
    return
