from fastapi import Depends, HTTPException
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import Usuario, db
from jose import jwt, JWTError
from main import SECRET_KEY, ALGORITHM, oauth2_schema, oauth2_schema_optional
from typing import Optional

async def pegar_sessao():
    try:
        AsyncSessionLocal = sessionmaker(bind=db, class_=AsyncSession, expire_on_commit=True)
        session = AsyncSessionLocal()
        yield session
    finally:
        await session.close()

async def authenticate_token(token: str = Depends(oauth2_schema), session: AsyncSession = Depends(pegar_sessao)):
    try:
        dict_info = jwt.decode(token, key=SECRET_KEY, algorithms=ALGORITHM)
        id_usuario = int(dict_info.get('sub'))
    except JWTError as e:
        raise HTTPException(status_code=401, detail='Acesso negado, verifique a validade do token.')

    result = await session.execute(select(Usuario).where(Usuario.id == id_usuario))
    usuario = result.scalars().first()

    if not usuario:
        raise HTTPException(status_code=401, detail='Acesso inválido.')
    else:
        return usuario

async def get_current_user_optional(token: Optional[str] = Depends(oauth2_schema_optional), session: AsyncSession = Depends(pegar_sessao)) -> Optional[Usuario]:

    if not token:
        return None

    try:
        dict_info = jwt.decode(token, key=SECRET_KEY, algorithms=ALGORITHM)
        id_usuario = int(dict_info.get('sub'))
    except JWTError:
        return None
    
    result = await session.execute(select(Usuario).where(Usuario.id == id_usuario))
    usuario = result.scalars().first()


    if not usuario:
        raise HTTPException(status_code=401, detail='Acesso inválido.')
    else:
        return usuario