var contador = 0;
const nome = document.getElementById("nome-usuario");
const NOMES_SISTEMAS = {
    ordem_paranormal: "Ordem Paranormal",
    tormenta20: "Tormenta 20"
};

if (nome) {
    const boasVindas = document.getElementById("texto-boas-vindas");
    const final = document.getElementById("final");
    const usuario = nome.dataset.usuario;
    const texto = `Olá ${usuario}, Seja bem-vindo ao D20HUB.`;
    let i = 0;
    function digitar() {
        if (i < texto.length) {
            if (i < 4) {
                boasVindas.textContent += texto[i];

            } else if (i < 4 + usuario.length) {
                nome.textContent += texto[i];

            } else {
                final.textContent += texto[i];
            }

            i++;

            let velocidade = 40 + Math.random() * 60;

            if (texto[i - 1] === " ") {
                velocidade += 80;
            }

            if (".,!?:;".includes(texto[i - 1])) {
                velocidade += 250;
            }

            setTimeout(digitar, velocidade);
        } else {
            const cursor = document.querySelector(".cursor");

            if (cursor) {
                cursor.style.display = "none";
            }
        }
    }

    document.addEventListener("DOMContentLoaded", function() {
        digitar();
    });
}

document.addEventListener("DOMContentLoaded", function() {
    const elemento = document.getElementById("texto-boas-vindas");

    if (elemento) {
        digitar();
    }
});

function criarDivFicha(id, nome, sistema) {
    const div = document.createElement("div");
    div.classList.add("divfichas");
    div.id = id;
    fichasContainer.appendChild(div);

    const etiqueta = document.createElement("span");
    etiqueta.classList.add("etiquetaSistema");
    etiqueta.textContent = NOMES_SISTEMAS[sistema] || sistema;
    div.appendChild(etiqueta);

    const input = document.createElement("input");
    input.type = "text";
    input.placeholder = "Nome da ficha";
    input.classList.add("inputficha");
    input.value = nome;
    div.appendChild(input);

    input.addEventListener('blur', () => {
        let nomeAtual = input.value.trim();
        fetch(`/fichas/${id}/ficha/salvar/`, {
            method: "POST",
            headers: {
                "X-CSRFToken": csrftoken
            },
            body: JSON.stringify({
            campo: "nome",   
            valor: nomeAtual
        })
        })
        .then(res => res.json())
        .then(data => {
            if (data.status !== true) {
                mostrarMensagem(
                    "Erro",
                    "Erro ao salvar o nome da ficha! Tente novamente."
                );
            }
        });
    });

    const botoesDiv = document.createElement("div");
    botoesDiv.classList.add("botoesDiv");
    div.appendChild(botoesDiv);
        
    const acessarBtn = document.createElement("button");
    acessarBtn.innerHTML = '<i class="bi-file-earmark-text"></i> Acessar';
    acessarBtn.classList.add("acessarBtn");
    botoesDiv.appendChild(acessarBtn);

    acessarBtn.addEventListener("click", () => {
        const nomeAtual = input.value.trim();
        if (nomeAtual) {
            window.location.href = `/fichas/${id}/ficha/`;
        } else {
                mostrarMensagem(
                    "Nome inválido",
                    "Por favor, digite um nome para a ficha."
                );
            }
    });
        
    const excluirBtn = document.createElement("button");
    excluirBtn.innerHTML = '<i class="bi bi-trash"></i> Excluir';
    excluirBtn.classList.add("excluirBtn");
    botoesDiv.appendChild(excluirBtn);

    excluirBtn.addEventListener("click", () => {

        confirmarAcao(
            "Excluir ficha",
            "Tem certeza que deseja excluir esta ficha?",
            () => {

                fetch(`/fichas/${id}/ficha/excluir/`, {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": window.csrftoken
                    }
                })
                .then(res => res.json())
                .then(data => {

                    if (data.status === true) {
                        fichasContainer.removeChild(div);
                        contador--;
                        document.getElementById("contadorFichas").textContent =
                            `Fichas: ${contador}/15`;
                    } else {
                        mostrarMensagem(
                            "Erro",
                            "Erro ao excluir ficha! Tente novamente."
                        );
                    }
                });
            }
        );
    });
}

