from django.db import models
from django.conf import settings

# Modelos mais independentes primeiro

class Credor(models.Model):
    credor_doc = models.CharField(max_length=18, primary_key=True, verbose_name="Documento do Credor (CNPJ/CPF)")
    credor_nome = models.CharField(max_length=255, verbose_name="Nome do Credor")

    def __str__(self):
        return f"{self.credor_nome} ({self.credor_doc})"

class ProdutoServico(models.Model):
    # Django cria um 'id' autoincremental por padrão (PROD_SERV_N)
    descricao = models.CharField(max_length=255, verbose_name="Descrição")
    valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor")

    def __str__(self):
        return self.descricao

class Contrato(models.Model):
    contrato_n = models.CharField(max_length=50, primary_key=True, verbose_name="Número do Contrato")
    credor = models.ForeignKey(Credor, on_delete=models.PROTECT, verbose_name="Credor")
    data_inicio = models.DateTimeField(verbose_name="Data de Início")
    data_fim = models.DateTimeField(verbose_name="Data de Fim")
    valor_total = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Valor Total")
    # A relação com itens será feita via ManyToManyField para maior flexibilidade
    itens = models.ManyToManyField(ProdutoServico, through='ItemContrato', verbose_name="Itens do Contrato")

    def __str__(self):
        return self.contrato_n

class ItemContrato(models.Model):
    """
    Este é o modelo 'through' para a relação N-N entre Contrato e ProdutoServico.
    Ele representa a tabela LISTA_ITENS do diagrama de uma forma mais idiomática no Django.
    """
    contrato = models.ForeignKey(Contrato, on_delete=models.CASCADE)
    produto_servico = models.ForeignKey(ProdutoServico, on_delete=models.PROTECT, verbose_name="Produto/Serviço")
    quantidade = models.IntegerField(default=1)

    class Meta:
        unique_together = ('contrato', 'produto_servico') # Garante que um produto não seja adicionado duas vezes ao mesmo contrato

    def __str__(self):
        return f"{self.quantidade}x {self.produto_servico.descricao} no Contrato {self.contrato.contrato_n}"


class Fatura(models.Model):
    fatura_n = models.CharField(max_length=50, primary_key=True, verbose_name="Número da Fatura")
    contrato = models.ForeignKey(Contrato, on_delete=models.PROTECT, verbose_name="Contrato")
    # O credor já está no contrato, mas mantendo como no diagrama:
    credor = models.ForeignKey(Credor, on_delete=models.PROTECT, verbose_name="Credor")
    data_emissao = models.DateTimeField(verbose_name="Data de Emissão")

    def __str__(self):
        return self.fatura_n

class NotaFiscal(models.Model):
    nf_n = models.CharField(max_length=50, primary_key=True, verbose_name="Número da NF")
    contrato = models.ForeignKey(Contrato, on_delete=models.PROTECT, verbose_name="Contrato")
    credor = models.ForeignKey(Credor, on_delete=models.PROTECT, verbose_name="Credor")
    data = models.DateTimeField(verbose_name="Data")

    def __str__(self):
        return self.nf_n

# ... outros modelos como Aditivo, Recibo, Boleto podem ser criados de forma similar ...

class Pagamento(models.Model):
    # Django cria um 'id' autoincremental (PAGTO_ID)
    data = models.DateTimeField(verbose_name="Data do Pagamento")
    periodo = models.CharField(max_length=50, verbose_name="Período de Referência")
    grupo = models.IntegerField(null=True, blank=True, verbose_name="Grupo")
    valor = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Valor Pago")

    # Relacionamentos (ForeignKey)
    # Definidos como opcionais (null=True, blank=True) pois um pagamento pode
    # estar associado a apenas um desses documentos.
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    credor = models.ForeignKey(Credor, on_delete=models.PROTECT, verbose_name="Credor")
    contrato = models.ForeignKey(Contrato, on_delete=models.PROTECT, verbose_name="Contrato")
    fatura = models.ForeignKey(Fatura, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Fatura")
    nota_fiscal = models.ForeignKey(NotaFiscal, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Nota Fiscal")
    # Adicione outros relacionamentos conforme necessário (Boleto, Recibo, etc.)

    def __str__(self):
        return f"Pagamento de {self.valor} em {self.data.strftime('%d/%m/%Y')}"
