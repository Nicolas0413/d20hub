import json
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_list_or_404, get_object_or_404, render
from django.contrib.auth.decorators import login_required

from sessoes.models import FichaSessao, Sala
from .models import Estatisticas, Ficha, Pericia, Habilidade, Item, Ataque, Inventario
from django.core.serializers.json import DjangoJSONEncoder
import traceback
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

# Dicts uteis

Modelos = {
    "ficha": Ficha,
    "habilidade": Habilidade,
    "ataque": Ataque,
    "pericia": Pericia,
    "item": Item
}

Paginas = {
    "detalhes": "detalhes.html",
    "ficha": "ficha.html",
    "habilidades": "habilidades.html",
    "inventario": "inventario.html",
    "pericias": "pericias.html"
}

Campos_Permitidos = {
    "ficha": ["visibilidade", "editabilidade", "nome", "personagem", "foto_personagem", "nex", "classe", "trilha", "origem", "patente", "anotacoes", "aparencia", "historia", "token_personagem", "estatisticas.forca", "estatisticas.agilidade", "estatisticas.vigor", "estatisticas.intelecto", "estatisticas.presenca", "estatisticas.pv_atual", "estatisticas.pv_maximos", "estatisticas.pe_atual", "estatisticas.pe_maximos", "estatisticas.sanidade_atual", "estatisticas.sanidade_maxima", "estatisticas.defesa", "estatisticas.esquiva", "estatisticas.bloqueio", "inventario.carga_atual", "inventario.carga_maxima", "inventario.cat1", "inventario.cat2", "inventario.cat3", "inventario.cat4"],
    "ataque": ["nome", "dano", "critico"],
    "pericia": ["nome", "descricao", "pagina", "dados", "bonus", "treinamento"],
    "habilidade": ["nome", "descricao", "pagina", "custo"],
    "item": ["nome", "categoria", "espaco", "descricao"],
    "imagem": ["foto_personagem", "token_personagem"]
}

# Funções uteis 

def salvar(request, campospermitidos, objeto):
    dados = json.loads(request.body)
    campo = dados.get('campo')
    valor = dados.get('valor')
    if campo not in campospermitidos:
        return {"status": False, "mensagem": "Campo Invalido."}
    if "." in campo: # Para campos relacionados" 
        relacao, campo = campo.split(".")
        if not hasattr(objeto, relacao): 
            return {"status": False, "mensagem": "Relação inválida."}
        objeto = getattr(objeto, relacao)
    # Garantir tipos corretos para campos numéricos de permissão
    if campo in ("visibilidade", "editabilidade"):
        try:
            valor = int(valor)
        except (TypeError, ValueError):
            return {"status": False, "mensagem": "Valor inválido para campo numérico."}

    setattr(objeto, campo, valor)
    objeto.save()
    try:
        valor_salvo = getattr(objeto, campo)
    except Exception:
        valor_salvo = None
    return {"status": True, "campo": campo, "valor": valor_salvo}

def lista_autorizados(objeto, permissao):
    if permissao not in ["visibilidade", "editabilidade"]:
        return []

    ficha = objeto if isinstance(objeto, Ficha) else getattr(objeto, "ficha", None)
    if ficha is None:
        return []

    valor_permissao = getattr(ficha, permissao)
    match valor_permissao:
        case 0:
            return [ficha.usuario.id]
        case 1:
            sessoes = FichaSessao.objects.filter(ficha=ficha)
            salas = [sessao.sala for sessao in sessoes]
            mestres = [sala.mestre.id for sala in salas]
            mestres.append(ficha.usuario.id)
            return mestres
        case 2:
            sessoes = FichaSessao.objects.filter(ficha=ficha)
            salas = [sessao.sala for sessao in sessoes]
            usuarios = {ficha.usuario.id}
            for sala in salas:
                usuarios.add(sala.mestre.id)
                usuarios.update(sala.jogadores.values_list("id", flat=True))
            return list(usuarios)
        case 3:
            return "publica"
        

def checar_permissao(request, objeto, permissao):
    usuarios_permitidos = lista_autorizados(objeto, permissao)
    if usuarios_permitidos == "publica":
        return True
    return request.user.id in usuarios_permitidos

