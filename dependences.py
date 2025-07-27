from fastapi import Depends, HTTPException
from sqlalchemy.orm import sessionmaker, Session
from models import db, Usuario
from jose import jwt, JWTError
from main import SECRET_KEY, ALGORITHM, oauth2_schema

def pegar_sessao():
    try:
        Session = sessionmaker(bind=db)
        session = Session()
        yield session
    finally:
        session.close()

def authenticate_token(token: str = Depends(oauth2_schema), session: Session = Depends(pegar_sessao)):
    try:
        dict_info = jwt.decode(token, key=SECRET_KEY, algorithms=ALGORITHM)
        id_usuario = int(dict_info.get('sub'))
    except JWTError as e:
        print(e)
        raise HTTPException(status_code=401, detail='Acesso negado, verifique a validade do token.')

    usuario = session.query(Usuario).filter(Usuario.id == id_usuario).first()

    if not usuario:
        raise HTTPException(status_code=401, detail='Acesso inválido.')
    else:
        return usuario