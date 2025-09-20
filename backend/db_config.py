# backend/db_config.py

import mysql.connector
from mysql.connector import Error

def conectar():
    """
    Função para conectar ao banco de dados MySQL no PythonAnywhere.
    Retorna o objeto de conexão se for bem-sucedido, ou None se falhar.
    """
    try:
        # Substitua pelas suas credenciais do PythonAnywhere
        conexao = mysql.connector.connect(
            host='Vitusau.mysql.pythonanywhere-services.com',
            user='Vitusau',
            password='QXLFZaEr',
            database='Vitusau$uconnect'
        )

        if conexao.is_connected():
            print("Conexão com o MySQL bem-sucedida!")
            return conexao

    except Error as e:
        print(f"Erro ao conectar ao MySQL: {e}")
        return None

# Exemplo de como usar a função (pode ser removido depois)
if __name__ == '__main__':
    conn = conectar()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT DATABASE();")
        db_name = cursor.fetchone()
        print(f"Você está conectado ao banco de dados: {db_name[0]}")
        cursor.close()
        conn.close()
        print("Conexão com o MySQL foi encerrada.")