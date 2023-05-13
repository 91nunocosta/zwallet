import abc

import hdwallet
import hdwallet.cryptocurrencies


class UnsupportedCurrency(Exception):
    pass


# We will add new HDWallet subclasses when we need to add support to a new currency
class HDWallet(abc.ABC):
    def __init__(self, currency: str):
        self.currency = currency
        self._create_hdwallet_backend()

    @abc.abstractmethod
    def _create_hdwallet_backend(self):
        ...  # pragma: no cover

    def private_key(self, _mnemonic: str, _index: int) -> str:  # type: ignore
        ...  # pragma: no cover

    def address(self, _mnemonic: str, _index: int) -> str:  # type: ignore
        ...  # pragma: no cover


class HDWallet1(HDWallet):
    def _create_hdwallet_backend(self):
        self._hdwallet = hdwallet.HDWallet(symbol=self.currency)

    def private_key(self, mnemonic: str, index: int) -> str:
        self._hdwallet.from_mnemonic(mnemonic)
        self._hdwallet.from_index(index)
        return self._hdwallet.private_key()

    def address(self, mnemonic: str, index: int) -> str:
        self._hdwallet.from_mnemonic(mnemonic)
        self._hdwallet.from_index(index)
        return self._hdwallet.p2pkh_address()

    @staticmethod
    def is_supported(currency: str) -> bool:
        try:
            hdwallet.cryptocurrencies.get_cryptocurrency(currency)
            return True
        except ValueError:
            return False


# class HDWallet2:
#    ...


def create_hdwallet(currency: str):
    if HDWallet1.is_supported(currency):
        return HDWallet1(currency)

        # see the supported currencies here:
        # https://github.com/meherett/python-hdwallet/blob/ecade4b46edadfef3db132f190d444a8c4640ddb/hdwallet/cryptocurrencies.py#L6751

    # elif currency == "CURRENCY_SYMBOL":
    #   return HDWallet2

    raise UnsupportedCurrency(currency)
