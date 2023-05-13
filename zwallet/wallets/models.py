from typing import Optional

from sqlmodel import Field, SQLModel


class Wallet(SQLModel, table=True):
    username: str = Field(primary_key=True)
    mnemonic: bytes


class Address(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(foreign_key="wallet.username")
    currency: str
    index: int
    address: str
