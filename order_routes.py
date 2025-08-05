from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from dependences import pegar_sessao, authenticate_token
from models import Pedidos, Usuario, ItensPedidos
from schemas import ItemSchema, ResponseOrderSchema
from typing import List

order_router = APIRouter(prefix='/pedidos', tags=['pedidos'], dependencies=[Depends(authenticate_token)])

@order_router.get('/')
async def pedidos():
    """
    Essa é a rota padrão de pedidos do nosso sistema. Todas as rotas dos pedidos precisam ser autenticados.
    """
    return {'mensagem': 'Você acessou a rota de pedidos!'}
    
@order_router.post('/pedido')
async def criar_pedido(session: AsyncSession = Depends(pegar_sessao), usuario: Usuario = Depends(authenticate_token)):
    create_order = Pedidos(user_id = usuario.id)

    session.add(create_order)
    await session.commit()
    await session.refresh(create_order)

    return {
        'mensagem': 'Pedido criado com sucesso!',
        'id_pedido': f'ID do pedido: {create_order.id}',
        'status': create_order.status
    }


@order_router.post('/pedido/cancelar/{id_pedido}')
async def cancelar_pedido(id_pedido: int, session: AsyncSession = Depends(pegar_sessao), usuario: Usuario = Depends(authenticate_token)):
    result_order = await session.execute(select(Pedidos).where(Pedidos.id == id_pedido))
    order = result_order.scalars().first()
    result_user_id = await session.execute(select(Usuario).where(Usuario.id == usuario.id))
    user_id = result_user_id.scalars().first()

    if not user_id.admin and user_id.id != order.user_id: 
        raise HTTPException(status_code=401, detail='Usuário não possui permissão necessária.')
    elif not order:
        raise HTTPException(status_code=400, detail='Pedido não encontrado.')
    elif order.status == 'CANCELADO':
        raise HTTPException(status_code=401, detail='Pedido já foi cancelado em outro momento.')
    
    order.status = 'CANCELADO'
    await session.commit()
    await session.refresh(order)

    return {
        'mensagem': f'Pedido {order.id} foi cancelado com sucesso.',
        'order': order
        }

@order_router.get('/listar_pedidos')
async def listar_pedidos(session: AsyncSession = Depends(pegar_sessao), usuario: Usuario = Depends(authenticate_token)):
    if not usuario.admin:
        raise HTTPException(status_code=401, detail='Usuário não possui permissão necessária.')
    
    result_orders = await session.execute(select(Pedidos))
    orders = result_orders.scalars().all()

    return {
        'orders': orders
        }

@order_router.post('/pedido/adicionar_pedido/{id_pedido}')
async def adicionar_pedido(id_pedido: int, item_order_schema: ItemSchema, session: AsyncSession = Depends(pegar_sessao), usuario: Usuario = Depends(authenticate_token)):
    order_result = await session.execute(select(Pedidos).where(Pedidos.id == id_pedido))
    order = order_result.scalars().first()

    if not order:
        raise HTTPException(status_code=400, detail='Pedido não encontrado.')
    elif order.user_id != usuario.id and not usuario.admin:
        raise HTTPException(status_code=401, detail='Você não tem autorização para acessar esse pedido.')
    
    item_pedido = ItensPedidos(item_order_schema.quantity, item_order_schema.sabor, item_order_schema.tamanho, item_order_schema.preco_unitario, id_pedido)
    
    session.add(item_pedido)
    await order.price_calc(session)
    await session.commit()
    await session.refresh(item_pedido)
    await session.refresh(order)

    return {
        'mensagem': 'Pedido realizado com sucesso!',
        'order_id': order.id,
        'item_id': item_pedido.id,
        'price': order.preco
    }

@order_router.delete('/pedido/remover_item/{id_item}')
async def remover_pedido(id_item: int, session: AsyncSession = Depends(pegar_sessao), usuario: Usuario = Depends(authenticate_token)):
    result_item = await session.execute(select(ItensPedidos).where(ItensPedidos.id == id_item))
    order_items = result_item.scalars().first()

    if not order_items:
        raise HTTPException(status_code=400, detail='Item não encontrado')

    result_order = await session.execute(select(Pedidos).where(Pedidos.id == order_items.pedido))
    order = result_order.scalars().first()

    if order.user_id != usuario.id and not usuario.admin:
        raise HTTPException(status_code=401, detail='Você não tem autorização para remover esse item.')
    
    item_data = {
        'id': order_items.id,
        'sabor': order_items.sabor,
        'preco_unitario': order_items.preco_unitario,
        'quantidade': order_items.quantity,
        'valor_total': order_items.quantity * order_items.preco_unitario
    }

    await session.delete(order_items)
    await order.price_calc(session)
    await session.commit()

    return {
        'mensagem': 'Item deletado com sucesso!',
        'item': item_data
    }


@order_router.post('/pedido/finalizar_pedido/{id_pedido}')
async def finalizar_pedido(id_pedido: int, session: AsyncSession = Depends(pegar_sessao), usuario: Usuario = Depends(authenticate_token)):
    result = await session.execute(select(Pedidos).where(Pedidos.id == id_pedido))
    order = result.scalars().first()

    if not order:
        raise HTTPException(status_code=400, detail=f'Pedido {id_pedido} não encontrado.')
    elif not usuario.admin:
        raise HTTPException(status_code=401, detail='Você não tem autorização para finalizar esse pedido.')
    
    order.status = 'FINALIZADO'

    item_data = {
        'id': order.id,
        'status': order.status,
        'preço': order.preco
    }

    await session.commit()

    return {
        'mensagem': f'Pedido {item_data['id']} foi finalizado com sucesso.',
        'pedido': item_data
    }

@order_router.get('/pedido/{id_pedido}')
async def exibir_pedido(id_pedido: int, session: AsyncSession = Depends(pegar_sessao), usuario: Usuario = Depends(authenticate_token)):
    result = await session.execute(select(Pedidos).where(Pedidos.id == id_pedido))
    order = result.scalars().first()

    if not order:
        raise HTTPException(status_code=400, detail=f'Pedido {id_pedido} não encontrado.')
    elif not usuario.admin and usuario.id != order.user_id:
        raise HTTPException(status_code=401, detail='Você não tem autorização para finalizar esse pedido.')
    
    return {
        'quantidade_itens_pedido': len(order.items),
        'itens_pedido': order.items
    }

@order_router.get('/listar/pedidos-usuario', response_model=List[ResponseOrderSchema])
async def exibir_pedidos_usuario(session: AsyncSession = Depends(pegar_sessao), usuario: Usuario = Depends(authenticate_token)):
    result = await session.execute(select(Pedidos).where(Pedidos.user_id == usuario.id))
    user_orders = result.scalars().all()


    if not user_orders:
        raise HTTPException(status_code=400, detail=f'Não há nenhum pedido para listar.')

    return user_orders

    















