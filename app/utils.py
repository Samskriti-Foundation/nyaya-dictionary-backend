import bcrypt

def hash(password: str) -> bytes:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


def verify(plain_password: str, hashed_password: bytes):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)