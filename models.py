from sqlalchemy import create_engine, Column, String, Integer, Boolean, Float, ForeignKey
from sqlalchemy.orm import declarative_base

# cria a conexão do seu banco de dados
db = create_engine('sqlite:///banco.db')

# cria a base do banco de dados
Base = declarative_base()

# criar as classes que vão ser as tabelas do banco
class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    name = Column('name', String, nullable=False)
    email = Column('email', String, nullable=False, unique=True)
    password = Column('password', String, nullable=False)
    status = Column('status', Boolean)
    admin = Column('admin', Boolean, default=False)

    def __init__(self, name, email, password, status=True, admin=False):
        self.name = name
        self.email = email
        self.password = password
        self.status = status
        self.admin = admin

class Pedidos(Base):
    __tablename__ = "pedidos"

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    status = Column('status', String, ) # pendente, cancelado, inicializado
    usuario = Column('usuario', ForeignKey('usuarios.id'))
    preco = Column('preco', Float, nullable=True)
    # itens = Column()

    def __init__(self, usuario, status="Pendente", preco=0):
        self.status = status
        self.usuario = usuario
        self.preco = preco

class ItensPedidos(Base):
    __tablename__ = 'itens_pedidos'

# executa a criação dos metadados do seu banco (cria efetivamente o banco de dados)

