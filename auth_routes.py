from fastapi import APIRouter, Depends, HTTPException
from models import Usuario, db # Importando tabela usuário
from dependences import pegar_sessao
from main import bcrypt_context
from schemas import UsuarioSchema
from sqlalchemy.orm import Session

auth_router = APIRouter(prefix='/auth', tags=['auth'])

@auth_router.get('/')
async def home():
    """
    Essa é a rota padrão de autenticação do nosso sistema. 
    """
    return {'mensagem': 'Você acessou a rota padrão de autenticação', 'autenticado': False}

@auth_router.post("/criar_usuario")
async def create_account(usuario_schema: UsuarioSchema, session: Session = Depends(pegar_sessao)):
    
    usuario = session.query(Usuario).filter(Usuario.email == usuario_schema.email).first()
    try:
        if usuario:
            raise HTTPException(status_code=400, detail='E-mail do usuário já cadastrado.')
        else:
            crypt_password = bcrypt_context.hash(usuario_schema.password)

            novo_usuario = Usuario(usuario_schema.name, usuario_schema.email, crypt_password, usuario_schema.status, usuario_schema.admin) # passar na ordem do db
            session.add(novo_usuario)
            session.commit()
            return {'mensagem': f'Email {usuario_schema.email} cadastrado com sucesso.'}
    except:
        raise HTTPException(status_code=400, detail='E-mail do usuário já cadastrado.')