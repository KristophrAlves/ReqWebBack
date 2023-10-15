from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from flask_cors import CORS
import pymysql

app = Flask(__name__)
bcrypt = Bcrypt(app)
CORS(app, supports_credentials=True)

mysql = pymysql.connect(
    host='localhost',
    user='root',
    password='1234',
    db='flaskdb'
)

@app.route('/GetUsuarios', methods=['GET'])
def query_users():
    cursor = mysql.cursor()
    cursor.execute('SELECT * FROM usuario')
    result = cursor.fetchall()
    cursor.close()
    return jsonify(result)

@app.route('/createUser', methods=['POST'])
def createUser():
    try:
        data = request.get_json()
        username = data['Nome']
        email = data['Email']
        password = data['Senha']
        cursor = mysql.cursor()

        # Verificar se o usuário já existe
        cursor.execute("SELECT id FROM usuario WHERE Nome = %s", (username))
        existing_user = cursor.fetchone()

        if existing_user:
            cursor.close()
            return jsonify({'message': 'Nome de usuário já existe'}), 400

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Inserir um novo registro na tabela 'users'
        cursor.execute("INSERT INTO usuario (Nome, Email, Senha) VALUES (%s, %s, %s)", (username, email, hashed_password))
        mysql.commit()

        cursor.close()

        return jsonify({'message': 'Usuário inserido com sucesso!'})
    except Exception as e:
        return str('Error', e), 400
    
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['Nome']
    password = data['Senha']

    cursor = mysql.cursor()
    cursor.execute("SELECT id, Senha FROM usuario WHERE Nome = %s", (username))
    user = cursor.fetchone()

    if user and bcrypt.check_password_hash(user[1], password):
        return jsonify({'message': 'Login bem-sucedido!', 'UserId':user[0]})
    else:
        return jsonify({'message': 'Credenciais inválidas'}), 401
    

if __name__ == "__main__":
    app.run(host="localhost", port=5000)
