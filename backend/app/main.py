from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import mysql.connector

# --- Modelos de Dados (Pydantic Schemas) ---
# O FastAPI usa isso para validar os dados que chegam nas requisições POST e PUT.
# Você pode mover isso para o seu arquivo schemas.py se preferir.
class EventCreateUpdate(BaseModel):
    title: str
    start: datetime
    descricao: str | None = None


# --- Configuração do App FastAPI ---
app = FastAPI(title="UCONNECT API", version="1.0.0")

origins = ["*"]  # Em produção, restrinja para o domínio do seu frontend

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Configuração e Conexão com o Banco de Dados ---
DB_CONFIG = {
    'host': 'uconnect-uconnect.c.aivencloud.com',
    'user': 'avnadmin',
    'password': 'AVNS_ZNdJaYqcEhNaEf1dsCl',
    'database': 'defaultdb',
    'port': 24757
}

def get_db_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        print(f"Erro de conexão com o banco de dados: {err}")
        return None

# --- Endpoints para Eventos (Calendário) ---

@app.get("/api/events")
def get_events():
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Falha na conexão com o banco de dados")
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, title, description, timestamp as start, academicGroupId, creatorId FROM Event")
    events = cursor.fetchall()
    cursor.close()
    conn.close()

    for event in events:
        event['tipo'] = event.get('description', 'evento-geral')
        event['className'] = event['tipo']

    return events

@app.post("/api/events", status_code=201)
def add_event(event: EventCreateUpdate): # Usa o modelo Pydantic para receber os dados
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Falha na conexão com o banco de dados")

    cursor = conn.cursor()
    query = """
        INSERT INTO Event (title, description, timestamp, creatorId) 
        VALUES (%s, %s, %s, %s)
    """
    # Em um sistema real, o creatorId viria da sessão do usuário autenticado
    values = (event.title, event.descricao, event.start, 1)
    
    try:
        cursor.execute(query, values)
        conn.commit()
        event_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return {"message": "Evento criado com sucesso", "id": event_id}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Erro ao inserir no banco de dados: {err}")

@app.put("/api/events/{event_id}")
def update_event(event_id: int, event: EventCreateUpdate): # Usa o modelo Pydantic
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Falha na conexão com o banco de dados")

    cursor = conn.cursor()
    query = """
        UPDATE Event SET title = %s, description = %s, timestamp = %s
        WHERE id = %s
    """
    values = (event.title, event.descricao, event.start, event_id)
    
    try:
        cursor.execute(query, values)
        conn.commit()
        cursor.close()
        conn.close()
        return {"message": f"Evento {event_id} atualizado com sucesso"}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar no banco de dados: {err}")

@app.delete("/api/events/{event_id}")
def delete_event(event_id: int):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Falha na conexão com o banco de dados")
        
    cursor = conn.cursor()
    query = "DELETE FROM Event WHERE id = %s"
    
    try:
        cursor.execute(query, (event_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return {"message": f"Evento {event_id} excluído com sucesso"}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Erro ao excluir do banco de dados: {err}")


# --- Outros Endpoints e Routers ---
# Seus routers de autenticação e usuários devem ser importados e incluídos aqui
# Exemplo:
# from .routers import auth_router, users_router
# app.include_router(auth_router)
# app.include_router(users_router)

@app.get("/")
async def root():
    return {"message": "UCONNECT API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
