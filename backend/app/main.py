# ---------------- ARQUIVO PRINCIPAL DA APLICAÇÃO (main.py) ---------------- #
"""
Este é o arquivo principal que inicializa e configura a aplicação FastAPI.
Ele é o ponto de entrada do servidor. Suas responsabilidades incluem:
- Criar as tabelas no banco de dados com base nos modelos SQLAlchemy.
- Instanciar o objeto principal do FastAPI com metadados da API.
- Configurar o Middleware CORS para permitir requisições de diferentes origens.
- Incluir e organizar os diferentes módulos de rotas (auth, users, etc.).
- Definir rotas básicas como a raiz ("/") e a de verificação de saúde ("/health").
"""
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, users, events, groups, publications
from .db import Base, engine

# --- Criação das Tabelas no Banco de Dados ---
# Esta linha utiliza os metadados do `Base` (herdado pelos modelos) para
# criar todas as tabelas no banco de dados conectado pelo `engine`.
# Isso só acontece se as tabelas ainda não existirem.
Base.metadata.create_all(bind=engine)


# --- Instanciação do FastAPI ---
# Aqui, a aplicação principal é criada. O título, a versão e os caminhos
# para a documentação interativa (Swagger UI em /docs e ReDoc em /redoc)
# são definidos.
app = FastAPI(
    title="UCONNECT API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# --- Configuração do CORS (Cross-Origin Resource Sharing) ---
# O middleware CORS é configurado para permitir que o frontend (rodando em
# origens diferentes, como http://localhost:5500) possa fazer requisições
# para esta API. `origins` define quais endereços são permitidos.
origins = {
    "null",  # Essencial para testes abrindo o HTML localmente
    "http://127.0.0.1:5500", # Para o Live Server do VS Code
    "http://localhost:5500",
    "http://127.0.0.1:8000", # Origem da própria API
    "http://localhost:3000", # Origem comum para React/Vue/etc.
}

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(origins),  # Lista de origens permitidas
    allow_credentials=True,
    allow_methods=["*"],          # Permite todos os métodos (GET, POST, etc.)
    allow_headers=["*"],          # Permite todos os cabeçalhos
)

# --- Inclusão dos Roteadores ---
# Cada `include_router` conecta um conjunto de rotas definido em outro
# arquivo (ex: `routers/users.py`) à aplicação principal. Isso ajuda a
# manter o código organizado e modular.
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(events.router)
app.include_router(groups.router)
app.include_router(publications.router)


# --- Rotas Principais (Raiz e Health Check) ---
# Estas são rotas simples definidas diretamente no arquivo principal.
# A rota raiz ("/") serve como uma página de boas-vindas da API.
# A rota "/health" é uma boa prática para verificar se a API está
# funcionando corretamente (viva e respondendo).
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
