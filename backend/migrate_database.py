# backend/migrate_database.py
"""
Script para adicionar a coluna 'type' à tabela Post
Execute este script uma única vez para atualizar o banco de dados
"""
import sys
from sqlalchemy import text
from app.db import engine

def migrate_add_post_type():
    """Adiciona a coluna 'type' à tabela Post se ela não existir"""
    
    print("Iniciando migração do banco de dados...")
    
    with engine.connect() as connection:
        try:
            check_column = text("""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'Post' 
                AND COLUMN_NAME = 'type'
            """)
            
            result = connection.execute(check_column)
            column_exists = result.scalar() > 0
            
            if column_exists:
                print("✓ A coluna 'type' já existe na tabela Post")
                return
            
            print("Adicionando coluna 'type' à tabela Post...")
            
            alter_table = text("""
                ALTER TABLE Post 
                ADD COLUMN type ENUM('announcement', 'notice') 
                NOT NULL DEFAULT 'announcement'
            """)
            
            connection.execute(alter_table)
            connection.commit()
            
            print("✓ Coluna 'type' adicionada com sucesso!")
            
            create_index = text("""
                CREATE INDEX idx_post_type ON Post(type)
            """)
            
            connection.execute(create_index)
            connection.commit()
            
            print("✓ Índice criado com sucesso!")
            print("✓ Migração concluída!")
            
        except Exception as e:
            print(f"✗ Erro durante a migração: {e}")
            connection.rollback()
            sys.exit(1)

if __name__ == "__main__":
    migrate_add_post_type()
