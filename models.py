# models.py

from sqlalchemy import (Column, Integer, String, MetaData,
                        ForeignKey, Table, create_engine)
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Credor(Base):
    __tablename__ = 'CREDOR'
    credor_doc = Column('CREDOR_DOC', String, primary_key=True)
    credor_nome = Column('CREDOR_NOME', String, nullable=False)

class ProdutosServicos(Base):
    __tablename__ = 'PRODUTOS_SERVICOS'
    prod_serv_n = Column('PROD_SERV_N', Integer, primary_key=True)
    prod_serv_descricao = Column('PROD_SERV_DESCRICAO', String, nullable=False)
    prod_serv_valor = Column('PROD_SERV_VALOR', Integer, nullable=False)

class Contrato(Base):
    __tablename__ = 'CONTRATO'
    contrato_n = Column('CONTRATO_N', String, primary_key=True)
    credor_doc = Column('CREDOR_DOC', String, ForeignKey('CREDOR.CREDOR_DOC'), primary_key=True)
    contrato_data_ini = Column('CONTRATO_DATA_INI', String, nullable=False)
    contrato_data_fim = Column('CONTRATO_DATA_FIM', String, nullable=False)
    contrato_valor = Column('CONTRATO_VALOR', Integer, nullable=False)
    lista_itens_n = Column('LISTA_ITENS_N', Integer, ForeignKey('LISTA_ITENS.LISTA_ITENS_N'))
    credor = relationship("Credor")

class Aditivos(Base):
    __tablename__ = 'ADITIVOS'
    aditivo_n = Column('ADITIVO_N', Integer, primary_key=True)
    contrato_n = Column('CONTRATO_N', String, ForeignKey('CONTRATO.CONTRATO_N'), primary_key=True)
    credor_doc = Column('CREDOR_DOC', String, ForeignKey('CREDOR.CREDOR_DOC'), primary_key=True)
    lista_itens_n = Column('LISTA_ITENS_N', Integer, ForeignKey('LISTA_ITENS.LISTA_ITENS_N'))
    aditivo_data_ini = Column('ADITIVO_DATA_INI', String)
    aditivo_data_fim = Column('ADITIVO_DATA_FIM', String)
    aditivo_valor = Column('ADITIVO_VALOR', Integer)
    contrato = relationship("Contrato")

class ListaItens(Base):
    __tablename__ = 'LISTA_ITENS'
    lista_itens_n = Column('LISTA_ITENS_N', Integer, primary_key=True)
    prod_serv_n = Column('PROD_SERV_N', Integer, ForeignKey('PRODUTOS_SERVICOS.PROD_SERV_N'))
    prod_serv_qtd = Column('PROD_SERV_QTD', Integer, nullable=False)
    produto_servico = relationship("ProdutosServicos")

class NF(Base):
    __tablename__ = 'NF'
    nf_n = Column('NF_N', String, primary_key=True)
    contrato_n = Column('CONTRATO_N', String, ForeignKey('CONTRATO.CONTRATO_N'))
    credor_doc = Column('CREDOR_DOC', String, ForeignKey('CREDOR.CREDOR_DOC'), primary_key=True)
    nf_data = Column('NF_DATA', String, nullable=False)
    credor = relationship("Credor")

class Recibo(Base):
    __tablename__ = 'RECIBO'
    recibo_n = Column('RECIBO_N', Integer, primary_key=True)
    credor_doc = Column('CREDOR_DOC', String, ForeignKey('CREDOR.CREDOR_DOC'), nullable=False)
    recibo_data = Column('RECIBO_DATA', String, nullable=False)
    credor = relationship("Credor")

class Fatura(Base):
    __tablename__ = 'FATURA'
    fatura_n = Column('FATURA_N', Integer, primary_key=True)
    contrato_n = Column('CONTRATO_N', String, ForeignKey('CONTRATO.CONTRATO_N'), nullable=False)
    credor_doc = Column('CREDOR_DOC', String, ForeignKey('CREDOR.CREDOR_DOC'), nullable=False)
    fatura_data = Column('FATURA_DATA', String, nullable=False)
    credor = relationship("Credor")

class Boleto(Base):
    __tablename__ = 'BOLETO'
    boleto_n = Column('BOLETO_N', Integer, primary_key=True)
    contrato_n = Column('CONTRATO_N', String, ForeignKey('CONTRATO.CONTRATO_N'))
    credor_doc = Column('CREDOR_DOC', String, ForeignKey('CREDOR.CREDOR_DOC'), nullable=False)
    boleto_data = Column('BOLETO_DATA', String, nullable=False)
    credor = relationship("Credor")

class Pagto(Base):
    __tablename__ = 'PAGTO'
    pagto_id = Column('PAGTO_ID', Integer, primary_key=True)
    pagto_data = Column('PAGTO_DATA', String, nullable=False)
    pagto_periodo = Column('PAGTO_PERIODO', String, nullable=False)
    pagto_grupo = Column('PAGTO_GRUPO', Integer)
    pagto_valor = Column('PAGTO_VALOR', Integer, nullable=False)
    prod_serv_n = Column('PROD_SERV_N', Integer, ForeignKey('PRODUTOS_SERVICOS.PROD_SERV_N'), nullable=False)
    prod_serv_qtd = Column('PROD_SERV_QTD', Integer, nullable=False)
    contrato_n = Column('CONTRATO_N', String, ForeignKey('CONTRATO.CONTRATO_N'))
    credor_doc = Column('CREDOR_DOC', String, ForeignKey('CREDOR.CREDOR_DOC'), nullable=False)
    nf_n = Column('NF_N', String, ForeignKey('NF.NF_N'))
    recibo_n = Column('RECIBO_N', Integer, ForeignKey('RECIBO.RECIBO_N'))
    fatura_n = Column('FATURA_N', Integer, ForeignKey('FATURA.FATURA_N'))
    boleto_n = Column('BOLETO_N', Integer, ForeignKey('BOLETO.BOLETO_N'))

    credor = relationship("Credor")
    produto_servico = relationship("ProdutosServicos")
    contrato = relationship("Contrato")
    nf = relationship("NF")
    recibo = relationship("Recibo")
    fatura = relationship("Fatura")
    boleto = relationship("Boleto")


if __name__ == '__main__':
    from database import engine
    # This will create all tables in the database
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")