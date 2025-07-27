from fastapi import APIRouter, Depends, HTTPException
from models import Usuario # Importando tabela usuário
from dependences import pegar_sessao
from main import bcrypt_context
from schemas import UsuarioSchema, LoginSchema
from sqlalchemy.orm import Session

auth_router = APIRouter(prefix='/auth', tags=['auth'])

def create_token(id_usuario):
    token = 'asdi7gafd80h923j8941j2asiodhgioasduhg'+f'{id_usuario}'
    return token

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

@auth_router.post("/login")
async def login(login_schema: LoginSchema, session: Session = Depends(pegar_sessao)):
    usuario = session.query(Usuario).filter(Usuario.email == login_schema.email).first()

    if usuario:
        check_password = bcrypt_context.verify(login_schema.password, usuario.password)
        
        if check_password:
            access_token = create_token(usuario.id)

            return {'access_token': access_token, 'token_type': 'Bearer'}
        
            # retornar token necessário
        else:
            raise HTTPException(status_code=400, detail='Email ou senha inválidos.')
    else:
        raise HTTPException(status_code=400, detail='Email ou senha inválidos.')