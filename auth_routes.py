from fastapi import APIRouter, Depends, HTTPException
from models import Usuario, db # Importando tabela usuário
from dependences import pegar_sessao
from main import bcrypt_context

auth_router = APIRouter(prefix='/auth', tags=['auth'])

@auth_router.get('/')
async def home():
    """
    Essa é a rota padrão de autenticação do nosso sistema. 
    """
    return {'mensagem': 'Você acessou a rota padrão de autenticação', 'autenticado': False}

@auth_router.post("/criar_usuario")
async def create_account(email: str, password: str, name: str, session=Depends(pegar_sessao)):
    
    usuario = session.query(Usuario).filter(Usuario.email == email).first()
    try:
        if usuario:
            raise HTTPException(status_code=400, detail='E-mail do usuário já cadastrado.')
        else:
            crypt_password = bcrypt_context.hash(password)

            novo_usuario = Usuario(name, email, crypt_password) # passar na ordem do db
            session.add(novo_usuario)
            session.commit()
            return {'mensagem': f'Email {email} cadastrado com sucesso.'}
    except:
        raise HTTPException(status_code=400, detail='E-mail do usuário já cadastrado.')