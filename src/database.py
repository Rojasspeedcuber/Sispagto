import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Date, Numeric, ForeignKey, inspect, PrimaryKeyConstraint
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import contextmanager

# Define o caminho do banco de dados na pasta 'data'
DATABASE_URL = "sqlite:///data/sispagto.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- Definição de Todas as Tabelas ---

class Credor(Base):
    __tablename__ = 'CREDOR'
    CREDOR_DOC = Column(String, primary_key=True)
    CREDOR_NOME = Column(String, nullable=False)

class ProdutoServico(Base):
    __tablename__ = 'PRODUTOS_SERVICOS'
    PROD_SERV_N = Column(Integer, primary_key=True, autoincrement=True)
    PROD_SERV_DESCRICAO = Column(String, nullable=False)
    PROD_SERV_VALOR = Column(Numeric, nullable=False)

class ListaItens(Base):
    __tablename__ = 'LISTA_ITENS'
    __table_args__ = (PrimaryKeyConstraint('LISTA_ITENS_N', 'PROD_SERV_N'),)
    LISTA_ITENS_N = Column(Integer, nullable=False)
    PROD_SERV_N = Column(Integer, ForeignKey('PRODUTOS_SERVICOS.PROD_SERV_N'), nullable=False)
    LISTA_ITENS_QTD = Column(Integer)
    
class Contrato(Base):
    __tablename__ = 'CONTRATO'
    CONTRATO_N = Column(String, primary_key=True)
    CREDOR_DOC = Column(String, ForeignKey('CREDOR.CREDOR_DOC'), nullable=False)
    CONTRATO_DATA_INI = Column(Date, nullable=False)
    CONTRATO_DATA_FIM = Column(Date, nullable=False)
    CONTRATO_VALOR = Column(Numeric, nullable=False)
    LISTA_ITENS_N = Column(Integer)

class Aditivo(Base):
    __tablename__ = 'ADITIVOS'
    __table_args__ = (PrimaryKeyConstraint('ADITIVO_N', 'CONTRATO_N'),)
    ADITIVO_N = Column(Integer, nullable=False)
    CONTRATO_N = Column(String, ForeignKey('CONTRATO.CONTRATO_N'), nullable=False)
    ADITIVO_TIPO = Column(String)
    ADITIVO_DATA_INI = Column(Date)
    ADITIVO_DATA_FIM = Column(Date)
    ADITIVO_VALOR = Column(Numeric)

class NF(Base):
    __tablename__ = 'NF'
    NF_ID = Column(Integer, primary_key=True, autoincrement=True) # Chave primária autoincrementada
    NF_N = Column(String) # Permite duplicatas
    NF_DATA = Column(Date)
    NF_VALOR = Column(Numeric)

class Recibo(Base):
    __tablename__ = 'RECIBO'
    RECIBO_N = Column(Integer, primary_key=True)
    RECIBO_DATA = Column(Date)
    RECIBO_VALOR = Column(Numeric)

class Fatura(Base):
    __tablename__ = 'FATURA'
    FATURA_N = Column(Integer, primary_key=True)
    FATURA_DATA = Column(Date)
    FATURA_VALOR = Column(Numeric)

class Boleto(Base):
    __tablename__ = 'BOLETO'
    BOLETO_N = Column(Integer, primary_key=True)
    BOLETO_DATA_VENC = Column(Date)
    BOLETO_VALOR = Column(Numeric)

class Pagamento(Base):
    __tablename__ = 'PAGTO'
    PAGTO_ID = Column(Integer, primary_key=True, autoincrement=True)
    PAGTO_DATA = Column(Date, nullable=False)
    PAGTO_PERIODO = Column(String)
    PAGTO_VALOR = Column(Numeric, nullable=False)
    PAGTO_GRUPO = Column(String)
    PAGTO_TIPO = Column(String)
    CREDOR_DOC = Column(String, ForeignKey('CREDOR.CREDOR_DOC'))
    CONTRATO_N = Column(String, ForeignKey('CONTRATO.CONTRATO_N'))
    PROD_SERV_N = Column(Integer, ForeignKey('PRODUTOS_SERVICOS.PROD_SERV_N'))
    PROD_SERV_QTD = Column(Integer)
    NF_N = Column(String) # Não é chave estrangeira para permitir flexibilidade
    RECIBO_N = Column(Integer)
    FATURA_N = Column(Integer)
    BOLETO_N = Column(Integer)

# --- Funções do Banco de Dados ---

def inicializar_banco():
    """Cria todas as tabelas definidas no metadado do Base."""
    # Apaga e recria o banco de dados para aplicar as novas estruturas de chave primária
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

@contextmanager
def get_session():
    """Fornece uma sessão transacional para o banco de dados."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

def table_exists(session, table_name):
    """Verifica se uma tabela existe no banco de dados."""
    inspector = inspect(session.bind)
    return inspector.has_table(table_name)