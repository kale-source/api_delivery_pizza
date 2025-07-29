from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dependences import pegar_sessao, authenticate_token
from schemas import PedidoSchema
from models import Pedidos, Usuario

order_router = APIRouter(prefix='/pedidos', tags=['pedidos'], dependencies=[Depends(authenticate_token)])

@order_router.get('/')
async def pedidos():
    """
    Essa é a rota padrão de pedidos do nosso sistema. Todas as rotas dos pedidos precisam ser autenticados.
    """
    return {'mensagem': 'Você acessou a rota de pedidos!'}
    
@order_router.post('/pedido')
async def criar_pedido(session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(authenticate_token)):
    # Falta definir pedidos, entre outros.
    create_order = Pedidos(user_id = usuario.id)

    session.add(create_order)
    session.commit()

    return {
        'mensagem': 'Pedido criado com sucesso!', 
        'id_pedido': f'ID do pedido: {create_order.id}',
        'id_usuario': usuario.id
        }

@order_router.post('/pedido/cancelar/{id_pedido}')
async def cancelar_pedido(id_pedido: int, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(authenticate_token)):
    order = session.query(Pedidos).filter(Pedidos.id == id_pedido).first()
    user_id = session.query(Usuario).filter(Usuario.id == usuario.id).first()

    if not user_id.admin and user_id.id != order.user_id: 
        raise HTTPException(status_code=401, detail='Usuário não possui permissão necessária.')
    elif not order:
        raise HTTPException(status_code=400, detail='Pedido não encontrado.')
    elif order.status == 'CANCELADO':
        raise HTTPException(status_code=401, detail='Pedido já foi cancelado em outro momento.')
    
    order.status = 'CANCELADO'
    session.commit()

    return {
        'mensagem': f'Pedido {order.id} foi cancelado com sucesso.',
        'order': order
        }





