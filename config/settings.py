from dotenv import load_dotenv

from config.util import Environment
from logger import logger

""""load environment variables"""

# Load env variables from a file, if exists else default would be set
logger.info("SERVER_INIT::Setting environment variables from .env file(if exists)...")
load_dotenv(verbose=True)


class DB:
    host = Environment.get_string("DB_HOST", "postgres_db")
    port = Environment.get_string("DB_PORT", '5432')
    name = Environment.get_string("DB_NAME", "cartdb")
    user = Environment.get_string("DB_USER", "cartdb_user")
    pass_ = Environment.get_string("DB_PASS", "zxcvbnml")


class JWTToken:
    algorithm = Environment.get_string("JWT_ALGORITHM", "HS256")
    secret = Environment.get_string("JWT_SECRET", "secret")
    access_token_expire_minutes = Environment.get_string("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "86400")
