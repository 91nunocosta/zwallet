import base64
import time
from datetime import timedelta

import pytest
from jose import jwe

from zwallet.jwt import InvalidJWToken, get_kdf


def test_jwt(salt, tokens):
    username = "user1"
    password = "pass1"

    token = tokens.create_access_token(
        username, password, expires_delta=timedelta(minutes=10), salt=salt
    )
    decoded_token = tokens.decode_access_token(token)

    assert decoded_token.sub == username

    kdf = get_kdf(salt)
    kdf.verify(
        password.encode(), base64.urlsafe_b64decode(decoded_token.encryption_key)
    )


def test_expired_token(salt, tokens):
    username = "user1"
    password = "pass1"

    token = tokens.create_access_token(
        username, password, salt=salt, expires_delta=timedelta(milliseconds=1)
    )

    time.sleep(1)

    with pytest.raises(InvalidJWToken):
        tokens.decode_access_token(token)


def test_decode_empty_token(tokens, jwe_key):
    jwe_token = jwe.encrypt("", jwe_key)

    with pytest.raises(InvalidJWToken):
        tokens.decode_access_token(jwe_token)
