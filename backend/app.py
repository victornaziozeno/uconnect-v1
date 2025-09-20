# backend/app.py

from flask import Flask, jsonify
from db_config import conectar # <-- Importa a sua função de conexão

app = Flask(__name__)

@app.route('/usuarios')
def get_usuarios():
    conn = conectar()
    if conn is None:
        return jsonify({"erro": "Não foi possível conectar ao banco de dados"}), 500

    cursor = conn.cursor(dictionary=True) # dictionary=True retorna resultados como dicionários
    cursor.execute("SELECT id, nome, email FROM usuarios") # Exemplo de query
    usuarios = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(usuarios)

# ... resto do seu código de API ...

if __name__ == '__main__':
    app.run()