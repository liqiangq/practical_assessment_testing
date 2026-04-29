import secrets
import string

TOKEN_LENGTH = 32
ALPHABET = string.ascii_letters + string.digits


def generate_token(length: int = TOKEN_LENGTH) -> str:
    return "".join(secrets.choice(ALPHABET) for _ in range(length))
