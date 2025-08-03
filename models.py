from sqlalchemy import create_engine, Column, String, Integer, Boolean, Float, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy_utils.types import ChoiceType

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

    # STATUS_PEDIDOS =  (
    #     ('PENDENTE', 'PENDENTE'),
    #     ('CANCELADO', 'CANCELADO'),
    #     ('FINALIZADO', 'FINALIZADO')
    # )

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    status = Column('status', String) # PENDENTE, CANCELADO, FINALIZADO '''ChoiceType(choices=STATUS_PEDIDOS)'''
    user_id = Column('user_id', ForeignKey('usuarios.id'))
    preco = Column('preco', Float, nullable=True)
    items = relationship('ItensPedidos', cascade='all, delete')

    def __init__(self, user_id, status="PENDENTE", preco=0):
        self.status = status
        self.user_id = user_id
        self.preco = preco
    
    def price_calc(self):
        preco_total = 0
        for items in self.items:
            preco_item = items.preco_unitario * items.quantity
            preco_total += preco_item
        
        self.preco = preco_total

class ItensPedidos(Base):
    __tablename__ = 'itens_pedidos'
    
    id = Column('id', Integer, primary_key=True, autoincrement=True)
    quantity = Column('quantity', Integer, default=1)
    sabor = Column('sabor', String)
    tamanho = Column('tamanho', String)
    preco_unitario = Column('preco_unitario', Float, default=0)
    pedido = Column('pedido', ForeignKey('pedidos.id'))

    def __init__(self, quantity, sabor, tamanho, preco_unitario, pedido):
        self.quantity = quantity
        self.sabor = sabor
        self.tamanho = tamanho
        self.preco_unitario = preco_unitario
        self.pedido = pedido

