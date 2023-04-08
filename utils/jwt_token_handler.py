from datetime import timedelta, datetime

import jwt

from config.settings import JWTToken
from controller.context_manager import context_actor_user_data, context_log_meta
from logger import logger
from models.user import UserTokenData
from utils.exceptions import AuthException


class JWTHandler:
    @staticmethod
    def create_access_token(to_encode: dict, expires_delta: timedelta = None):
        """
        Create access token for the user and add expiry to token
        :param to_encode:
        :param expires_delta:
        :return:
        """
        if expires_delta:
            expire = datetime.now() + expires_delta
        else:
            expire = datetime.now() + timedelta(minutes=int(JWTToken.access_token_expire_minutes))
        to_encode.update({"exp": expire.timestamp()})
        encoded_jwt = jwt.encode(to_encode, JWTToken.secret, algorithm=JWTToken.algorithm)
        return encoded_jwt

    @staticmethod
    def decode_access_token(token: str):
        """
        Decode the access token and set the user data in context
        :param token:   access token
        :return:
        """
        try:
            payload = jwt.decode(token, JWTToken.secret, algorithms=[JWTToken.algorithm])
            context_actor_user_data.set(UserTokenData(**payload))
        except Exception as e:
            logger.error(extra=context_log_meta.get(), msg=f"Error while decoding access token: {e}")
            raise AuthException(status_code=401, message="Invalid authentication credentials")
