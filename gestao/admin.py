from django.contrib import admin
from .models import Produto, Maquina, Receita, Venda, Movimentacao, Tarifa

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'preco', 'estoque_atual', 'tipo')
    search_fields = ('nome', 'id')

@admin.register(Venda)
class VendaAdmin(admin.ModelAdmin):
    list_display = ('id', 'data', 'total', 'pagamento')
    list_filter = ('pagamento', 'data')

admin.site.register(Maquina)
admin.site.register(Receita)
admin.site.register(Movimentacao)
admin.site.register(Tarifa)