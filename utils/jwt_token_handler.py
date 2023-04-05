import json
from datetime import timedelta, datetime
import jwt

from config.settings import JWTToken


class JWTHandler:
    @staticmethod
    def create_access_token(to_encode: dict, expires_delta: timedelta = None):
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=int(JWTToken.access_token_expire_minutes))
        to_encode.update({"exp": expire.timestamp()})
        encoded_jwt = jwt.encode(to_encode, JWTToken.secret, algorithm=JWTToken.algorithm)
        return encoded_jwt
