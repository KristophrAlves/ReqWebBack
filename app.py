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

        cursor.execute("SELECT id FROM usuario WHERE Email = %s", (email))
        existing_user = cursor.fetchone()

        if existing_user:
            cursor.close()
            return jsonify({'message': 'Email de usuário já existe'}), 400

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        cursor.execute("INSERT INTO usuario (Nome, Email, Senha) VALUES (%s, %s, %s)", (username, email, hashed_password))
        mysql.commit()

        cursor.close()

        return jsonify({'message': 'Usuário inserido com sucesso!'})
    except Exception as e:
        return str('Error', e), 400
    
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data['Email']
    password = data['Senha']

    cursor = mysql.cursor()
    cursor.execute("SELECT id, Senha FROM usuario WHERE Email = %s", (email))
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
        usuario_id = data['UsuarioID'] 

        cursor = mysql.cursor()

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

        cursor.execute("SELECT * FROM veterinario WHERE UsuarioID = %s", (usuario_id,))
        veterinarios = cursor.fetchall()

        cursor.close()

        if veterinarios:
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
        required_fields = ["ID", 'Nome', 'Cpf', 'Crmv', 'UfCrmv', 'Email', 'NumeroHabilitacao', 'Telefone', 'Endereco', 'Cidade', 'Uf', 'UsuarioID']
        for field in required_fields:
            if field not in data:
                return jsonify({'message': f'O campo obrigatório {field} está faltando'}), 400

        cursor = mysql.cursor()

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

        cursor.execute("SELECT * FROM veterinario WHERE ID = %s", (veterinario_id,))
        veterinario = cursor.fetchone()

        cursor.close()

        if veterinario:
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

        cursor.execute("SELECT * FROM veterinario WHERE ID = %s", (veterinario_id,))
        veterinario = cursor.fetchone()

        if not veterinario:
            cursor.close()
            return jsonify({'message': 'Nenhum veterinário encontrado com o ID fornecido'}), 404

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
        cnpj = data['Cpf']
        endereco = data['Endereco']
        email = data['Email']
        telefone = data['Telefone']
        cidade = data['Cidade']
        uf = data['Uf']
        usuario_id = data['UsuarioID'] 

        cursor = mysql.cursor()

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

        cursor.execute("SELECT * FROM Proprietario WHERE UsuarioID = %s", (usuario_id,))
        proprietarios = cursor.fetchall()

        cursor.close()

        if proprietarios:
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

        required_fields = ["Nome", "Cpf", "Cnpj", "Endereco", "Email", "Telefone", "Cidade", "Uf", "UsuarioID"]
        for field in required_fields:
            if field not in data:
                return jsonify({'message': f'O campo obrigatório {field} está faltando'}), 400

        cursor = mysql.cursor()

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

        cursor.execute("SELECT * FROM Proprietario WHERE ID = %s", (proprietario_id,))
        proprietario = cursor.fetchone()

        cursor.close()

        if proprietario:
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

        cursor.execute("SELECT * FROM Proprietario WHERE ID = %s", (proprietario_id))
        proprietario = cursor.fetchone()

        if not proprietario:
            cursor.close()
            return jsonify({'message': 'Nenhum proprietário encontrado com o ID fornecido'}), 404

        cursor.execute("DELETE FROM Proprietario WHERE ID = %s", (proprietario_id))
        mysql.commit()
        cursor.close()

        return jsonify({'message': 'Proprietário excluído com sucesso'})
    except Exception as e:
        return str(e), 400
		
