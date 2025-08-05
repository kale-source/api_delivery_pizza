from sqlalchemy import Column, String, Integer, Boolean, Float, ForeignKey, select
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

# criando engine do db
db = create_async_engine('sqlite+aiosqlite:///./banco.db', echo=True)

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
    status = Column('status', String) # PENDENTE, CANCELADO, FINALIZADO '''ChoiceType(choices=STATUS_PEDIDOS)'''
    user_id = Column('user_id', ForeignKey('usuarios.id'))
    preco = Column('preco', Float, default=0)
    items = relationship('ItensPedidos', cascade='all, delete', lazy='selectin')

    def __init__(self, user_id, status="PENDENTE", preco=0):
        self.status = status
        self.user_id = user_id
        self.preco = preco
    
    async def price_calc(self, session: AsyncSession):
        preco_total = 0

        result = await session.execute(select(ItensPedidos).where(ItensPedidos.pedido == self.id))
        items = result.scalars().all()

        for item in items:
            preco_item = item.preco_unitario * item.quantity
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

