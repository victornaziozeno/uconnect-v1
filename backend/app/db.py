# ---------------- CONEXÃO COM O BANCO DE DADOS ---------------- #
"""
Este arquivo, db.py, é responsável por configurar a conexão com o banco de
dados usando SQLAlchemy. Ele lê a URL de conexão de um arquivo .env para
segurança, cria o "motor" (engine) de conexão e define uma função (get_db)
para fornecer sessões de banco de dados para as rotas da API.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# --- Configuração e Engine ---
# Lê a URL do banco de dados a partir das variáveis de ambiente.
# O 'engine' é o ponto de entrada para o banco de dados e gerencia o pool de
# conexões. `echo=True` é útil para debug, pois exibe as queries SQL geradas.
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://avnadmin:AVNS_ZNdJaYqcEhNaEf1dsCl@uconnect-uconnect.c.aivencloud.com:24757/defaultdb")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=True  # Debug - remover em produção
)

# --- Sessão e Base Declarativa ---
# SessionLocal é uma fábrica de sessões. Cada instância sua será uma sessão.
# Base é a classe da qual todos os modelos ORM (tabelas) irão herdar.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# --- Função de Dependência para Sessão ---
# A função get_db é uma dependência do FastAPI que cria e fornece uma sessão
# para cada requisição. O bloco try/finally garante que a sessão seja sempre
# fechada (db.close()), mesmo que ocorram erros durante a requisição.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
