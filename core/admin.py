# core/admin.py
from django.contrib import admin
from .models import (
    Credor,
    ProdutoServico,
    Contrato,
    ItemContrato,
    Fatura,
    NotaFiscal,
    Pagamento
)

# Classe para permitir adicionar Itens diretamente na página do Contrato
class ItemContratoInline(admin.TabularInline):
    model = ItemContrato
    extra = 1 # Quantidade de campos extras para adicionar novos itens

@admin.register(Contrato)
class ContratoAdmin(admin.ModelAdmin):
    inlines = [ItemContratoInline]
    list_display = ('contrato_n', 'credor', 'data_inicio', 'data_fim', 'valor_total')

@admin.register(Pagamento)
class PagamentoAdmin(admin.ModelAdmin):
    list_display = ('id', 'data', 'valor', 'contrato', 'fatura', 'nota_fiscal')
    list_filter = ('data', 'credor', 'contrato')


# Registro simples para os outros models
admin.site.register(Credor)
admin.site.register(ProdutoServico)
admin.site.register(Fatura)
admin.site.register(NotaFiscal)
