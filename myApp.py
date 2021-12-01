import flask
import socket
from flask import request, jsonify
from mysql.connector import connect, Error

try:
    connection = connect(
        host = "127.0.0.1",
        port = "3306",
        user = "root",
        password = "131311",
        database = 'sys',
    )
except:
    print("Erro ao tentar conectar ao banco")
    exit(1)
    
app = flask.Flask(__name__)

app.config["DEBUG"] = True

host_ip = socket.gethostname()

local_ip = socket.gethostbyname(host_ip)

@app.route("/getLista")
def getAllUser():
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM pessoas") #realiza a consulta
        obj = cursor.fetchall()
        
        listaNomes = []
        for obj in obj:
            listaNomes.append(
                {"id": obj[0], "nome": obj[1]}
            )
    except:
        return jsonify(
            {
                "cod": 0,
                "status": "Erro no server"
            }    
        )
    return jsonify({"cod":1,"dados":listaNomes}) 
    
@app.route("/insere", methods=['POST'])
def insertOne():
    json = request.get_json()
    if(not(json)): #if caso nao venha json
        return jsonify( 
            {
                "cod": 0,
                "status": "Sem dados"
            }
        )
    
    if((not('nome' in json)) or (not('data' in json))): #if caso nao venha o nome
        return jsonify({
                "cod": 0,
                "status": "Faltou ser passado campo no Json"
        })
    
    if(len(json["data"]) > 10):  #caso a string venha maior que 10
        return jsonify({
                "cod": 0,
                "status": "Data Invalida, sao necessarios 10 caracteres"
        })
    
    consulta = "INSERT INTO pessoas VALUES(null, %s, %s)"
    informacoes = (json['nome'], json['data'])
    
    try:
        cursor = connection.cursor()
        cursor.execute(consulta, informacoes)
        cursor.execute("COMMIT")
    except:
        return jsonify(
            {
                "cod": 0,
                "status": "Nao inserido" #erro no banco 
            }
        )
        
    return jsonify( #foi inserido
        {
            "cod": 1,
            "status": "Inserido"
        }
    )

@app.route("/getDetalhe")
def getOne():
    parameter = request.args.get('id') #pega o id
    
    if(not(parameter)): #ve se  veio id
        return jsonify({
            "cod": 0,
            "status": "Sem ID"
        })

    try:
        parameter = int(parameter)
    except:
        return jsonify({
            "cod": 0,
            "status": "parametro Id invalido: O id precisa ser do tipo INTEIRO"
        })
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM pessoas WHERE id = {}".format(parameter)) #faz a req e recebe um array com os valores
    obj = cursor.fetchone()
    try:
        return jsonify({"cod":1,"dados":{
            "id":   obj[0],
            "nome": obj[1],
            "data": obj[2]       
        }})

    except:
        return jsonify({
            "cod": 0,
            "status": "Nao existe este ID"
        })
    
@app.route("/apagaID", methods=['DELETE'])
def removeOne():
    parameter = request.args.get('id')

    if(not(parameter)):
        return jsonify({
            "cod": 0,
            "status": "Nao foi passado o parametro ID"
        })

    try:
        parameter = int(parameter)

    except:
        return jsonify({
            "cod": 0,
            "status": "parametro Id invalido: O id precisa ser do tipo INTEIRO"
        })
    
    try:
      
        cursor = connection.cursor()
        cursor.execute("SELECT nome FROM pessoas WHERE id = {}".format(parameter)) # faz a req e recebe o select
        obj = cursor.fetchone()
        cursor.execute("DELETE FROM pessoas WHERE id = {}".format(parameter))
        cursor.execute("commit")
    except:
        return jsonify({
            "cod": 0,
            "status": "Nao apagado"
        })
        
    return jsonify({
            "cod": 1,
            "nomeApagado": obj[0], #printa o nome do excluido
            "status": "Apagado"
        })    
    
if __name__ == '__main__':
    print(local_ip)
    app.run(host=local_ip, port= 3000)

