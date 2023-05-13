import pytest
from fastapi import HTTPException, status
from jose import jwe, jwt

from zwallet.dependencies import Tokens, get_auth_token, get_session


def test_get_session() -> None:
    assert get_session()


def test_get_auth_token(token: str, username: str, encryption_key: str, tokens: Tokens):
    auth_token = get_auth_token(tokens, token)

    assert auth_token.sub == username
    assert auth_token.encryption_key == encryption_key


def test_get_invalid_auth_token(jwe_key, username, encryption_key, tokens: Tokens):
    with pytest.raises(HTTPException) as error:
        jwt_token = jwt.encode(
            {"sub": username, "encryption_key": encryption_key}, key=""
        )
        jwe_token = jwe.encrypt(jwt_token, jwe_key).decode()
        get_auth_token(tokens, jwe_token)

    assert error.value.status_code == status.HTTP_401_UNAUTHORIZED

    with pytest.raises(HTTPException) as error:
        jwe_token = jwe.encrypt("invalid token", jwe_key).decode()
        get_auth_token(tokens, jwe_token)

    assert error.value.status_code == status.HTTP_401_UNAUTHORIZED
