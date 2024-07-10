import bcrypt

def hash(password: str) -> bytes:
    """
    Hashes a password using bcrypt.
    
    Args:
        password (str): The password to hash.
    
    Returns:
        bytes: The hashed password.
    """
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def verify(plain_password: str, hashed_password: bytes) -> bool:
    """
    Verifies a plain password against a hashed password.
    
    Args:
        plain_password (str): The plain password to verify.
        hashed_password (bytes): The hashed password to verify against.
    
    Returns:
        bool: True if the password matches the hash, False otherwise.
    """
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)
