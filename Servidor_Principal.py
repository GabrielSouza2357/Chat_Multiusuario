"""
Servidor principal do chat, responsável por gerenciar as conexões dos clientes e a troca de mensagens. 
"""

from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from datetime import datetime
import os, requests, threading

app = Flask(__name__)
app.config['SECRET_KEY'] = '#Secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

host = "0.0.0.0"
port = 4002

# Lista de mensagens enviadas e usuários conectados:
mensagens = []
usuarios = {}

# Histórico de mensagens e de réplica:
arq_hist = "Histórico/Mensagens.txt"
arq_rep = "Histórico_de_Réplica.txt"

# URL do servidor réplica:
url_rep = f"http://{host}:{port}/replica"

# Função para salvar histórico de mensagens em um arquivo:
def salvar_historico(mensagem):
    os.makedirs("Histórico", exist_ok=True)
    with open(arq_hist, "a", encoding="utf-8") as f:
        f.write(f"{mensagem}\n")

# Função para thread de replicação de mensagens para o servidor réplica:
def replicar_mensagem(mensagem):
    try:
        requests.post(url_rep, json={"msg": mensagem}, timeout=3)
    except Exception as e:
        print(f"Erro ao replicar mensagem: {e}")

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template("Chat.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template("Login.html")

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    return render_template("Cadastro.html")

@app.route('/replica', methods=['GET', 'POST'])
def replicar():
    arq = request.json
    tem = arq.get("time")
    use = arq.get("user")
    men = arq.get("msg")
    with open(arq_rep, "a", encoding="utf-8") as f:
        f.write(f"[{tem}] -> {use}: {men}\n")
    return {
        "status": "ok"
    }

# Conexão de clientes:
@socketio.on('connect')
def conectar():
    print("\nCliente conectado.")
    
# Desconexão de clientes:
@socketio.on('disconnect')
def desconectar():
    nome_usuario = usuarios.get(request.sid, "Usuário")
    emit('message', {
        'user': "Servidor", 
        'msg': f"{nome_usuario} saiu do chat."
        }, broadcast=True)
    print(f"\n{nome_usuario} saiu do chat.")
    usuarios.pop(request.sid, None)

# Entrada do usuário
@socketio.on('join')
def entrar(data):
    nome_usuario = data['user']
    email = data['email']
    senha = data['password']
    usuarios[request.sid] = nome_usuario
    emit('message', {
        'user': "Servidor", 
        'msg': f"{nome_usuario} entrou no chat.",
        'email': email,
        'password': senha
        }, broadcast=True)
    print(f"\n{nome_usuario} entrou no chat.")
    
# Mensagem enviada pelo usuário
@socketio.on('send_message')
def enviar_mensagem(data):
    mensagem = data['msg']
    nome_usuario = usuarios.get(request.sid, "Usuário")
    tempo = datetime.now().strftime('%H:%M:%S')
    men_form = f"[{tempo}] -> {nome_usuario}: {mensagem}"
    
    # Salvar histórico de mensagens
    salvar_historico(men_form)
    
    # Adicionar mensagem à lista
    mensagens.append({'user': nome_usuario, 'msg': mensagem})
    
    # Replicar mensagem para o servidor réplica
    thread = threading.Thread(target=replicar_mensagem, args=(men_form,))
    thread.start()
    
    # Enviar mensagem para todos os clientes
    emit('message', {
        'user': nome_usuario, 
        'msg': mensagem, 
        'time': tempo
        }, broadcast=True)
    
    print(f"\n{nome_usuario} [{tempo}]: {mensagem}")

if __name__ == "__main__":
    if not os.path.exists(arq_hist):
        with open(arq_hist, "w", encoding="utf-8") as f:
            f.write("")
    elif not os.path.exists(arq_rep):
        with open(arq_rep, "w", encoding="utf-8") as f:
            f.write("")
    socketio.run(
        app, 
        debug=True, 
        host=host, 
        port=port
        )