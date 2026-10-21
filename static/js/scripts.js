var contador = 0;
const nome = document.getElementById("nome-usuario");
const NOMES_SISTEMAS = {
    ordem_paranormal: "Ordem Paranormal",
    tormenta20: "Tormenta 20"
};

function atualizarContador() {
    document.getElementById("contadorFichas").textContent =
        interpolate(gettext("Fichas: %(contador)s/15"), { contador: contador }, true);
}

if (nome) {
    const boasVindas = document.getElementById("texto-boas-vindas");
    const final = document.getElementById("final");
    const usuario = nome.dataset.usuario;

    const modelo = gettext("Olá %(usuario)s, Seja bem-vindo ao D20HUB.");
    const [antes, depois] = modelo.split("%(usuario)s");
    const texto = antes + usuario + depois;
    const fimNome = antes.length + usuario.length;
    let i = 0;

    function digitar() {
        if (i < texto.length) {
            if (i < antes.length) {
                boasVindas.textContent += texto[i];

            } else if (i < fimNome) {
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
    input.placeholder = gettext("Nome da ficha");
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
                    gettext("Erro"),
                    gettext("Erro ao salvar o nome da ficha! Tente novamente.")
                );
            }
        });
    });

    const botoesDiv = document.createElement("div");
    botoesDiv.classList.add("botoesDiv");
    div.appendChild(botoesDiv);
        
    const acessarBtn = document.createElement("button");
    acessarBtn.innerHTML = '<i class="bi-file-earmark-text"></i> ' + gettext("Acessar");
    acessarBtn.classList.add("acessarBtn");
    botoesDiv.appendChild(acessarBtn);

    acessarBtn.addEventListener("click", () => {
        const nomeAtual = input.value.trim();
        if (nomeAtual) {
            window.location.href = `/fichas/${id}/ficha/`;
        } else {
            mostrarMensagem(
                gettext("Nome inválido"),
                gettext("Por favor, digite um nome para a ficha.")
            );
        }
    });
        
    const excluirBtn = document.createElement("button");
    excluirBtn.innerHTML = '<i class="bi bi-trash"></i> ' + gettext("Excluir");
    excluirBtn.classList.add("excluirBtn");
    botoesDiv.appendChild(excluirBtn);

    excluirBtn.addEventListener("click", () => {

        confirmarAcao(
            gettext("Excluir ficha"),
            gettext("Tem certeza que deseja excluir esta ficha?"),
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
                        atualizarContador();
                    } else {
                        mostrarMensagem(
                            gettext("Erro"),
                            gettext("Erro ao excluir ficha! Tente novamente.")
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
        atualizarContador();
    });
}

if (document.getElementById("fichasContainer")) {
    carregarFichas();
    const sistemaModal = document.getElementById("sistemaModal");

    document.getElementById("criarFicha").addEventListener("click", () => {
        if (contador >= 15) {
            mostrarMensagem(
                gettext("Limite atingido"),
                gettext("Você já possui o número máximo de 15 fichas.")
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
            gettext("Limpar fichas"),
            gettext("Tem certeza que deseja excluir todas as suas fichas?"),
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
                        atualizarContador();
                    } else {
                        mostrarMensagem(
                            gettext("Erro"),
                            gettext("Não foi possível limpar as fichas. Tente novamente.")
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
            atualizarContador();
        } else {
            mostrarMensagem(
                gettext("Erro"),
                data.mensagem || gettext("Não foi possível criar a ficha. Tente novamente.")
            );
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