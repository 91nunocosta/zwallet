import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from zwallet.auth.models import User
from zwallet.auth.router import Tokens, pwd_context
from zwallet.dependencies import get_auth_token


@pytest.fixture(name="password")
def password_fixture():
    return "pass"


@pytest.fixture(name="user")
def user_fixture(session: Session, password: str):
    hashed_password = pwd_context.hash(password)
    user = User(username="bob", password=hashed_password, salt=b"")
    session.add(user)
    session.commit()
    return user


def test_create_user(client: TestClient, session: Session):
    username = "bob"
    password = "pass"

    response = client.post(
        "/users",
        json={
            "username": username,
            "password": password,
        },
    )
    data = response.json()

    assert response.status_code == 201
    assert data.get("username") == username
    created_user = session.query(User).filter_by(username=data["username"]).first()
    assert created_user
    assert created_user.password != password


def test_create_repeated_user(user: User, client: TestClient):
    response = client.post(
        "/users",
        json={"username": user.username, "password": user.password},
    )
    assert response.status_code == 422


def test_successful_login(
    client: TestClient,
    tokens: Tokens,
    user: User,
    password: str,
):
    response = client.post(
        "/token",
        data={
            "username": user.username,
            "password": password,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data.get("token_type") == "bearer"
    jwe_token = data.get("access_token")
    token_payload = get_auth_token(tokens, jwe_token)
    assert token_payload.sub == user.username


def test_incorrect_user_login(client: TestClient, password: str):
    response = client.post(
        "/token",
        data={
            "username": "incorrect_user",
            "password": password,
        },
    )
    assert response.status_code == 401


def test_incorrect_password_login(client: TestClient, user: User):
    response = client.post(
        "/token",
        data={
            "username": user.username,
            "password": "incorrect_password",
        },
    )
    assert response.status_code == 401
