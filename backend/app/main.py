from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, users, events, groups, publications
from .db import Base, engine

# Cria as tabelas no banco de dados, se não existirem
Base.metadata.create_all(bind=engine)

# Cria a aplicação principal do FastAPI
app = FastAPI(
    title="UCONNECT API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

origins = {
    "null",  # Essencial para testes abrindo o HTML localmente
    "http://127.0.0.1:5500", # Para o Live Server do VS Code
    "http://localhost:5500",
    "http://127.0.0.1:8000", # Origem da própria API (geralmente não necessário, mas não prejudica)
    "http://localhost:3000", # Origem que estava no segundo bloco
}

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(origins),  # Converte o set de volta para uma lista
    allow_credentials=True,
    allow_methods=["*"],          # Permite todos os métodos (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],          # Permite todos os cabeçalhos
)

# Inclui os roteadores da sua aplicação
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(events.router)

app.include_router(groups.router)
app.include_router(publications.router)

# Rota principal
@app.get("/")
def root():
    return {
        "message": "UCONNECT API",
        "docs": "/docs",
        "health": "/health"
    }

# Rota de verificação de saúde da API
@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}