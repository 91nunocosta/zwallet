import os
from datetime import timedelta

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from zwallet.api import create_api
from zwallet.dependencies import get_session
from zwallet.jwt import Tokens, generate_encryption_key


@pytest.fixture(name="jwe_key")
def jwe_key_fixture():
    return "D9F8273A5B1C6E9D4F7A2B5C8E3F6A9D"


@pytest.fixture(name="jwt_key")
def jwt_key_fixture():
    return "A3B5D8E7C6F4A1B9D5E8C3A7B2F5D8E6"


@pytest.fixture(name="tokens")
def tokens_fixture(jwt_key, jwe_key):
    return Tokens(jwt_key=jwt_key, jwe_key=jwe_key)


@pytest.fixture(name="username")
def username_fixture():
    return "user1"


@pytest.fixture(name="password")
def password_fixture():
    return "password1"


@pytest.fixture(name="username_unauth")
def username_unauth_fixtue():
    return "unauth_user"


@pytest.fixture(name="salt")
def salt_fixture():
    return os.urandom(16)


@pytest.fixture(name="encryption_key")
def encryption_key_fixture(password, salt):
    return generate_encryption_key(password, salt)


@pytest.fixture(name="token")
def auth_token_fixture(username: str, password: str, salt: bytes, tokens: Tokens):
    access_token_expires = timedelta(minutes=60)
    access_token = tokens.create_access_token(
        username=username,
        password=password,
        salt=salt,
        expires_delta=access_token_expires,
    )
    return access_token


@pytest.fixture(name="session")
def session_fixture() -> Session:  # pylint: disable=unused-argument
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    return Session(engine)


@pytest.fixture(autouse=True)
def env_fixture(monkeypatch, jwt_key, jwe_key):
    monkeypatch.setenv("JWT_KEY", jwt_key, prepend=False)
    monkeypatch.setenv("JWE_KEY", jwe_key, prepend=False)
    monkeypatch.setenv("AUTH_EXP", 30, prepend=False)

    monkeypatch.setenv("DATABASE_URL", "sqlite://", prepend=False)


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    api = create_api()
    api.dependency_overrides[get_session] = get_session_override
    client = TestClient(api)
    yield client
    api.dependency_overrides.clear()