def limpar_ficha(ficha_id):
    ficha = get_object_or_404(Ficha, id=ficha_id)       
    Pericia.objects.filter(ficha=ficha).delete()
    Habilidade.objects.filter(ficha=ficha).delete()
    Ataque.objects.filter(ficha=ficha).delete()
    Item.objects.filter(inventario__ficha=ficha).delete()
    return True

# Views

@login_required
def home_fichas_view(request):
    usuario = {'usuario': request.user.username}
    return render(request, 'fichas/home.html', usuario)

@login_required
def fichas_usuario_view(request):
    fichas = Ficha.objects.filter(usuario=request.user)
    vetor_fichas = [{"id": ficha.id, "nome": ficha.nome, "sistema": ficha.sistema} for ficha in fichas]
    return JsonResponse(vetor_fichas, safe=False, status=200)

@login_required
def criar_ficha_view(request):
    if request.method == 'POST':
        try:
            dados = json.loads(request.body or "{}")
        except json.JSONDecodeError:
            dados = {}
        sistema = dados.get("sistema", "ordem_paranormal")
        if sistema not in dict(Ficha.SISTEMAS):
            return JsonResponse({"status": False, "mensagem": "Sistema inválido."})
        ficha = Ficha.objects.create(usuario=request.user, nome="", sistema=sistema)
        Estatisticas.objects.create(ficha=ficha)
        Inventario.objects.create(ficha=ficha)
        return JsonResponse({"id": ficha.id, "nome": ficha.nome, "sistema": ficha.sistema, "status": True})
    return JsonResponse({"status": False, "mensagem": "Método inválido"})
    
@login_required
def limpar_fichas_view(request):
    if request.method == 'POST':
        Ficha.objects.filter(usuario=request.user).delete()
        return JsonResponse({"status": True})
    

# CRUD Fichas

@login_required
def criar_view(request, ficha_id, categoria):
    if request.method != 'POST':
        return JsonResponse ({"status": False, "mensagem": "Método invalido"})
    modelo = Modelos.get(categoria)
    if not modelo:
        return JsonResponse ({"status": False, "mensagem": "Categoria inexistente"})
    
    ficha = get_object_or_404(Ficha, id=ficha_id, usuario=request.user)
    if categoria == "item":
        modelo.objects.create(inventario=ficha.inventario)
        return JsonResponse({"status": True}) 
    modelo.objects.create(ficha=ficha)
    return JsonResponse({"status": True})

@login_required
def ler_view(request, ficha_id, categoria):
    ficha = get_object_or_404(Ficha, id=ficha_id)
    pagina = Paginas.get(categoria)

    if not pagina:
        return JsonResponse(
            {"status": False, "mensagem": "Não encontrada"},
            status=404
        )

    url = f'fichas/{ficha.sistema}/{pagina}'

    if not checar_permissao(request, ficha, "visibilidade"):
        return JsonResponse(
            {"status": False, "mensagem": "Não tem permissão de acesso"},
            status=403
        )

    pode_editar = checar_permissao(
        request,
        ficha,
        "editabilidade"
    )

    return render(request, url, {
        'ficha': ficha,
        'pode_editar': pode_editar
    })
    
@login_required
def salvar_view(request, categoria_id, categoria):
    if request.method != 'POST':
        return JsonResponse ({"status": False, "mensagem": "Método invalido"})
    mensagem = ""
    modelo = Modelos.get(categoria)
    if not modelo:
        return JsonResponse ({"status": False, "mensagem": "Categoria inexistente"})
    
    objeto = get_object_or_404(modelo, id=categoria_id)
    if not checar_permissao(request, objeto, "editabilidade"):
        return JsonResponse ({"status": False, "mensagem": "Permissão Negada"})
    
    campospermitidos = Campos_Permitidos.get(categoria, "")
    dados = salvar(request, campospermitidos, objeto)
    status = dados["status"]
    mensagem = dados.get("mensagem", "")
    resposta = {"status": status, "mensagem": mensagem}
    if status:
        # incluir campo/valor salvo para diagnóstico
        resposta['campo'] = dados.get('campo')
        resposta['valor'] = dados.get('valor')
    return JsonResponse (resposta)

