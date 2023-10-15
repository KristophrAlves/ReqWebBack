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
    
@app.route('/cadastro_veterinario', methods=['POST'])
def cadastro_veterinario():
    try:
        data = request.get_json()
        nome = data['Nome']
        cpf = data['Cpf']
        crmv = data['Crmv']
        uf_crmv = data['UfCrmv']
        email = data['Email']
        numero_habilitacao = data['NumeroHabilitacao']
        telefone = data['Telefone']
        endereco = data['Endereco']
        cidade = data['Cidade']
        uf = data['Uf']
        usuario_id = data['UsuarioID']  # Relacione este ID com o usuário que está logado

        cursor = mysql.cursor()

        # Insira um novo veterinário na tabela 'veterinario'
        cursor.execute("INSERT INTO veterinario (Nome, Cpf, Crmv, UfCrmv, Email, NumeroHabilitacao, Telefone, Endereco, Cidade, Uf, UsuarioID) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                       (nome, cpf, crmv, uf_crmv, email, numero_habilitacao, telefone, endereco, cidade, uf, usuario_id))
        mysql.commit()

        cursor.close()

        return jsonify({'message': 'Veterinário cadastrado com sucesso!'})
    except Exception as e:
        return str(e), 400
    
@app.route('/Getveterinarios/<int:usuario_id>', methods=['GET'])
def get_veterinarios_por_usuario(usuario_id):
    try:
        cursor = mysql.cursor()

        # Realize uma consulta para obter os veterinários associados a um usuário específico
        cursor.execute("SELECT * FROM veterinario WHERE UsuarioID = %s", (usuario_id,))
        veterinarios = cursor.fetchall()

        cursor.close()

        if veterinarios:
            # Crie uma lista de dicionários com as informações dos veterinários
            veterinarios_info = []
            for veterinario in veterinarios:
                veterinario_info = {
                    "ID": veterinario[0],
                    "Nome": veterinario[1],
                    "Cpf": veterinario[2],
                    "Crmv": veterinario[3],
                    "UfCrmv": veterinario[4],
                    "Email": veterinario[5],
                    "NumeroHabilitacao": veterinario[6],
                    "Telefone": veterinario[7],
                    "Endereco": veterinario[8],
                    "Cidade": veterinario[9],
                    "Uf": veterinario[10],
                    "UsuarioID": veterinario[11]
                }
                veterinarios_info.append(veterinario_info)
            return jsonify(veterinarios_info)
        else:
            return jsonify({'message': 'Nenhum veterinário associado a este usuário'}), 404
    except Exception as e:
        return str(e), 400

@app.route('/veterinario/<int:veterinario_id>', methods=['PUT'])
def update_veterinario(veterinario_id):
    try:
        data = request.get_json()
        # Certifique-se de que os campos obrigatórios sejam fornecidos na solicitação JSON
        required_fields = ["ID", 'Nome', 'Cpf', 'Crmv', 'UfCrmv', 'Email', 'NumeroHabilitacao', 'Telefone', 'Endereco', 'Cidade', 'Uf', 'UsuarioID']
        for field in required_fields:
            if field not in data:
                return jsonify({'message': f'O campo obrigatório {field} está faltando'}), 400

        cursor = mysql.cursor()

        # Atualize os dados do veterinário com base no ID
        cursor.execute("UPDATE veterinario SET Nome = %s, Cpf = %s, Crmv = %s, UfCrmv = %s, Email = %s, NumeroHabilitacao = %s, Telefone = %s, Endereco = %s, Cidade = %s, Uf = %s, UsuarioID = %s WHERE ID = %s",
                       (data['Nome'], data['Cpf'], data['Crmv'], data['UfCrmv'], data['Email'], data['NumeroHabilitacao'], data['Telefone'], data['Endereco'], data['Cidade'], data['Uf'], data['UsuarioID'], veterinario_id))
        mysql.commit()

        cursor.close()

        return jsonify({'message': 'Veterinário atualizado com sucesso'})
    except Exception as e:
        return str(e), 400
    
@app.route('/veterinario/<int:veterinario_id>', methods=['GET'])
def get_veterinario_por_id(veterinario_id):
    try:
        cursor = mysql.cursor()

        # Realize uma consulta para obter um veterinário específico com base no ID
        cursor.execute("SELECT * FROM veterinario WHERE ID = %s", (veterinario_id,))
        veterinario = cursor.fetchone()

        cursor.close()

        if veterinario:
            # Crie um dicionário com as informações do veterinário
            veterinario_info = {
                "ID": veterinario[0],
                "Nome": veterinario[1],
                "Cpf": veterinario[2],
                "Crmv": veterinario[3],
                "UfCrmv": veterinario[4],
                "Email": veterinario[5],
                "NumeroHabilitacao": veterinario[6],
                "Telefone": veterinario[7],
                "Endereco": veterinario[8],
                "Cidade": veterinario[9],
                "Uf": veterinario[10],
                "UsuarioID": veterinario[11]
            }
            return jsonify(veterinario_info)
        else:
            return jsonify({'message': 'Nenhum veterinário encontrado com o ID fornecido'}), 404
    except Exception as e:
        return str(e), 400
    
@app.route('/veterinario/<int:veterinario_id>', methods=['DELETE'])
def delete_veterinario(veterinario_id):
    try:
        cursor = mysql.cursor()

        # Verifique se o veterinário com o ID fornecido existe
        cursor.execute("SELECT * FROM veterinario WHERE ID = %s", (veterinario_id,))
        veterinario = cursor.fetchone()

        if not veterinario:
            cursor.close()
            return jsonify({'message': 'Nenhum veterinário encontrado com o ID fornecido'}), 404

        # Se o veterinário existe, execute a exclusão
        cursor.execute("DELETE FROM veterinario WHERE ID = %s", (veterinario_id,))
        mysql.commit()
        cursor.close()

        return jsonify({'message': 'Veterinário excluído com sucesso'})
    except Exception as e:
        return str(e), 400
    
@app.route('/cadastro_proprietario', methods=['POST'])
def cadastro_proprietario():
    try:
        data = request.get_json()
        nome = data['Nome']
        cpf = data['Cpf']
        cnpj = data['Cnpj']
        endereco = data['Endereco']
        email = data['Email']
        telefone = data['Telefone']
        cidade = data['Cidade']
        uf = data['Uf']
        usuario_id = data['UsuarioID']  # Relacione este ID com o usuário que está logado

        cursor = mysql.cursor()

        # Insira um novo proprietário na tabela 'Proprietario'
        cursor.execute("INSERT INTO Proprietario (Nome, Cpf, Cnpj, Endereco, Email, Telefone, Cidade, Uf, UsuarioID) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                       (nome, cpf, cnpj, endereco, email, telefone, cidade, uf, usuario_id))
        mysql.commit()

        cursor.close()

        return jsonify({'message': 'Proprietário cadastrado com sucesso!'})
    except Exception as e:
        return str(e), 400
    
@app.route('/Getproprietarios/<int:usuario_id>', methods=['GET'])
def get_proprietarios_por_usuario(usuario_id):
    try:
        cursor = mysql.cursor()

        # Realize uma consulta para obter os proprietários associados a um usuário específico
        cursor.execute("SELECT * FROM Proprietario WHERE UsuarioID = %s", (usuario_id,))
        proprietarios = cursor.fetchall()

        cursor.close()

        if proprietarios:
            # Crie uma lista de dicionários com as informações dos proprietários
            proprietarios_info = []
            for proprietario in proprietarios:
                proprietario_info = {
                    "ID": proprietario[0],
                    "Nome": proprietario[1],
                    "Cpf": proprietario[2],
                    "Cnpj": proprietario[3],
                    "Endereco": proprietario[4],
                    "Email": proprietario[5],
                    "Telefone": proprietario[6],
                    "Cidade": proprietario[7],
                    "Uf": proprietario[8],
                    "UsuarioID": proprietario[9]
                }
                proprietarios_info.append(proprietario_info)
            return jsonify(proprietarios_info)
        else:
            return jsonify({'message': 'Nenhum proprietário associado a este usuário'}), 404
    except Exception as e:
        return str(e), 400
    
@app.route('/proprietario/<int:proprietario_id>', methods=['PUT'])
def update_proprietario(proprietario_id):
    try:
        data = request.get_json()
        # Certifique-se de que os campos obrigatórios sejam fornecidos na solicitação JSON
        required_fields = ["Nome", "Cpf", "Cnpj", "Endereco", "Email", "Telefone", "Cidade", "Uf", "UsuarioID"]
        for field in required_fields:
            if field not in data:
                return jsonify({'message': f'O campo obrigatório {field} está faltando'}), 400

        cursor = mysql.cursor()

        # Atualize os dados do proprietário com base no ID
        cursor.execute("UPDATE Proprietario SET Nome = %s, Cpf = %s, Cnpj = %s, Endereco = %s, Email = %s, Telefone = %s, Cidade = %s, Uf = %s, UsuarioID = %s WHERE ID = %s",
                       (data['Nome'], data['Cpf'], data['Cnpj'], data['Endereco'], data['Email'], data['Telefone'], data['Cidade'], data['Uf'], data['UsuarioID'], proprietario_id))
        mysql.commit()

        cursor.close()

        return jsonify({'message': 'Proprietário atualizado com sucesso'})
    except Exception as e:
        return str(e), 400
    
@app.route('/proprietario/<int:proprietario_id>', methods=['GET'])
def get_proprietario_por_id(proprietario_id):
    try:
        cursor = mysql.cursor()

        # Realize uma consulta para obter um proprietário específico com base no ID
        cursor.execute("SELECT * FROM Proprietario WHERE ID = %s", (proprietario_id,))
        proprietario = cursor.fetchone()

        cursor.close()

        if proprietario:
            # Crie um dicionário com as informações do proprietário
            proprietario_info = {
                "ID": proprietario[0],
                "Nome": proprietario[1],
                "Cpf": proprietario[2],
                "Cnpj": proprietario[3],
                "Endereco": proprietario[4],
                "Email": proprietario[5],
                "Telefone": proprietario[6],
                "Cidade": proprietario[7],
                "Uf": proprietario[8],
                "UsuarioID": proprietario[9]
            }
            return jsonify(proprietario_info)
        else:
            return jsonify({'message': 'Nenhum proprietário encontrado com o ID fornecido'}), 404
    except Exception as e:
        return str(e), 400
    
@app.route('/proprietario/<int:proprietario_id>', methods=['DELETE'])
def delete_proprietario(proprietario_id):
    try:
        cursor = mysql.cursor()

        # Verifique se o proprietário com o ID fornecido existe
        cursor.execute("SELECT * FROM Proprietario WHERE ID = %s", (proprietario_id))
        proprietario = cursor.fetchone()

        if not proprietario:
            cursor.close()
            return jsonify({'message': 'Nenhum proprietário encontrado com o ID fornecido'}), 404

        # Se o proprietário existe, execute a exclusão
        cursor.execute("DELETE FROM Proprietario WHERE ID = %s", (proprietario_id))
        mysql.commit()
        cursor.close()

        return jsonify({'message': 'Proprietário excluído com sucesso'})
    except Exception as e:
        return str(e), 400

if __name__ == "__main__":
    app.run(host="localhost", port=5000)
