from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dependences import pegar_sessao, authenticate_token
from models import Pedidos, Usuario, ItensPedidos
from schemas import ItemSchema

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

@order_router.get('/listar_pedidos')
async def listar_pedidos(session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(authenticate_token)):
    if not usuario.admin:
        raise HTTPException(status_code=401, detail='Usuário não possui permissão necessária.')
    
    orders = session.query(Pedidos).all()

    return {
        'orders': orders
        }

@order_router.post('/pedido/adicionar_pedido/{id_pedido}')
async def adicionar_pedido(id_pedido: int, item_order_schema: ItemSchema, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(authenticate_token)):
    order = session.query(Pedidos).filter(Pedidos.id == id_pedido).first()

    if not order:
        raise HTTPException(status_code=400, detail='Pedido não encontrado.')
    elif order.user_id != usuario.id and not usuario.admin:
        raise HTTPException(status_code=401, detail='Você não tem autorização para acessar esse pedido.')
    
    item_pedido = ItensPedidos(item_order_schema.quantity, item_order_schema.sabor, item_order_schema.tamanho, item_order_schema.preco_unitario, id_pedido)
    
    session.add(item_pedido)
    order.price_calc()
    session.commit()

    return {
        'mensagem': 'Pedido realizado com sucesso!',
        'order_id': order.id,
        'price': order.preco
    }

@order_router.delete('/pedido/remover_item/{id_item}')
async def remover_pedido(id_item: int, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(authenticate_token)):
    order_items = session.query(ItensPedidos).filter(ItensPedidos.id == id_item).first()

    if not order_items:
        raise HTTPException(status_code=400, detail='Item não encontrado')

    order = session.query(Pedidos).filter(Pedidos.id == order_items.pedido).first()

    if order.user_id != usuario.id and not usuario.admin:
        raise HTTPException(status_code=401, detail='Você não tem autorização para remover esse item.')
    
    session.delete(order_items)
    order.price_calc()
    session.commit()

    return {
        'mensagem': 'Item deletado com sucesso!',
        'order_id': order.id,
        'itens_pedido': order_items
    }














