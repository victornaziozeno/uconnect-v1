from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth_router, users_router
from .db import Base, engine
from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
from datetime import datetime

app = FastAPI(title="UCONNECT API", version="1.0.0")
app = Flask(__name__)
CORS(app)

DB_CONFIG = {
    'host': 'uconnect-uconnect.c.aivencloud.com',
    'user': 'avnadmin', # ou seu usuário
    'password': 'AVNS_ZNdJaYqcEhNaEf1dsCl', # ou sua senha
    'database': 'defaultdb' # nome do seu banco de dados
}
def get_db_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        print(f"Erro de conexão com o banco de dados: {err}")
        return None

@app.route('/api/events', methods=['GET'])
def get_events():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Falha na conexão com o banco de dados"}), 500
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, title, description, timestamp as start, academicGroupId, creatorId FROM Event")
    events = cursor.fetchall()
    cursor.close()
    conn.close()

    for event in events:
        event['tipo'] = event.get('description', 'evento-geral')
        event['className'] = event['tipo']

    return jsonify(events)

@app.route('/api/events', methods=['POST'])
def add_event():
    data = request.get_json()
    
    if not data or 'title' not in data or 'start' not in data:
        return jsonify({"error": "Dados incompletos"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Falha na conexão com o banco de dados"}), 500

    cursor = conn.cursor()
    query = """
        INSERT INTO Event (title, description, timestamp, creatorId) 
        VALUES (%s, %s, %s, %s)
    """
    values = (data['title'], data.get('descricao'), data['start'], 1)
    
    try:
        cursor.execute(query, values)
        conn.commit()
        event_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return jsonify({"message": "Evento criado com sucesso", "id": event_id}), 201
    except mysql.connector.Error as err:
        return jsonify({"error": f"Erro ao inserir no banco de dados: {err}"}), 500

@app.route('/api/events/<int:event_id>', methods=['PUT'])
def update_event(event_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Dados incompletos"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Falha na conexão com o banco de dados"}), 500

    cursor = conn.cursor()
    query = """
        UPDATE Event SET title = %s, description = %s, timestamp = %s
        WHERE id = %s
    """
    values = (data['title'], data.get('descricao'), data['start'], event_id)
    
    try:
        cursor.execute(query, values)
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": f"Evento {event_id} atualizado com sucesso"}), 200
    except mysql.connector.Error as err:
        return jsonify({"error": f"Erro ao atualizar no banco de dados: {err}"}), 500

@app.route('/api/events/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Falha na conexão com o banco de dados"}), 500
        
    cursor = conn.cursor()
    query = "DELETE FROM Event WHERE id = %s"
    
    try:
        cursor.execute(query, (event_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": f"Evento {event_id} excluído com sucesso"}), 200
    except mysql.connector.Error as err:
        return jsonify({"error": f"Erro ao excluir do banco de dados: {err}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(users_router)

@app.get("/")
async def root():
    return {"message": "UCONNECT API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
