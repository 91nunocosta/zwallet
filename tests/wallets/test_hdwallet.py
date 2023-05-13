import coinaddrng
import pytest

from zwallet.wallets.hdwallet import UnsupportedCurrency, create_hdwallet

MENEMONIC = (
    "sceptre capter séquence girafe absolu relatif fleur zoologie muscle "
    "sirop saboter parure"
)


def test_create_hdwallet():
    hdwallet = create_hdwallet("BTC")
    assert hdwallet.currency == "BTC"


def test_create_hdwallet_with_unsupported_currency():
    with pytest.raises(UnsupportedCurrency):
        create_hdwallet("unsupported")


def test_address():
    hdwallet = create_hdwallet("BTC")
    address = hdwallet.address(MENEMONIC, 0)
    result = coinaddrng.validate("btc", address)
    assert result.valid
    assert result.ticker == "btc"

    hdwallet = create_hdwallet("ETH")
    address = hdwallet.address(MENEMONIC, 1)
    result = coinaddrng.validate("eth", address)
    assert result.valid
    assert result.ticker == "eth"


def test_private_key():
    hdwallet = create_hdwallet("BTC")
    assert hdwallet.private_key(MENEMONIC, 0)
