# gestao/models.py
from django.db import models

class Produto(models.Model):
    id = models.CharField(primary_key=True, max_length=50)
    nome = models.TextField()
    tipo = models.CharField(max_length=20, blank=True, null=True)
    grupo = models.CharField(max_length=50, blank=True, null=True)
    unidade = models.CharField(max_length=10, blank=True, null=True)
    preco = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    custo = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    estoque_atual = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    estoque_fundo = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    estoque_minimo = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    controla_estoque = models.BooleanField(default=True)
    # JSONField requer PostgreSQL
    codigos_barras = models.JSONField(default=list, blank=True, null=True) 
    categoria = models.TextField(blank=True, null=True)
    data_cadastro = models.DateField(blank=True, null=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        db_table = 'produtos'
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'

    def __str__(self):
        return f"{self.id} - {self.nome}"

class Maquina(models.Model):
    id = models.CharField(primary_key=True, max_length=50)
    nome = models.TextField(blank=True, null=True)
    potencia_w = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    gas_kg_h = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)

    class Meta:
        db_table = 'maquinas'
        verbose_name = 'Máquina'
        verbose_name_plural = 'Máquinas'

    def __str__(self):
        return self.nome or self.id

class Tarifa(models.Model):
    chave = models.CharField(primary_key=True, max_length=50)
    valor = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)

    class Meta:
        db_table = 'tarifas'

    def __str__(self):
        return f"{self.chave}: {self.valor}"

class Receita(models.Model):
    id_produto = models.OneToOneField(Produto, models.DO_NOTHING, db_column='id_produto', primary_key=True)
    nome = models.TextField(blank=True, null=True)
    rendimento = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    tempo_preparo = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    margem_lucro = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    imposto_perc = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    custo_insumos = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    custo_maquinas = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    custo_mao_obra = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    custo_total_lote = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    custo_unitario = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    ingredientes = models.JSONField(blank=True, null=True)
    maquinas_uso = models.JSONField(blank=True, null=True)

    class Meta:
        db_table = 'receitas'

class Movimentacao(models.Model):
    # O Django gerencia o ID autoincrement automaticamente se omitido, 
    # mas como mapeamos do banco existente, vamos deixar explicito se necessário
    data = models.DateTimeField(blank=True, null=True)
    cod_produto = models.ForeignKey(Produto, models.DO_NOTHING, db_column='cod_produto', blank=True, null=True)
    nome_produto = models.TextField(blank=True, null=True)
    qtd = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    tipo = models.CharField(max_length=50, blank=True, null=True)
    motivo = models.TextField(blank=True, null=True)
    usuario = models.CharField(max_length=50, blank=True, null=True)
    saldo_anterior = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    saldo_novo = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)

    class Meta:
        db_table = 'movimentacoes'

class Venda(models.Model):
    data = models.DateTimeField(blank=True, null=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    pagamento = models.CharField(max_length=50, blank=True, null=True)
    operador = models.CharField(max_length=50, blank=True, null=True)
    itens = models.JSONField()

    class Meta:
        db_table = 'vendas'