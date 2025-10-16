# ---------------- ROTAS DE CHAT (VERSÃO COMPATÍVEL) ---------------- #
"""
Rotas de chat ajustadas para a estrutura:
Conversation → Channel → Subchannel → Message
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from .. import models, schemas, utils
from ..db import get_db

router = APIRouter(
    prefix="/chats",
    tags=["Chat"]
)

# Dependência para obter o usuário logado
get_current_user = utils.get_current_user


@router.get("/", response_model=List[schemas.Chat])
def get_user_conversations(
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    """
    Lista todas as conversas das quais o usuário atual participa.
    """
    # Busca todas as conversas em que o usuário atual é um participante
    user_chats = db.query(models.Conversation).filter(
        models.Conversation.participants.any(id=current_user.id)
    ).all()
    
    # Para cada conversa, anexa a última mensagem
    result = []
    for chat in user_chats:
        # Encontra o channel associado à conversa
        channel = db.query(models.Channel).filter(
            models.Channel.conversationId == chat.id
        ).first()
        
        last_msg = None
        if channel:
            # Se um channel for encontrado, busca o subchannel
            subchannel = db.query(models.Subchannel).filter(
                models.Subchannel.parentChannelId == channel.id
            ).first()
            
            if subchannel:
                # Busca a mensagem mais recente
                last_msg = db.query(models.Message).filter(
                    models.Message.subchannelId == subchannel.id
                ).order_by(models.Message.timestamp.desc()).first()
        
        # Cria objeto para resposta
        chat_data = schemas.Chat(
            id=chat.id,
            title=chat.title or "Sem título",
            participants=[
                schemas.UserSimple(id=p.id, name=p.name) 
                for p in chat.participants
            ],
            last_message=last_msg
        )
        result.append(chat_data)
    
    return result


@router.get("/{chat_id}/messages", response_model=List[schemas.Message])
def get_chat_messages(
    chat_id: int, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    """
    Obtém todas as mensagens de uma conversa específica.
    """
    # Validação 1: A conversa existe?
    chat = db.query(models.Conversation).filter(
        models.Conversation.id == chat_id
    ).first()
    
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Conversa não encontrada"
        )
    
    # Validação 2: O usuário atual pertence a esta conversa?
    participant_ids = [p.id for p in chat.participants]
    if current_user.id not in participant_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Acesso negado a esta conversa"
        )

    # Encontra o channel da conversa
    channel = db.query(models.Channel).filter(
        models.Channel.conversationId == chat_id
    ).first()
    
    if not channel:
        return []  # Retorna lista vazia se não houver channel

    # Encontra o subchannel do channel
    subchannel = db.query(models.Subchannel).filter(
        models.Subchannel.parentChannelId == channel.id
    ).first()
    
    if not subchannel:
        return []  # Retorna lista vazia se não houver subchannel

    # Retorna todas as mensagens do subchannel em ordem cronológica
    messages = db.query(models.Message).filter(
        models.Message.subchannelId == subchannel.id
    ).order_by(models.Message.timestamp.asc()).all()
    
    return messages


@router.post("/{chat_id}/messages", response_model=schemas.Message, status_code=status.HTTP_201_CREATED)
def send_message(
    chat_id: int, 
    message: schemas.MessageCreate, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    """
    Envia uma nova mensagem para uma conversa.
    """
    # Validações de segurança
    chat = db.query(models.Conversation).filter(
        models.Conversation.id == chat_id
    ).first()
    
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Conversa não encontrada"
        )

    participant_ids = [p.id for p in chat.participants]
    if current_user.id not in participant_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Você não pode enviar mensagens para esta conversa"
        )

    # Encontra ou cria o channel
    channel = db.query(models.Channel).filter(
        models.Channel.conversationId == chat_id
    ).first()
    
    if not channel:
        # Criar channel automaticamente se não existir
        channel = models.Channel(
            name=f"Channel-{chat_id}",
            conversationId=chat_id
        )
        db.add(channel)
        db.flush()

    # Encontra ou cria o subchannel
    subchannel = db.query(models.Subchannel).filter(
        models.Subchannel.parentChannelId == channel.id
    ).first()
    
    if not subchannel:
        # Criar subchannel automaticamente se não existir
        subchannel = models.Subchannel(
            name="Geral",
            parentChannelId=channel.id
        )
        db.add(subchannel)
        db.flush()

    # Cria a nova mensagem
    new_message = models.Message(
        content=message.content,
        subchannelId=subchannel.id,
        authorId=current_user.id,
        timestamp=datetime.utcnow(),
        isRead=False
    )
    db.add(new_message)
    
    # Atualiza o timestamp da conversa
    chat.updatedAt = datetime.utcnow()
    
    db.commit()
    db.refresh(new_message)
    
    return new_message


@router.post("/{chat_id}/read", status_code=status.HTTP_204_NO_CONTENT)
def mark_messages_as_read(
    chat_id: int, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    """
    Marca todas as mensagens de uma conversa (que não foram enviadas pelo usuário atual) como lidas.
    """
    # Validações de segurança
    conversation = db.query(models.Conversation).filter(
        models.Conversation.id == chat_id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Conversa não encontrada"
        )

    participant_ids = [p.id for p in conversation.participants]
    if current_user.id not in participant_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Acesso negado a esta conversa"
        )

    # Encontra o channel
    channel = db.query(models.Channel).filter(
        models.Channel.conversationId == chat_id
    ).first()
    
    if not channel:
        return

    # Encontra o subchannel
    subchannel = db.query(models.Subchannel).filter(
        models.Subchannel.parentChannelId == channel.id
    ).first()
    
    if not subchannel:
        return

    # Atualiza o status 'isRead' das mensagens
    db.query(models.Message).filter(
        models.Message.subchannelId == subchannel.id,
        models.Message.authorId != current_user.id,
        models.Message.isRead == False
    ).update({"isRead": True})
    
    db.commit()
    
    return


@router.post("/", response_model=schemas.Chat, status_code=status.HTTP_201_CREATED)
def create_conversation(
    chat_data: schemas.ChatCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Cria uma nova conversa entre usuários.
    """
    # Buscar participantes
    participants = db.query(models.User).filter(
        models.User.id.in_(chat_data.participant_ids)
    ).all()
    
    if len(participants) != len(chat_data.participant_ids):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Um ou mais participantes não foram encontrados"
        )
    
    # Adicionar o usuário atual se não estiver na lista
    if current_user not in participants:
        participants.append(current_user)
    
    # Criar a conversa
    new_conversation = models.Conversation(
        title=f"Chat com {', '.join([p.name for p in participants if p.id != current_user.id])}",
        type=models.ConversationType.direct if len(participants) == 2 else models.ConversationType.group,
        participants=participants
    )
    db.add(new_conversation)
    db.flush()
    
    # Criar channel automaticamente
    channel = models.Channel(
        name=f"Channel-{new_conversation.id}",
        conversationId=new_conversation.id
    )
    db.add(channel)
    db.flush()
    
    # Criar subchannel automaticamente
    subchannel = models.Subchannel(
        name="Geral",
        parentChannelId=channel.id
    )
    db.add(subchannel)
    db.commit()
    db.refresh(new_conversation)
    
    return schemas.Chat(
        id=new_conversation.id,
        title=new_conversation.title,
        participants=[schemas.UserSimple(id=p.id, name=p.name) for p in participants],
        last_message=None
    )