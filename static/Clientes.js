const socket = io();

let nome_usuario = socket.on("message", (data) => data.user);
let email = socket.on("message", (data) => data.email);
let senha = socket.on("message", (data) => data.password);

socket.emit("join", {
    user: nome_usuario,
    email: email,
    password: senha
});

// Cliente recebendo uma thread
socket.on("message", (data) => {
    const pacoteChat = document.getElementById("pacote-chat");
    const div = document.createElement("div");
    if (nome_usuario === data.user) {
        div.classList.add("mensagem-usuario");
    }
    else {
        div.classList.add("mensagem");
    }
    div.innerHTML = `<strong>${data.user}: </strong><weak>${data.msg}</weak>`;
    pacoteChat.appendChild(div);
    pacoteChat.scrollTop = pacoteChat.scrollHeight;

    socket.emit("join", {
        user: nome_usuario,
        email: email,
        password: senha
    });
});

function cadastrar_usuario() {
    const nomeInput = document.getElementById("nome-usuario");
    const emailInput = document.getElementById("email");
    const senhaInput = document.getElementById("senha");
    const confirmarSenhaInput = document.getElementById("confirmar-senha");
    nome_usuario = nomeInput.value.trim();
    email = emailInput.value.trim();
    senha = senhaInput.value.trim();
    const confirmarSenha = confirmarSenhaInput.value.trim();
    if (nome_usuario === "") {
        alert("Por favor, insira um nome de usuário.");
        return;
    }
    if (email === "") {
        alert("Por favor, insira um email.");
        return;
    }
    if (senha === "") {
        alert("Por favor, insira uma senha.");
        return;
    }
    else if (senha !== confirmarSenha) {
        alert("As senhas não coincidem.");
        return;
    }
    socket.emit("join", {
        user: nome_usuario, 
        email: email,
        password: senha
    });
    window.location.href = "/";
}

function entrar_no_chat() {
    const nomeInput = document.getElementById("nome-usuario");
    const emailInput = document.getElementById("email");
    const senhaInput = document.getElementById("senha");
    nome_usuario = nomeInput.value.trim();
    const email = emailInput.value.trim();
    const senha = senhaInput.value.trim();
    if (nome_usuario === "") {
        alert("Por favor, insira seu nome de usuário.");
        return;
    }
    else if (email === "") {
        alert("Por favor, insira seu email.");
        return;
    }
    else if (senha === "") {
        alert("Por favor, insira sua senha.");
        return;
    }
    socket.emit("join", { 
        user: nome_usuario, 
        email: email, 
        password: senha });
    window.location.href = "/";
}

function enviar_mensagem() {
    const mensagemInput = document.getElementById("mensagem-usuario");
    const mensagem = mensagemInput.value.trim();
    if (mensagem === "") {
        return;
    }
    socket.emit("send_message", {
        msg: mensagem });
    mensagemInput.value = "";
}

function sair_do_chat() {
    window.location.href = "/login";
}