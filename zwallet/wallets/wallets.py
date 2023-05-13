from typing import List

import sqlalchemy.exc
from cryptography.fernet import Fernet
from hdwallet.utils import generate_mnemonic
from sqlmodel import Session

from .hdwallet import create_hdwallet
from .models import Address, Wallet


class AddressNotFound(Exception):
    pass


class WalletNotFound(Exception):
    pass


class WalletAlredyExists(Exception):
    pass


class WalletsManager:
    def __init__(self, session: Session) -> None:
        self.session = session

    def _encrypt(self, plaitext: str, encryption_key: str) -> bytes:
        fernet = Fernet(encryption_key)
        return fernet.encrypt(plaitext.encode())

    def _decrypt(self, encrypted_data: bytes, encryption_key: str) -> str:
        fernet = Fernet(encryption_key)
        return fernet.decrypt(encrypted_data).decode()

    def get_mnemonic(self, username: str, encryption_key: str) -> str:
        try:
            wallet = self.session.query(Wallet).filter_by(username=username).one()
            return self._decrypt(wallet.mnemonic, encryption_key)
        except sqlalchemy.exc.NoResultFound as error:
            raise WalletNotFound(username) from error

    def add_wallet(self, username: str, encryption_key: str) -> Wallet:
        if self.session.query(Wallet).filter_by(username=username).first():
            raise WalletAlredyExists(username)

        mnemonic = generate_mnemonic()
        wallet = Wallet(
            username=username, mnemonic=self._encrypt(mnemonic, encryption_key)
        )
        self.session.add(wallet)
        self.session.commit()
        return wallet

    def add_address(self, currency: str, username: str, encryption_key: str) -> Address:
        mnemonic = self.get_mnemonic(username, encryption_key)
        index = (
            self.session.query(Address)
            .filter_by(username=username, currency=currency)
            .count()
        )
        address_value = create_hdwallet(currency).address(mnemonic, index)
        address = Address(
            currency=currency,
            username=username,
            index=index,
            address=address_value,
        )
        self.session.add(address)
        self.session.commit()
        self.session.refresh(address)
        return address

    def get_all_addresses(self, username: str) -> List[Address]:
        return self.session.query(Address).filter_by(username=username).all()

    def get_addresss(self, address_id: int) -> Address:
        try:
            return self.session.query(Address).filter_by(id=address_id).one()
        except sqlalchemy.exc.NoResultFound as error:
            raise AddressNotFound(address_id) from error

    def get_private_key(self, address_id: int, encryption_key: str) -> str:
        address = self.get_addresss(address_id)
        mnemonic = self.get_mnemonic(address.username, encryption_key)
        return create_hdwallet(address.currency).private_key(mnemonic, address.index)
