from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 🔧 Aqui colocamos a URL completa já com +pymysql e o caminho do certificado SSL
DATABASE_URL = (
    "mysql+pymysql://avnadmin:AVNS_ZNdJaYqcEhNaEf1dsCl"
    "@uconnect-uconnect.c.aivencloud.com:24757/defaultdb"
    "?ssl_ca=C:/Users/Victor/Desktop/projeto/uconnect-v1-main/backend/app/ca.pem"
)

# Criar engine
engine = create_engine(DATABASE_URL, pool_pre_ping=True, echo=True)  # echo=True para ver logs SQL

# Sessão do banco
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para os modelos
Base = declarative_base()


# Dependência para injeção no FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
