from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from models import Usuario # Importando tabela usuário
from dependences import pegar_sessao, authenticate_token, get_current_user_optional
from main import bcrypt_context, ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY
from schemas import UsuarioSchema, LoginSchema
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from typing import Optional

auth_router = APIRouter(prefix='/auth', tags=['auth'])

def create_token(id_usuario, token_duration=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    # Token JWT
    
    expiration_date = datetime.now(timezone.utc) + token_duration
    dict_info = {"sub": str(id_usuario), 'exp': expiration_date} # Por padrão tem que deixar EXP para reconhecer que é um datetime

    encoded_jwt = jwt.encode(dict_info, key=SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

@auth_router.get('/')
async def home():
    """
    Essa é a rota padrão de autenticação do nosso sistema. 
    """
    return {
        'mensagem': 'Você acessou a rota padrão de autenticação', 'autenticado': False
        }

@auth_router.post("/criar_usuario")
async def create_account(usuario_schema: UsuarioSchema, session: AsyncSession = Depends(pegar_sessao), usuario_auth: Optional[Usuario] = Depends(get_current_user_optional)):
    
    if not usuario_auth and usuario_schema.admin:
        raise HTTPException(status_code=401, detail='Você não está autenticado, não é possivel criar uma conta admin.')
    elif usuario_auth:
        if not usuario_auth.admin and usuario_schema.admin:
            raise HTTPException(status_code=401, detail='Você não tem permissão de criar um usuário admin')
    
    result = await session.execute(select(Usuario).where(Usuario.email == usuario_schema.email))
    usuario = result.scalars().first() # Scalars transforma o resultado da consulta em objetos python

    try:
        if usuario:
            raise HTTPException(status_code=400, detail=f'E-mail do usuário já cadastrado. {usuario}')
        else:
            crypt_password = bcrypt_context.hash(usuario_schema.password)

            novo_usuario = Usuario(usuario_schema.name, usuario_schema.email, crypt_password, usuario_schema.status, usuario_schema.admin) # passar na ordem do db
            session.add(novo_usuario)
            await session.commit()
            return {
                'mensagem': f'Email {usuario_schema.email} cadastrado com sucesso.'
                }
    except:
        raise HTTPException(status_code=400, detail='E-mail do usuário já cadastrado.')

@auth_router.post("/login")
async def login(login_schema: LoginSchema, session: AsyncSession = Depends(pegar_sessao)):
    result = await session.execute(select(Usuario).where(Usuario.email == login_schema.email))
    usuario = result.scalars().first()

    if usuario:
        check_password = bcrypt_context.verify(login_schema.password, usuario.password)
        
        if check_password:
            access_token = create_token(usuario.id)
            refresh_token = create_token(usuario.id, timedelta(days=7))

            return {
                    'access_token': access_token, 
                    'refresh': refresh_token, 
                    'token_type': 'Bearer'
                    }
        else:
            raise HTTPException(status_code=400, detail='Email ou senha inválidos.')
    else:
        raise HTTPException(status_code=400, detail='Email ou senha inválidos.')

@auth_router.post("/login-form")
async def login(login_form: OAuth2PasswordRequestForm = Depends(), session: AsyncSession = Depends(pegar_sessao)):
    result = await session.execute(select(Usuario).where(Usuario.email == login_form.username))
    usuario = result.scalars().first()

    if usuario:
        check_password = bcrypt_context.verify(login_form.password, usuario.password)
        
        if check_password:
            access_token = create_token(usuario.id)

            return {
                    'access_token': access_token, 
                    'token_type': 'Bearer'
                    }
        else:
            raise HTTPException(status_code=400, detail='Email ou senha inválidos.')
    else:
        raise HTTPException(status_code=400, detail='Email ou senha inválidos.')

@auth_router.get("/refresh")
async def use_refresh_token(usuario: Usuario = Depends(authenticate_token)):
    access_token = create_token(usuario.id)

    return {
            'access_token': access_token, 
            'token_type': 'Bearer'
            }