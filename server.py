from flask import Flask, request, jsonify
from flask_cors import CORS 
from werkzeug.security import check_password_hash, generate_password_hash
from dotenv import load_dotenv
import os
import mysql.connector
import jwt
import datetime

load_dotenv() 

app = Flask(__name__)
CORS(app)

SECRET_KEY = os.getenv('SECRET_KEY')

def get_db_connection():
    connection = mysql.connector.connect(
        host='mysql-primeiro-crud-alessandrow13-2639.g.aivencloud.com',
        port='28460',
        user='avnadmin',
        password=os.getenv('DB_PASSWORD'),
        database='app_database',
        ssl_ca='ca.pem'
    )
    return connection

@app.route('/api/register', methods=['POST'])
def register_user():
    data = request.get_json()
    input_username = data.get('username')
    input_password = data.get('password')

    if not input_username or not input_password:
        return jsonify({"error": "Missing credentials"}), 400
    
    hashed_password = generate_password_hash(input_password)

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        query = "INSERT INTO users (username, password_hash) VALUES (%s, %s)"
        cursor.execute(query, (input_username, hashed_password))
        connection.commit()
        return jsonify({"message": "Usuário criado com sucesso!"}), 201
    except mysql.connector.Error as err:
        if err.error == 1062: # 1062(Usuário duplicado)
            return jsonify({"error": "Este usuário já existe. Tente outro."}), 400

        return jsonify({"error": "Falha ao conectar com o banco de dados."}), 500
    finally:
        cursor.close()
        connection.close()
    
@app.route('/api/login', methods=['POST'])
def handle_login():
    data = request.get_json()
    input_username = data.get('username')
    input_password = data.get('password')

    if not input_username or not input_password:
        return jsonify({"error": "Missing credentials"}), 400

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    query = "SELECT * FROM users WHERE username = %s"
    cursor.execute(query, (input_username,))
    user_record = cursor.fetchone()

    cursor.close()
    connection.close()

    if user_record and check_password_hash(user_record['password_hash'], input_password):
        expiration_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
        token = jwt.encode(
            {"username": input_username, "exp": expiration_time},
            SECRET_KEY,
            algorithm="HS256"
        )
        return jsonify({"message": "Logado com sucesso", "token": token}), 200
    else:
        return jsonify({"error": "Senha ou usuário inválido."}), 401
    
@app.route('/api/protected-data', methods=['GET'])
def get_protected_data():
    auth_header = request.headers.get('Authorization')

    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Missing or invalid token"}), 401
    
    token = auth_header.split(" ")[1]

    try:
        decoded_data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        username = decoded_data['username']
        return jsonify({"message": f"Bem-vindo ao dashboard, {username}!"}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token has expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401

@app.route('/api/notes', methods=['GET', 'POST'])
def manage_notes():
    auth_reader = request.headers.get('Authorization')

    if not auth_reader or not auth_reader.startswith('Bearer '):
        return jsonify({"error": "Não autorizado"}), 401
    
    token = auth_reader.split(" ")[1]

    try:
        decoded_data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        current_username = decoded_data['username']
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token has expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401
    
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    if request.method == 'POST':
        data = request.get_json()
        note_content = data.get('content')

        if not note_content:
            return jsonify({"error": "Note cannot be empty"}), 400
        
        try:
            query = "INSERT INTO notes (username, content) VALUES (%s, %s)"
            cursor.execute(query, (current_username, note_content))
            connection.commit()
            return jsonify({"message": "Note saved sucessfully"}), 201
        except mysql.connector.Error as err:
            return jsonify({"error": str(err)}), 400
        finally:
            cursor.close()
            connection.close()
    elif request.method == 'GET':
        try:
            query = "SELECT id, content, created_at FROM notes WHERE username = %s ORDER BY created_at DESC"
            cursor.execute(query, (current_username,))
            user_notes = cursor.fetchall()
            return jsonify(user_notes), 200
        except mysql.connector.Error as err:
            return jsonify({"error": str(err)}), 400
        finally:
            cursor.close()
            connection.close()

@app.route('/api/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    auth_header = request.headers.get('Authorization')

    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Unauthorized"}), 401
    
    token = auth_header.split(" ")[1]

    try:
        decoded_data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        current_username = decoded_data['username']
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token has expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401
    
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        query = "DELETE FROM notes WHERE id = %s AND username = %s"
        cursor.execute(query, (note_id, current_username))
        connection.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Nota não encontrada ou sem autorização."}), 404
        
        return jsonify({"message": "Nota deletada com sucesso!"}), 200
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 400
    finally:
        cursor.close()
        connection.close()

@app.route('/api/notes/<int:note_id>', methods=['PUT'])
def update_note(note_id):
    auto_header = request.headers.get('Authorization')

    if not auto_header or not auto_header.startswith('Bearer '):
        return jsonify({"error": "Unauthorized"}), 401
    
    token = auto_header.split(" ")[1]

    try:
        decode_data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        current_username = decode_data['username']
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token has expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401
    
    data = request.get_json()
    new_content = data.get('content')

    if not new_content:
        return jsonify({"error": "Nota não pode estar vazia"}), 400
    
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        query = "UPDATE notes SET content = %s WHERE id = %s AND username = %s"
        cursor.execute(query, (new_content, note_id, current_username))
        connection.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Nota não encontrada ou sem permissão"}), 404
        
        return jsonify({"message": "Nota atualizada com sucesso!"}), 200
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 400
    finally:
        cursor.close()
        connection.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)