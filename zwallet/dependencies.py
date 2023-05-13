from functools import lru_cache
from typing import Annotated

import sqlmodel
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

import zwallet.jwt
import zwallet.settings
from zwallet.jwt import InvalidJWToken


@lru_cache()
def get_settings():
    return zwallet.settings.Settings()


Settings = Annotated[zwallet.settings.Settings, Depends(get_settings)]


@lru_cache()
def get_engine():
    return sqlmodel.create_engine(
        get_settings().database_url,
        echo=True,
        connect_args={"check_same_thread": False},
    )


@lru_cache()
def get_session():
    engine = get_engine()
    with sqlmodel.Session(engine) as session:
        return session


Session = Annotated[sqlmodel.Session, Depends(get_session)]


def get_tokens(conf: Settings):
    return zwallet.jwt.Tokens(jwt_key=conf.jwt_key, jwe_key=conf.jwe_key)


Tokens = Annotated[zwallet.jwt.Tokens, Depends(get_tokens)]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_auth_token(
    tokens: Tokens,
    token: Annotated[str, Depends(oauth2_scheme)],
):
    try:
        return tokens.decode_access_token(token)
    except InvalidJWToken as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from error


AuthToken = Annotated[zwallet.jwt.AuthToken, Depends(get_auth_token)]