@login_required
def salvar_imagem_view(request, ficha_id, categoria):
    if request.method != 'POST':
        return JsonResponse ({"status": False, "mensagem": "Método invalido"})
    ficha = get_object_or_404(Ficha, id=ficha_id, usuario=request.user)
    if categoria not in Campos_Permitidos.get("imagem", []):
        return JsonResponse({"status": False, "mensagem": "Categoria inválida."})
    foto = request.FILES.get(categoria)
    if not foto:
        return JsonResponse({"status": False, "mensagem": "Nenhuma foto enviada."})
    if not foto.content_type.startswith("image/"):
        return JsonResponse({"status": False, "mensagem": "Arquivo inválido."})
    campo = getattr(ficha, categoria)
    campo.save(foto.name, foto)
    return JsonResponse({"status": True})

@login_required
def excluir_view(request, categoria_id, categoria):
    if request.method != 'POST':
        return JsonResponse ({"status": False, "mensagem": "Método invalido"})
    modelo = Modelos.get(categoria)
    if not modelo:
        return JsonResponse ({"status": False, "mensagem": "Categoria inexistente"})
    objeto = get_object_or_404(modelo, id=categoria_id)
    if not checar_permissao(request, objeto, "editabilidade"):
        return JsonResponse ({"status": False, "mensagem": "Permissão Negada"})
    objeto.delete()
    return JsonResponse({"status": True})

@login_required
def exportar_view(request, ficha_id):
    ficha = get_object_or_404(Ficha, id=ficha_id, usuario=request.user)
    status = get_object_or_404(Estatisticas, ficha=ficha)
    inventario = get_object_or_404(Inventario, ficha=ficha)
    pericias = Pericia.objects.filter(ficha=ficha)
    habilidades = Habilidade.objects.filter(ficha=ficha)
    ataques = Ataque.objects.filter(ficha=ficha)
    itens = Item.objects.filter(inventario=ficha.inventario)
    
    dados_ficha = {"nome": ficha.nome, "personagem": ficha.personagem, "nex": ficha.nex, "classe": ficha.classe, "trilha": ficha.trilha, "origem": ficha.origem, "patente": ficha.patente, "anotacoes": ficha.anotacoes, "aparencia": ficha.aparencia, "historia": ficha.historia}
    dados = {"sistema": ficha.sistema, "dados_ficha": dados_ficha, "estatisticas": estatisticas, "pericias": pericias, "habilidades": habilidades, "ataques": ataques, "inventario": inventario, "itens": itens}
    estatisticas = {"forca": status.forca, "agilidade": status.agilidade, "vigor": status.vigor, "intelecto": status.intelecto, "presenca": status.presenca, "pv_atual": status.pv_atual, "pv_maximos": status.pv_maximos, "pe_atual": status.pe_atual, "pe_maximos": status.pe_maximos, "sanidade_atual": status.sanidade_atual, "sanidade_maxima": status.sanidade_maxima, "defesa": status.defesa, "esquiva": status.esquiva, "bloqueio": status.bloqueio}
    inventario = {"carga_atual": inventario.carga_atual, "carga_maxima": inventario.carga_maxima, "cat1": inventario.cat1, "cat2": inventario.cat2, "cat3": inventario.cat3, "cat4": inventario.cat4}
    pericias = list(pericias.values("nome", "descricao", "pagina", "dados", "treinamento", "bonus"))
    habilidades = list(habilidades.values("nome", "descricao", "pagina", "custo"))
    ataques = list(ataques.values("nome", "dano", "critico"))
    itens = list(itens.values("nome", "categoria", "espaco", "descricao"))

    dados = {"dados_ficha": dados_ficha, "estatisticas": estatisticas, "pericias": pericias, "habilidades": habilidades,"ataques": ataques, "inventario": inventario, "itens": itens}

    arquivo = HttpResponse(json.dumps(dados, indent=4, cls=DjangoJSONEncoder, ensure_ascii=False), content_type='application/json')
    arquivo['Content-Disposition'] = ('attachment; filename="ficha.json"')

    return arquivo