function carregarFichas() {
    contador = 0;
    fetch("/fichas/usuario/", {
        method: "GET",
        headers: {
            "X-CSRFToken": csrftoken
        }
    })
    .then(res => res.json())
    .then(data => {
        data.forEach(ficha => {
            criarDivFicha(ficha.id, ficha.nome, ficha.sistema);
            contador++;
        });
        document.getElementById("contadorFichas").textContent = `Fichas: ${contador}/15`;
    });
}

if (document.getElementById("fichasContainer")) {
    carregarFichas();
    const sistemaModal = document.getElementById("sistemaModal");

    document.getElementById("criarFicha").addEventListener("click", () => {
        if (contador >= 15) {
            mostrarMensagem(
                "Limite atingido",
                "Você já possui o número máximo de 15 fichas."
            );
            return;
        }
        sistemaModal.style.display = "flex";
    });

    document.getElementById("sistemaModalFechar").addEventListener("click", () => {
        sistemaModal.style.display = "none";
    });

    sistemaModal.addEventListener("click", (e) => {
        if (e.target === sistemaModal) {
            sistemaModal.style.display = "none";
        }
    });

    document.querySelectorAll(".sistema-opcao").forEach(botao => {
        botao.addEventListener("click", () => {
            sistemaModal.style.display = "none";
            criarFicha(botao.dataset.sistema);
        });
    });

    document.getElementById("limparFichas").addEventListener("click", () => {
        confirmarAcao(
            "Limpar fichas",
            "Tem certeza que deseja excluir todas as suas fichas?",
            () => {
                fetch("/fichas/limpar/", {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": csrftoken
                    }
                })
                .then(res => res.json())
                .then(data => {
                    if (data.status === true) {
                        while (fichasContainer.firstChild) {fichasContainer.removeChild(fichasContainer.firstChild);}
                        contador = 0;
                        document.getElementById("contadorFichas").textContent = `Fichas: ${contador}/15`;
                    } else {

                        mostrarMensagem(
                            "Erro",
                            "Não foi possível limpar as fichas. Tente novamente."
                        );
                    }
                });
            }
        );
    });
}

function criarFicha(sistema) {
    fetch("/fichas/criar/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrftoken
        },
        body: JSON.stringify({ sistema: sistema })
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === true) {
            criarDivFicha(data.id, data.nome, data.sistema);
            contador++;
            document.getElementById("contadorFichas").textContent = `Fichas: ${contador}/15`;
        } else {
            mostrarMensagem("Erro", data.mensagem || "Não foi possível criar a ficha. Tente novamente.");
        }
    });
}

function mostrarMensagem(titulo, mensagem) {
    const modal = document.getElementById("mensagemModal");

    document.getElementById("mensagemModalTitulo").textContent = titulo;
    document.getElementById("mensagemModalTexto").textContent = mensagem;
    document.getElementById("mensagemModalCancelar").style.display = "none";
    document.getElementById("mensagemModalConfirmar").textContent = "OK";
    document.getElementById("mensagemModalConfirmar").style.display = "block";

    modal.style.display = "flex";

    document.getElementById("mensagemModalConfirmar").onclick = () => {
        modal.style.display = "none";
    };

    document.getElementById("mensagemModalFechar").onclick = () => {
        modal.style.display = "none";
    };
}

function confirmarAcao(titulo, mensagem, callback) {
    const modal = document.getElementById("mensagemModal");

    document.getElementById("mensagemModalTitulo").textContent = titulo;
    document.getElementById("mensagemModalTexto").textContent = mensagem;

    const cancelar = document.getElementById("mensagemModalCancelar");
    const confirmar = document.getElementById("mensagemModalConfirmar");
    const fechar = document.getElementById("mensagemModalFechar");

    cancelar.style.display = "block";
    confirmar.style.display = "block";

    modal.style.display = "flex";

    confirmar.onclick = () => {
        modal.style.display = "none";
        callback();
    };

    cancelar.onclick = () => {
        modal.style.display = "none";
    };

    fechar.onclick = () => {
        modal.style.display = "none";
    };
}

