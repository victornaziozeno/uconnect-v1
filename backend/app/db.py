# ---------------- DATABASE CONNECTION ---------------- #
# Este arquivo, db.py, é responsável por configurar a conexão com o banco de dados usando SQLAlchemy. Ele lê a URL de conexão de um arquivo .env para segurança, cria o "motor" (engine) de conexão e define uma função (get_db) para fornecer sessões de banco de dados para as rotas da API.

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://avnadmin:AVNS_ZNdJaYqcEhNaEf1dsCl@uconnect-uconnect.c.aivencloud.com:24757/defaultdb")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=True  # Debug - remover em produção
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()