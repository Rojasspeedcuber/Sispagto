# src/database.py
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Date, Numeric, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

# --- CONFIGURAÇÃO DO BANCO DE DADOS ---
DATABASE_URL = "sqlite:///data/sispagto.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- DEFINIÇÃO DOS MODELOS (TABELAS) ---
# As classes abaixo mapeiam as tabelas descritas no PDF [cite: 4]

class Credor(Base):
    __tablename__ = 'CREDOR'
    CREDOR_DOC = Column(String, primary_key=True) # [cite: 16]
    CREDOR_NOME = Column(String, nullable=False) # [cite: 16]

class Contrato(Base):
    __tablename__ = 'CONTRATO'
    CONTRATO_N = Column(String, primary_key=True) # [cite: 18]
    CREDOR_DOC = Column(String, ForeignKey('CREDOR.CREDOR_DOC'), primary_key=True) # [cite: 18]
    CONTRATO_DATA_INI = Column(Date, nullable=False) # [cite: 18]
    CONTRATO_DATA_FIM = Column(Date, nullable=False) # [cite: 18]
    CONTRATO_VALOR = Column(Numeric, nullable=False) # [cite: 18]

# ... (Definição de todas as outras classes: Pagto, NF, Recibo, Fatura, Boleto, etc.)
# A estrutura seguirá as especificações das tabelas do PDF. [cite: 5, 7, 9, 11, 13, 19, 21, 23]

# --- FUNÇÃO DE INICIALIZAÇÃO ---
def inicializar_banco():
    """ Cria todas as tabelas no banco de dados se não existirem. """
    Base.metadata.create_all(bind=engine)

# --- FUNÇÕES CRUD (EXEMPLOS) ---
def get_session():
    return SessionLocal()

def cadastrar_credor(doc, nome):
    """ Cadastra um novo credor. [cite: 132] """
    db = get_session()
    novo_credor = Credor(CREDOR_DOC=doc, CREDOR_NOME=nome)
    db.add(novo_credor)
    db.commit()
    db.close()

def listar_credores():
    """ Retorna uma lista de todos os credores cadastrados. """
    db = get_session()
    credores = db.query(Credor).all()
    db.close()
    return credores

def cadastrar_pagamento(pagamento_data):
    """
    Cadastra um novo pagamento após validar as regras de negócio.
    Os dados do pagamento são recebidos em um dicionário ou objeto.
    [cite: 81]
    """
    # Lógica para adicionar na tabela PAGTO e, dependendo do tipo,
    # também nas tabelas NF, RECIBO, FATURA ou BOLETO.
    # [cite: 92, 93, 94, 95]
    pass

def get_relatorio_pagamentos(filtros):
    """
    Busca os dados de pagamentos aplicando os filtros e retorna um DataFrame.
    [cite: 153, 154]
    """
    # Query complexa que junta as tabelas PAGTO, CREDOR, CONTRATO, etc.,
    # para montar a planilha conforme especificado. [cite: 152]
    pass