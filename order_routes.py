from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from dependences import pegar_sessao
from schemas import PedidoSchema
from models import Pedidos

order_router = APIRouter(prefix='/pedidos', tags=['pedidos'])

@order_router.get('/')
async def pedidos():
    """
    Essa é a rota padrão de pedidos do nosso sistema. Todas as rotas dos pedidos precisam ser autenticados.
    """
    return {'mensagem': 'Você acessou a rota de pedidos!'}
    
@order_router.post('/pedido')
async def criar_pedido(pedido_schema: PedidoSchema, session: Session = Depends(pegar_sessao)):
    criar_pedido = Pedidos(user_id=pedido_schema.user_id)

    session.add(criar_pedido)
    session.commit()

    return {'mensagem': 'Pedido criado com sucesso!', 'id_pedido': f'ID do pedido: {criar_pedido.id}'}




