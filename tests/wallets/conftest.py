from datetime import timedelta
from typing import List

import pytest
from cryptography.fernet import Fernet
from hdwallet.utils import generate_mnemonic
from sqlmodel import Session

from zwallet.jwt import Tokens
from zwallet.wallets.models import Address, Wallet


@pytest.fixture(name="username_no_wallet")
def username_no_wallet_fixture():
    return "user_no_wallet"


@pytest.fixture(name="password_no_wallet")
def password_no_wallet_fixture():
    return "password4"


@pytest.fixture(name="token_no_wallet")
def auth_token_without_wallet_fixture(
    username_no_wallet: str, password_no_wallet: str, salt: bytes, tokens: Tokens
):
    access_token_expires = timedelta(minutes=60)
    access_token = tokens.create_access_token(
        username=username_no_wallet,
        password=password_no_wallet,
        salt=salt,
        expires_delta=access_token_expires,
    )
    return access_token


@pytest.fixture(name="mnemonic")
def mnemonic_fixture():
    return generate_mnemonic()


@pytest.fixture(name="wallets")
def wallets_fixture(username, username_unauth, mnemonic, encryption_key):
    frenet = Fernet(encryption_key)
    encrypted_mnemonic = frenet.encrypt(mnemonic.encode())
    return [
        Wallet(username=username, mnemonic=encrypted_mnemonic)
        for username in [username, username_unauth]
    ]


@pytest.fixture(name="address")
def address_fixture(username: str):
    return Address(
        id=1,
        currency="BTC",
        username=username,
        index=0,
        address="2N3kfQkYDH48Z4ZR88uay tLHNVbNJowjTym",
    )


@pytest.fixture(name="unauth_address")
def unauth_address_fixture():
    return Address(
        id=2,
        currency="ETH",
        address="0x71C7656EC7ab88b098defB751B7401B5f6d8976F",
        username="unauth_user",
        index=0,
    )


@pytest.fixture(name="addresses")
def addresses_fixture(address: Address, unauth_address: Address):
    return [address, unauth_address]


@pytest.fixture(name="session")
def session_fixture(
    session: Session,
    addresses: List[Address],
    wallets: List[Wallet],
):
    for wallet in session.query(Wallet).all():
        session.delete(wallet)
    for wallet in wallets:
        session.add(wallet)

    for address in session.query(Address).all():
        session.delete(address)
    for address in addresses:
        session.add(address)

    session.commit()

    return session
