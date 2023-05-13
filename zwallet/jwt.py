import base64
from datetime import datetime, timedelta

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from jose import JWTError, jwe, jwt
from pydantic import BaseModel


class AuthToken(BaseModel):
    sub: str
    encryption_key: str


class InvalidJWToken(Exception):
    pass


def get_kdf(salt):
    return PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )


def generate_encryption_key(password: str, salt: bytes):
    kdf = get_kdf(salt)
    key = kdf.derive(password.encode())
    return base64.urlsafe_b64encode(key).decode()


class Tokens:
    def __init__(self, jwt_key: str, jwe_key: str):
        self._jwt_key = jwt_key
        self._jwe_key = jwe_key

    def create_access_token(
        self, username: str, password: str, expires_delta: timedelta, salt: bytes
    ) -> str:
        payload = {
            "sub": username,
            "encryption_key": generate_encryption_key(password, salt),
        }

        expire = datetime.utcnow() + expires_delta

        payload.update({"exp": expire})

        jwt_token = jwt.encode(payload, self._jwt_key)

        jwe_token = jwe.encrypt(jwt_token, self._jwe_key)

        return jwe_token.decode()

    def decode_access_token(self, token: str) -> AuthToken:
        jwt_token = jwe.decrypt(token, self._jwe_key)

        if not jwt_token:
            raise InvalidJWToken

        try:
            payload = jwt.decode(jwt_token, self._jwt_key)
            return AuthToken(**payload)

        except JWTError as jwt_error:
            raise InvalidJWToken from jwt_error
