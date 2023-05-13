from pydantic import BaseSettings, Field

KEY_SIZE = 32


class Settings(BaseSettings):
    database_url: str = Field(min_length=3)
    jwt_key: str = Field(min_length=KEY_SIZE, max_length=KEY_SIZE)
    jwe_key: str = Field(min_length=KEY_SIZE, max_length=KEY_SIZE)
    auth_exp: int
