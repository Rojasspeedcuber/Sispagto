import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Date, Numeric, ForeignKey, inspect
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import contextmanager

DATABASE_URL = "sqlite:///data/sispagto.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Credor(Base):
    __tablename__ = 'CREDOR'
    CREDOR_DOC = Column(String, primary_key=True)
    CREDOR_NOME = Column(String, nullable=False)

class Contrato(Base):
    __tablename__ = 'CONTRATO'
    CONTRATO_N = Column(String, primary_key=True)
    CREDOR_DOC = Column(String, ForeignKey('CREDOR.CREDOR_DOC'), nullable=False)
    CONTRATO_DATA_INI = Column(Date, nullable=False)
    CONTRATO_DATA_FIM = Column(Date, nullable=False)
    CONTRATO_VALOR = Column(Numeric, nullable=False)
    LISTA_ITENS_N = Column(Integer) # Coluna adicionada

class ProdutoServico(Base):
    __tablename__ = 'PRODUTOS_SERVICOS'
    PROD_SERV_N = Column(Integer, primary_key=True, autoincrement=True)
    PROD_SERV_DESCRICAO = Column(String, nullable=False)
    PROD_SERV_VALOR = Column(Numeric, nullable=False)

class Pagamento(Base):
    __tablename__ = 'PAGTO'
    PAGTO_ID = Column(Integer, primary_key=True, autoincrement=True)
    PAGTO_DATA = Column(Date, nullable=False)
    PAGTO_PERIODO = Column(String)
    PAGTO_VALOR = Column(Numeric, nullable=False)
    CREDOR_DOC = Column(String, ForeignKey('CREDOR.CREDOR_DOC'))
    CONTRATO_N = Column(String, ForeignKey('CONTRATO.CONTRATO_N'))
    PAGTO_TIPO = Column(String) 
    PAGTO_GRUPO = Column(String) # Coluna adicionada

def inicializar_banco():
    Base.metadata.create_all(bind=engine)

@contextmanager
def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

def table_exists(session, table_name):
    inspector = inspect(session.bind)
    return inspector.has_table(table_name)