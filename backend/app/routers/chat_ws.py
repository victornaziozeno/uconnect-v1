# app/routes/chat_ws.py
import asyncio
from typing import Dict, Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter(prefix="/chats", tags=["Chat"])

# mapa chat_id -> set of WebSocket connections
_connections: Dict[int, Set[WebSocket]] = {}

async def _broadcast_to_chat(chat_id: int, payload: dict):
    """Envia payload a todas as conexões websocket do chat (não bloqueante)."""
    conns = list(_connections.get(chat_id, set()))
    if not conns:
        return
    await asyncio.gather(*[conn.send_json(payload) for conn in conns], return_exceptions=True)

@router.websocket("/ws/{chat_id}")
async def websocket_endpoint(websocket: WebSocket, chat_id: int, token: str = None):
    """
    WebSocket para receber updates em tempo real para um chat.
    Opcional: token para autenticação (implemente validação se quiser).
    """
    await websocket.accept()
    chat_id = int(chat_id)
    if chat_id not in _connections:
        _connections[chat_id] = set()
    _connections[chat_id].add(websocket)

    try:
        while True:
            # Mantém a conexão viva. Recebe pings do cliente (opcional).
            _ = await websocket.receive_text()
    except WebSocketDisconnect:
        _connections.get(chat_id, set()).discard(websocket)
    except Exception:
        _connections.get(chat_id, set()).discard(websocket)
        try:
            await websocket.close()
        except Exception:
            pass
