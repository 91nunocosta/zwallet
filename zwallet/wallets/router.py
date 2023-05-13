from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

import zwallet.wallets.wallets
from zwallet.dependencies import AuthToken, Session

from .hdwallet import UnsupportedCurrency
from .models import Address, Wallet
from .wallets import AddressNotFound, WalletAlredyExists, WalletNotFound

router = APIRouter()


class AddressRequest(BaseModel):
    currency: str


def get_wallets_manager(session: Session) -> zwallet.wallets.wallets.WalletsManager:
    return zwallet.wallets.wallets.WalletsManager(session)


WalletsManager = Annotated[
    zwallet.wallets.wallets.WalletsManager, Depends(get_wallets_manager)
]


@router.post("/wallets", response_model=Wallet, status_code=status.HTTP_201_CREATED)
def create_wallet(auth_token: AuthToken, wallets: WalletsManager):
    try:
        return wallets.add_wallet(auth_token.sub, auth_token.encryption_key)
    except WalletAlredyExists as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="User {username} already have a wallet.",
        ) from error


@router.post("/addresses", response_model=Address, status_code=status.HTTP_201_CREATED)
def create_address(
    request: AddressRequest, auth_token: AuthToken, wallets: WalletsManager
):
    try:
        return wallets.add_address(
            request.currency, auth_token.sub, auth_token.encryption_key
        )
    except UnsupportedCurrency as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Unsupported currency: {request.currency}",
        ) from error
    except WalletNotFound as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"User {auth_token.sub} doesn't have a wallet yet",
        ) from error


@router.get("/addresses", response_model=List[Address])
def list_addresses(auth_token: AuthToken, wallets: WalletsManager):
    return wallets.get_all_addresses(auth_token.sub)


@router.get("/addresses/{identifier}", response_model=Address)
def get_address(identifier: int, auth_token: AuthToken, wallets: WalletsManager):
    try:
        address = wallets.get_addresss(identifier)
    except AddressNotFound as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from error

    if address.username != auth_token.sub:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    return address
