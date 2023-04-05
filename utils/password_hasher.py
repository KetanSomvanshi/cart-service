from passlib.context import CryptContext


class HashedPassword:
    """utility class to hash and verify passwords"""
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @staticmethod
    def get_password_hash(password: str) -> str:
        return HashedPassword.pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return HashedPassword.pwd_context.verify(plain_password, hashed_password)
