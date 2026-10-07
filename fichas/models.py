from django.db import models
from django.conf import settings


  
class Ficha(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="fichas")
    visibilidade = models.IntegerField(choices=[(0, 'Privada'), (1, 'Mestre'), (2, 'Sala'), (3, 'Pública')], default=0)
    editabilidade = models.IntegerField(choices=[(0, 'Privada'), (1, 'Mestre'), (2, 'Sala'), (3, 'Pública')], default=0)
    nome = models.CharField(max_length=64, default="")
    personagem = models.CharField(max_length=64, default="Nome do personagem")
    foto_personagem = models.ImageField(upload_to='fichas/foto_personagem/', default='foto_personagem/personagem')
    nex = models.IntegerField(null=True, blank=True, default=40)
    classe = models.CharField(max_length=32, default="Combatente")
    trilha = models.CharField(max_length=32, default="Aniquilador")
    origem = models.CharField(max_length=32, default="Acadêmico")
    patente = models.CharField(max_length=32, default="Recruta")
    tamanho = models.CharField(max_length=16, default="Médio")
    anotacoes = models.TextField(default="Anotações gerais sobre o personagem e missões")
    aparencia = models.TextField(default="Descrição física do personagem como: gênero, idade, altura etc.")
    historia = models.TextField(default="História do personagem (de onde veio, qual seu objetivo etc.)")
    token_personagem = models.ImageField(upload_to='fichas/token_personagem/', default='token_personagem/token')
    SISTEMAS = [('ordem_paranormal', 'Ordem Paranormal'), ('tormenta20', 'Tormenta 20')]
    sistema = models.CharField(max_length=32, choices=SISTEMAS, default='ordem_paranormal')
    def __str__(self):
        return self.nome

class Estatisticas(models.Model):
    ficha = models.OneToOneField(Ficha, on_delete=models.CASCADE, related_name="estatisticas")
    forca = models.IntegerField(default=1)
    agilidade = models.IntegerField(default=1)
    vigor = models.IntegerField(default=1)
    intelecto = models.IntegerField(default=1)
    presenca = models.IntegerField(default=1)
    carisma = models.IntegerField(default=1)
    pv_atual = models.IntegerField(null=True, blank=True, default=1)
    pv_maximos = models.IntegerField(null=True, blank=True, default=1)
    pe_atual = models.IntegerField(null=True, blank=True, default=1)
    pe_maximos = models.IntegerField(null=True, blank=True, default=1)
    sanidade_atual = models.IntegerField(null=True, blank=True, default=1)
    sanidade_maxima = models.IntegerField(null=True, blank=True, default=1)
    defesa = models.IntegerField(null=True, blank=True, default=0)
    esquiva = models.IntegerField(null=True, blank=True, default=0)
    bloqueio = models.IntegerField(null=True, blank=True, default=0)

    def __str__(self):
        return f"Estatísticas de {self.ficha.nome}"

class Pericia(models.Model):
    ficha = models.ForeignKey(Ficha, on_delete=models.CASCADE, related_name="pericias")
    nome = models.CharField(max_length=128, default="")
    descricao = models.TextField(default="")
    pagina = models.CharField(max_length=128, default="")
    dados = models.IntegerField(null=True, blank=True, default=1)
    ATRIBUTOS = [("FOR", "FOR"), ("DES", "DES"), ("CON", "CON"), ("INT", "INT"), ("SAB", "SAB"), ("CAR", "CAR")]
    atributo = models.CharField(max_length=3, choices=ATRIBUTOS, default="FOR")
    treinamento = models.CharField(max_length=32, default="")
    bonus = models.IntegerField(null=True, blank=True, default=0)

    def __str__(self):
        return self.nome
    
class Ataque(models.Model):
    ficha = models.ForeignKey(Ficha, on_delete=models.CASCADE, related_name="ataques")
    nome = models.CharField(max_length=32, default="Ataque")
    dano = models.CharField(max_length=16, default="")
    critico = models.CharField(max_length=16, default="20 x2")

    def __str__(self):
        return self.nome

class Habilidade(models.Model):
    ficha = models.ForeignKey(Ficha, on_delete=models.CASCADE, related_name="habilidades")
    nome = models.CharField(max_length=128, default="")
    descricao = models.TextField(default="")
    pagina = models.CharField(max_length=128, default="")
    custo = models.CharField(max_length=128, default="")

    def __str__(self):
        return self.nome
    
class Inventario(models.Model):
    ficha = models.OneToOneField(Ficha, on_delete=models.CASCADE, related_name="inventario")
    carga_atual = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, default=0)
    carga_maxima = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, default=0)
    cat1 = models.IntegerField(null=True, blank=True, default=0)
    cat2 = models.IntegerField(null=True, blank=True, default=0)
    cat3 = models.IntegerField(null=True, blank=True, default=0)
    cat4 = models.IntegerField(null=True, blank=True, default=0)

    def __str__(self):
        return f"Inventário de {self.ficha.nome}"

class Item(models.Model):
    inventario = models.ForeignKey('Inventario', on_delete=models.CASCADE, related_name="itens")
    nome = models.CharField(max_length=128, default="Nome")
    espaco = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, default=1)
    categoria = models.CharField(max_length=32, default="0")
    descricao = models.TextField(default="")

    def __str__(self):
        return self.nome

    
    
