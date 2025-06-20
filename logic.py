# logic.py

from sqlalchemy.orm import Session
from models import Pagto, Contrato, Credor, ProdutosServicos, NF, Recibo, Fatura, Boleto
from datetime import datetime

def create_credor(db: Session, credor_doc: str, nome: str):
    """
    Creates a new Credor. 
    """
    db_credor = Credor(credor_doc=credor_doc, credor_nome=nome)
    db.add(db_credor)
    db.commit()
    db.refresh(db_credor)
    return db_credor

def create_produto_servico(db: Session, descricao: str, valor: int):
    """
    Creates a new Produto/Servico. 
    """
    db_prod_serv = ProdutosServicos(prod_serv_descricao=descricao, prod_serv_valor=valor)
    db.add(db_prod_serv)
    db.commit()
    db.refresh(db_prod_serv)
    return db_prod_serv

def create_contrato(db: Session, contrato_n: str, credor_doc: str, data_ini: str, data_fim: str, valor: int):
    """
    Creates a new Contrato, validating business rules. 
    """
    # Business Rule Validation 
    if datetime.strptime(data_fim, '%Y-%m-%d') < datetime.strptime(data_ini, '%Y-%m-%d'):
        raise ValueError("Contract end date cannot be earlier than the start date.")

    db_contrato = Contrato(
        contrato_n=contrato_n,
        credor_doc=credor_doc,
        contrato_data_ini=data_ini,
        contrato_data_fim=data_fim,
        contrato_valor=valor
    )
    db.add(db_contrato)
    db.commit()
    db.refresh(db_contrato)
    return db_contrato

def create_payment(db: Session, data: str, periodo: str, valor: int, prod_serv_n: int, prod_serv_qtd: int,
                   credor_doc: str, contrato_n: str = None, grupo: int = None, tipo_pagamento: str = None,
                   doc_n: str = None, doc_data: str = None):
    """
    Creates a new Pagamento and associated document (NF, Recibo, etc.). 
    """
    pagto_data_dt = datetime.strptime(data, '%Y-%m-%d')

    if contrato_n:
        contrato = db.query(Contrato).filter(Contrato.contrato_n == contrato_n).first()
        if not contrato:
            raise ValueError("Contract not found.")

        # Business Rule Validation: Payment date must be within contract validity 
        if not (datetime.strptime(contrato.contrato_data_ini, '%Y-%m-%d') <= pagto_data_dt <= datetime.strptime(contrato.contrato_data_fim, '%Y-%m-%d')):
            raise ValueError("Payment date is outside the contract's validity period.")

        # Business Rule Validation: Payment value cannot exceed remaining contract value 
        pagamentos_sum = db.query(Pagto).filter(Pagto.contrato_n == contrato_n).with_entities(Pagto.pagto_valor).all()
        total_pago = sum(p[0] for p in pagamentos_sum)
        if valor > (contrato.contrato_valor - total_pago):
            raise ValueError("Payment value exceeds the available amount in the contract.")

    db_pagto = Pagto(
        pagto_data=data,
        pagto_periodo=periodo,
        pagto_valor=valor,
        prod_serv_n=prod_serv_n,
        prod_serv_qtd=prod_serv_qtd,
        credor_doc=credor_doc,
        contrato_n=contrato_n,
        pagto_grupo=grupo
    )

    # Handle different payment types 
    if tipo_pagamento == 'nf':
        if not all([doc_n, doc_data]): raise ValueError("NF number and date are required.")
        db_nf = NF(nf_n=doc_n, credor_doc=credor_doc, nf_data=doc_data, contrato_n=contrato_n)
        db.add(db_nf)
        db_pagto.nf_n = db_nf.nf_n
    elif tipo_pagamento == 'recibo':
        if not doc_data: raise ValueError("Recibo date is required.")
        db_recibo = Recibo(credor_doc=credor_doc, recibo_data=doc_data)
        db.add(db_recibo)
        db.flush()
        db_pagto.recibo_n = db_recibo.recibo_n
    elif tipo_pagamento == 'fatura':
        if not all([contrato_n, doc_data]): raise ValueError("Contract and Fatura date are required.")
        db_fatura = Fatura(contrato_n=contrato_n, credor_doc=credor_doc, fatura_data=doc_data)
        db.add(db_fatura)
        db.flush()
        db_pagto.fatura_n = db_fatura.fatura_n
    elif tipo_pagamento == 'boleto':
        if not doc_data: raise ValueError("Boleto date is required.")
        db_boleto = Boleto(contrato_n=contrato_n, credor_doc=credor_doc, boleto_data=doc_data)
        db.add(db_boleto)
        db.flush()
        db_pagto.boleto_n = db_boleto.boleto_n

    db.add(db_pagto)
    db.commit()
    db.refresh(db_pagto)
    return db_pagto