@app.route('/cadastro_animal', methods=['POST'])
def cadastro_animal():
    try:
        data = request.get_json()
        nome = data['Nome']
        registro_marca = data['RegistroMarca']
        especie = data['Especie']
        raca = data['Raca']
        sexo = data['Sexo']
        gestacao = data['Gestacao']
        data_nascimento = data['DataNascimento']
        propriedade = data['Propriedade']
        classificacao = data['Classificacao']
        numero_cadastro_propriedade = data['NumeroCadastroPropriedade']
        coordenadas = data['Coordenadas']
        numero_equideos = data['NumeroEquideos']
        cidade = data['Cidade']
        uf = data['Uf']
        pelagem = data['Pelagem']
        descricao = data['Descricao']
        proprietario_id = data['ProprietarioID']
        usuario_id = data['UsuarioID']

        cursor = mysql.cursor()

        cursor.execute("INSERT INTO Animal (Nome, RegistroMarca, Especie, Raca, Sexo, Gestacao, DataNascimento, Propriedade, Classificacao, NumeroCadastroPropriedade, Coordenadas, NumeroEquideos, Cidade, Uf, Pelagem, Descricao, ProprietarioID, UsuarioID) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                       (nome, registro_marca, especie, raca, sexo, gestacao, data_nascimento, propriedade, classificacao, numero_cadastro_propriedade, coordenadas, numero_equideos, cidade, uf, pelagem, descricao, proprietario_id, usuario_id))
        mysql.commit()

        cursor.close()

        return jsonify({'message': 'Animal cadastrado com sucesso!'})
    except Exception as e:
        return str(e), 400
    
@app.route('/Getanimais/<int:usuario_id>', methods=['GET'])
def get_animais_por_usuario(usuario_id):
    try:
        cursor = mysql.cursor()

        cursor.execute("SELECT * FROM Animal WHERE UsuarioID = %s", (usuario_id,))
        animais = cursor.fetchall()

        cursor.close()

        if animais:
            animais_info = []
            for animal in animais:
                animal_info = {
                    "ID": animal[0],
                    "Nome": animal[1],
                    "RegistroMarca": animal[2],
                    "Especie": animal[3],
                    "Raca": animal[4],
                    "Sexo": animal[5],
                    "Gestacao": animal[6],
                    "DataNascimento": animal[7].strftime('%Y-%m-%d'),
                    "Propriedade": animal[8],
                    "Classificacao": animal[9],
                    "NumeroCadastroPropriedade": animal[10],
                    "Coordenadas": animal[11],
                    "NumeroEquideos": animal[12],
                    "Cidade": animal[13],
                    "Uf": animal[14],
                    "Pelagem": animal[15],
                    "Descricao": animal[16],
                    "ProprietarioID": animal[17],
                    "UsuarioID": animal[18]
                }
                animais_info.append(animal_info)
            return jsonify(animais_info)
        else:
            return jsonify({'message': 'Nenhum animal associado a este usuário'}), 404
    except Exception as e:
        return str(e), 400
    
@app.route('/animal/<int:animal_id>', methods=['PUT'])
def update_animal(animal_id):
    try:
        data = request.get_json()

        required_fields = ["ID", "Nome", "RegistroMarca", "Especie", "Raca", "Sexo", "Gestacao", "DataNascimento", "Propriedade", "Classificacao", "NumeroCadastroPropriedade", "Coordenadas", "NumeroEquideos", "Cidade", "Uf", "Pelagem", "Descricao", "ProprietarioID", "UsuarioID"]
        for field in required_fields:
            if field not in data:
                return jsonify({'message': 'O campo obrigatório {field} está faltando'}), 400

        cursor = mysql.cursor()

        cursor.execute("UPDATE Animal SET Nome = %s, RegistroMarca = %s, Especie = %s, Raca = %s, Sexo = %s, Gestacao = %s, DataNascimento = %s, Propriedade = %s, Classificacao = %s, NumeroCadastroPropriedade = %s, Coordenadas = %s, NumeroEquideos = %s, Cidade = %s, Uf = %s, Pelagem = %s, Descricao = %s, ProprietarioID = %s, UsuarioID = %s WHERE ID = %s",
                       (data['Nome'], data['RegistroMarca'], data['Especie'], data['Raca'], data['Sexo'], data['Gestacao'], data['DataNascimento'], data['Propriedade'], data['Classificacao'], data['NumeroCadastroPropriedade'], data['Coordenadas'], data['NumeroEquideos'], data['Cidade'], data['Uf'], data['Pelagem'], data['Descricao'], data['ProprietarioID'], data['UsuarioID'], animal_id))
        mysql.commit()

        cursor.close()

        return jsonify({'message': 'Animal atualizado com sucesso'})
    except Exception as e:
        return str(e), 400

@app.route('/animal/<int:animal_id>', methods=['GET'])
def get_animal_por_id(animal_id):
    try:
        cursor = mysql.cursor()

        cursor.execute("SELECT * FROM Animal WHERE ID = %s", (animal_id,))
        animal = cursor.fetchone()

        cursor.close()

        if animal:
            animal_info = {
                "ID": animal[0],
                "Nome": animal[1],
                "RegistroMarca": animal[2],
                "Especie": animal[3],
                "Raca": animal[4],
                "Sexo": animal[5],
                "Gestacao": animal[6],
                "DataNascimento": animal[7].strftime('%Y-%m-%d'),
                "Propriedade": animal[8],
                "Classificacao": animal[9],
                "NumeroCadastroPropriedade": animal[10],
                "Coordenadas": animal[11],
                "NumeroEquideos": animal[12],
                "Cidade": animal[13],
                "Uf": animal[14],
                "Pelagem": animal[15],
                "Descricao": animal[16],
                "ProprietarioID": animal[17],
                "UsuarioID": animal[18]
            }
            return jsonify(animal_info)
        else:
            return jsonify({'message': 'Nenhum animal encontrado com o ID fornecido'}), 404
    except Exception as e:
        return str(e), 400

@app.route('/animal/<int:animal_id>', methods=['DELETE'])
def delete_animal(animal_id):
    try:
        cursor = mysql.cursor()

        cursor.execute("SELECT * FROM Animal WHERE ID = %s", (animal_id,))
        animal = cursor.fetchone()

        if not animal:
            cursor.close()
            return jsonify({'message': 'Nenhum animal encontrado com o ID fornecido'}), 404

        cursor.execute("DELETE FROM Animal WHERE ID = %s", (animal_id,))
        mysql.commit()
        cursor.close()

        return jsonify({'message': 'Animal excluído com sucesso'})
    except Exception as e:
        return str(e), 400

@app.route('/cadastro_exame', methods=['POST'])
def cadastro_exame():
    try:
        data = request.get_json()
        serie = data['Serie']
        numero = data['Numero']
        metodo = data['Metodo']
        finalidade = data['Finalidade']
        data_exame = data['DataExame']
        veterinario_id = data['VeterinarioID']
        animal_id = data['AnimalID']
        usuario_id = data['UsuarioID']

        cursor = mysql.cursor()

        cursor.execute("INSERT INTO Exame (Serie, Numero, Metodo, Finalidade, DataExame, VeterinarioID, AnimalID, UsuarioID) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                       (serie, numero, metodo, finalidade, data_exame, veterinario_id, animal_id, usuario_id))
        mysql.commit()
        cursor.close()

        return jsonify({'message': 'Exame cadastrado com sucesso!'})
    except Exception as e:
        return str(e), 400

@app.route('/Getexames/<int:usuario_id>', methods=['GET'])
def get_exames_por_usuario(usuario_id):
    try:
        cursor = mysql.cursor()

        cursor.execute("SELECT * FROM Exame WHERE UsuarioID = %s", (usuario_id,))
        exames = cursor.fetchall()

        cursor.close()

        if exames:
            exames_info = []
            for exame in exames:
                exame_info = {
                    "ID": exame[0],
                    "Serie": exame[1],
                    "Numero": exame[2],
                    "Metodo": exame[3],
                    "Finalidade": exame[4],
                    "DataExame": exame[5].strftime('%Y-%m-%d'),
                    "VeterinarioID": exame[6],
                    "AnimalID": exame[7],
                    "UsuarioID": exame[8]
                }
                exames_info.append(exame_info)
            return jsonify(exames_info)
        else:
            return jsonify({'message': 'Nenhum exame associado a este usuário'}), 404
    except Exception as e:
        return str(e), 400

@app.route('/exame/<int:exame_id>', methods=['PUT'])
def update_exame(exame_id):
    try:
        data = request.get_json()
        serie = data['Serie']
        numero = data['Numero']
        metodo = data['Metodo']
        finalidade = data['Finalidade']
        data_exame = data['DataExame']
        veterinario_id = data['VeterinarioID']
        animal_id = data['AnimalID']
        usuario_id = data['UsuarioID']

        cursor = mysql.cursor()

        cursor.execute("UPDATE Exame SET Serie = %s, Numero = %s, Metodo = %s, Finalidade = %s, DataExame = %s, VeterinarioID = %s, AnimalID = %s, UsuarioID = %s WHERE ID = %s",
                       (serie, numero, metodo, finalidade, data_exame, veterinario_id, animal_id, usuario_id, exame_id))
        mysql.commit()
        
        cursor.close()

        return jsonify({'message': 'Exame atualizado com sucesso'})
    except Exception as e:
        return str(e), 400

@app.route('/exame/<int:exame_id>', methods=['GET'])
def get_exame_por_id(exame_id):
    try:
        cursor = mysql.cursor()

        cursor.execute("SELECT * FROM Exame WHERE ID = %s", (exame_id,))
        exame = cursor.fetchone()

        cursor.close()

        if exame:
            exame_info = {
                "ID": exame[0],
                "Serie": exame[1],
                "Numero": exame[2],
                "Metodo": exame[3],
                "Finalidade": exame[4],
                "DataExame": exame[5].strftime('%Y-%m-%d'),
                "VeterinarioID": exame[6],
                "AnimalID": exame[7],
                "UsuarioID": exame[8]
            }
            return jsonify(exame_info)
        else:
            return jsonify({'message': 'Nenhum exame encontrado com o ID fornecido'}), 404
    except Exception as e:
        return str(e), 400
    
@app.route('/exame/<int:exame_id>', methods=['DELETE'])
def delete_exame(exame_id):
    try:
        cursor = mysql.cursor()

        cursor.execute("SELECT * FROM Exame WHERE ID = %s", (exame_id,))
        exame = cursor.fetchone()

        if not exame:
            cursor.close()
            return jsonify({'message': 'Nenhum exame encontrado com o ID fornecido'}), 404

        cursor.execute("DELETE FROM Exame WHERE ID = %s", (exame_id,))
        mysql.commit()
        cursor.close()

        return jsonify({'message': 'Exame excluído com sucesso'})
    except Exception as e:
        return str(e), 400

@app.route('/exameCompleto/<int:exame_id>', methods=['GET'])
def get_exame_completo(exame_id):
    try:
        cursor = mysql.cursor()

        cursor.execute("SELECT * FROM Exame WHERE ID = %s", (exame_id))
        exame = cursor.fetchone()

        if not exame:
            cursor.close()
            return jsonify({'message': 'Nenhum exame encontrado com o ID fornecido'}), 404

        cursor.execute("SELECT * FROM Proprietario WHERE ID = (SELECT ProprietarioID FROM Animal WHERE ID = %s)", (exame[7],))
        proprietario = cursor.fetchone()

        cursor.execute("SELECT * FROM Veterinario WHERE ID = %s", (exame[6],))
        veterinario = cursor.fetchone()

        cursor.execute("SELECT * FROM Animal WHERE ID = %s", (exame[7],))
        animal = cursor.fetchone()

        cursor.close()

        if exame and proprietario and veterinario and animal:
            exame_info = {
                "Exame": {
                    "ID": exame[0] or '',
                    "Serie": exame[1] or '' ,
                    "Numero": exame[2] or '' ,
                    "Metodo": exame[3] or '' ,
                    "Finalidade": exame[4] or '' ,
                    "DataExame": exame[5].strftime('%Y-%m-%d') or '',
                    "VeterinarioID": exame[6] or '',
                    "AnimalID": exame[7] or '',
                    "UsuarioID": exame[8] or ''
                },
                "Proprietario": {
                    "ID": proprietario[0] or '',
                    "Nome": proprietario[1] or '',
                    "CPF": proprietario[2] or '',
                    "CNPJ": proprietario[3] or '',
                    "Endereco": proprietario[4] or '',
                    "Email": proprietario[5] or '',
                    "Telefone": proprietario[6] or '',
                    "Cidade": proprietario[7] or '',
                    "Uf": proprietario[8] or ''
                },
                "Veterinario": {
                    "ID": veterinario[0] or '',
                    "Nome": veterinario[1] or '',
                    "Cpf": veterinario[2] or '',
                    "Crmv": veterinario[3] or '',
                    "UfCrmv": veterinario[4] or '',
                    "Email": veterinario[5] or '',
                    "NumeroHabilitacao": veterinario[6] or '',
                    "Telefone": veterinario[7] or '',
                    "Endereco": veterinario[8] or '',
                    "Cidade": veterinario[9] or '',
                    "Uf": veterinario[10] or ''
                },
                "Animal": {
                    "ID": animal[0] or '',
                    "Nome": animal[1] or '',
                    "RegistroMarca": animal[2] or '',
                    "Especie": animal[3] or '',
                    "Raca": animal[4] or '',
                    "Sexo": animal[5] or '',
                    "Gestacao": animal[6] or '',
                    "DataNascimento": animal[7].strftime('%Y-%m-%d') or '',
                    "Propriedade": animal[8] or '',
                    "Classificacao": animal[9] or '',
                    "NumeroCadastroPropriedade": animal[10] or '',
                    "Coordenadas": animal[11] or '',
                    "NumeroEquideos": animal[12] or '',
                    "Cidade": animal[13] or '',
                    "Uf": animal[14] or '',
                    "Pelagem": animal[15] or '',
                    "Descricao": animal[16] or '',
                    "ProprietarioID": animal[17] or '',
                    "UsuarioID": animal[18] or ''
                }
            }

            return jsonify(exame_info)
        else:
            return jsonify({'message': 'Alguns dados não puderam ser encontrados'}), 404
    except Exception as e:
        return str(e), 400


if __name__ == "__main__":
    app.run(host="localhost", port=5000)