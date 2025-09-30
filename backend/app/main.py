from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, users, events
from .db import Base, engine


# Cria a aplicação principal do FastAPI
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="UCONNECT API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Adiciona o middleware de CORS para permitir requisições de outras origens (ex: seu frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:5500", "http://localhost:5500"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)


# Inclui os routers da aplicação para organizar os endpoints
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(events.router)

# Endpoint raiz para verificar se a API está online
@app.get("/")
def root():
    return {
        "message": "UCONNECT API",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}