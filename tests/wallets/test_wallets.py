import coinaddrng
import pytest

from zwallet.wallets.models import Address, Wallet
from zwallet.wallets.wallets import (
    AddressNotFound,
    WalletAlredyExists,
    WalletNotFound,
    WalletsManager,
)


@pytest.fixture(name="wallets")
def wallets_manager_fixture(session):
    return WalletsManager(session)


def test_add_wallet(wallets: WalletsManager, encryption_key: str):
    username = "newuser"
    wallet = wallets.add_wallet(username, encryption_key)

    assert wallet.username == username
    assert len(wallet.mnemonic) > 30

    assert wallets.session.query(Wallet).filter_by(username=username).one()


def test_add_repeated_wallet(
    wallets: WalletsManager, username: str, encryption_key: str
):
    with pytest.raises(WalletAlredyExists):
        wallets.add_wallet(username, encryption_key)


def test_get_mnemonic(
    wallets: WalletsManager, username: str, encryption_key: str, mnemonic: str
):
    assert wallets.get_mnemonic(username, encryption_key) == mnemonic


def test_get_mnemonic_for_user_without_wallet(
    wallets: WalletsManager, encryption_key: str
):
    with pytest.raises(WalletNotFound):
        wallets.get_mnemonic("user_without_wallet", encryption_key)


def test_add_address(
    wallets: WalletsManager, username: str, encryption_key: str
) -> None:
    address = wallets.add_address("BTC", username, encryption_key)

    assert address.currency == "BTC"
    assert address.username == username
    validation = coinaddrng.validate("btc", address.address)
    assert validation.valid
    assert validation.ticker == "btc"
    assert wallets.session.query(Address).filter_by(id=address.id).one() == address


def test_add_address_indexes(
    wallets: WalletsManager, username: str, encryption_key: str
):
    # Note that the wallet's database has no ETH address for the user
    # Index must start with 0
    previous_address = None

    for i in range(3):
        address = wallets.add_address("ETH", username, encryption_key)

        assert address.address != previous_address

        assert address.index == i

        previous_address = address.address


def test_list_addresses(wallets: WalletsManager, username: str, address: Address):
    assert wallets.get_all_addresses(username) == [address]


def test_get_address(wallets: WalletsManager, address: Address):
    address_id: int = address.id  # type: ignore
    assert wallets.get_addresss(address_id) == address


def test_get_non_existing_address(wallets: WalletsManager):
    with pytest.raises(AddressNotFound):
        wallets.get_addresss(1000)


def test_get_private_key(
    wallets: WalletsManager, address: Address, encryption_key: str
):
    address_id: int = address.id  # type: ignore

    key1 = wallets.get_private_key(address_id, encryption_key)
    key2 = wallets.get_private_key(address_id, encryption_key)

    assert isinstance(key1, str)
    assert isinstance(key2, str)

    # ensures private key retrieval is deterministic
    assert key1 == key2


def test_get_private_key_for_non_existing(wallets: WalletsManager, encryption_key: str):
    with pytest.raises(AddressNotFound):
        wallets.get_private_key(1000, encryption_key)