@login_required
def importar_view(request, ficha_id):
    try:
        if request.method != "POST":
            return JsonResponse({"status": False, "mensagem": "Método inválido."})
        ficha = get_object_or_404(Ficha, id=ficha_id, usuario=request.user)
        arquivo = request.FILES.get("arquivo")
        if not arquivo:
            return JsonResponse({"status": False, "mensagem": "Nenhum arquivo enviado."})
        if not isinstance(dados, dict):
            return JsonResponse({"status": False, "mensagem": "Formato de JSON inválido."})
        try:
            conteudo = arquivo.read()
            if isinstance(conteudo, bytes):
                conteudo = conteudo.decode("utf-8-sig")
            dados = json.loads(conteudo)
        except json.JSONDecodeError:
            return JsonResponse({"status": False, "mensagem": "JSON inválido."})

        if not isinstance(dados, dict):
            return JsonResponse({"status": False, "mensagem": "Formato de JSON inválido."})
        
        if dados.get("sistema", "ordem_paranormal") != ficha.sistema:
            return JsonResponse({"status": False, "mensagem": "Este arquivo é de outro sistema."})
        
        def campos_validos(modelo):
            return {field.name for field in modelo._meta.concrete_fields if not field.primary_key}

        def aplicar_dados(objeto, origem, excluir=()):
            campos = campos_validos(objeto.__class__)
            for campo, valor in origem.items():
                if campo in campos and campo not in excluir:
                    setattr(objeto, campo, valor)

        dados_ficha = dados.get("dados_ficha", {})
        if not isinstance(dados_ficha, dict):
            return JsonResponse({"status": False, "mensagem": "Bloco 'dados_ficha' inválido."})

        aplicar_dados(ficha, dados_ficha, excluir=("usuario", "sistema"))
        ficha.usuario = request.user
        ficha.save()

        dados_estatisticas = dados.get("estatisticas", {})
        if not isinstance(dados_estatisticas, dict):
            return JsonResponse({"status": False, "mensagem": "Bloco 'estatisticas' inválido."})

        estatisticas, _ = Estatisticas.objects.get_or_create(ficha=ficha)
        aplicar_dados(estatisticas, dados_estatisticas, excluir=("ficha",))
        estatisticas.ficha = ficha
        estatisticas.save()

        dados_inventario = dados.get("inventario", {})
        if not isinstance(dados_inventario, dict):
            return JsonResponse({"status": False, "mensagem": "Bloco 'inventario' inválido."})

        inventario, _ = Inventario.objects.get_or_create(ficha=ficha)
        aplicar_dados(inventario, dados_inventario, excluir=("ficha",))
        inventario.ficha = ficha
        inventario.save()

        listas = {
            "pericias": (Pericia, "ficha"),
            "habilidades": (Habilidade, "ficha"),
            "ataques": (Ataque, "ficha"),
            "itens": (Item, "inventario"),
        }

        contagens = {}

        for chave_json, (modelo, relacao) in listas.items():
            itens = dados.get(chave_json, [])
            if itens is None:
                itens = []

            if not isinstance(itens, list):
                return JsonResponse({"status": False, "mensagem": f"Bloco '{chave_json}' inválido."})

            if relacao == "ficha":
                modelo.objects.filter(ficha=ficha).delete()
            elif relacao == "inventario":
                modelo.objects.filter(inventario=inventario).delete()

            novos = []

            for entrada in itens:
                if not isinstance(entrada, dict):
                    return JsonResponse({"status": False, "mensagem": f"Item inválido dentro de '{chave_json}'."})

                campos = {field.name for field in modelo._meta.concrete_fields if not field.primary_key}

                entrada_filtrada = {campo: valor for campo, valor in entrada.items() if campo in campos and campo not in ("id", "ficha", "inventario")}

                if relacao == "ficha":
                    novos.append(modelo(ficha=ficha, **entrada_filtrada))
                else:
                    novos.append(modelo(inventario=inventario, **entrada_filtrada))

            if novos:
                modelo.objects.bulk_create(novos)

            contagens[chave_json] = len(novos)

        return JsonResponse({"status": True, "mensagem": "Ficha importada com sucesso.", "contagens": contagens})
    except Exception as e:
        print(traceback.format_exc())
        return JsonResponse({"status": False, "mensagem": f"Erro ao importar ficha: {str(e)}"})





