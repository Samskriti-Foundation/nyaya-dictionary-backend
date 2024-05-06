import jwt
from datetime import datetime, timedelta, UTC
from app import schemas
from app.config import settings


SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes
REFRESH_TOKEN_EXPIRE_MINUTES = settings.refresh_token_expire_minutes


def create_access_token(data: dict):
    to_encode = data.copy() # Data to be encoded in JWT token (email, role, access in this case).

    expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

def create_refresh_token(data: dict):
    to_encode = data.copy() # Data to be encoded in JWT token (email, role, access in this case).
    
    expire = datetime.now(UTC) + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

def verify_access_token(token: str, credentials_exception):
    """
    Verify the access token by decoding the token using the secret key and algorithm.
    
    Parameters:
    - token (str): The access token to be verified.
    - credentials_exception: The exception to be raised if credentials are invalid.
    
    Returns:
    - TokenData: The token data containing the user's email.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("email")
        if email is None:
            raise credentials_exception
        
        role: schemas.Role = payload.get("role")

        if role is None:
            raise credentials_exception
        
        access: schemas.Access = payload.get("access")

        if access is None:
            raise credentials_exception

        token_data = schemas.TokenData(email=email, role=role, access=access)
    
    except jwt.ExpiredSignatureError:
        raise credentials_exception
    
    return token_data