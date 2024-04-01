import jwt
from datetime import datetime, timedelta, UTC
from app import schemas, database, models
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/login')


SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes
REFRESH_TOKEN_EXPIRE_MINUTES = settings.refresh_token_expire_minutes

def create_access_token(data: dict):
    """
    A function that creates an access token based on the input data dictionary.
    
    Parameters:
    - data (dict): A dictionary containing the data to be encoded into the token.
    
    Returns:
    - str: The encoded JWT access token.
    """
    to_encode = data.copy()

    expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

def create_refresh_token(data: dict):
    """
    Creates a refresh token using the provided data.

    Args:
        data (dict): A dictionary containing the data to be encoded in the refresh token.

    Returns:
        str: The encoded refresh token.

    """
    to_encode = data.copy()
    
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
        token_data = schemas.TokenData(email=email)

    except jwt.ExpiredSignatureError:
        raise credentials_exception
    
    except jwt.InvalidTokenError:
        raise credentials_exception
    
    return token_data


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    """
    Retrieves the current user based on the provided token.

    Args:
        token (str): The access token for authentication. Defaults to Depends(oauth2_scheme).
        db (Session): The database session. Defaults to Depends(database.get_db).

    Returns:
        Admin: The admin user object associated with the provided token.

    Raises:
        HTTPException: If the token cannot be validated or the credentials are invalid.

    """
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail=f"Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})

    token = verify_access_token(token, credentials_exception)

    admin = db.query(models.Admin).filter(models.Admin.email == token.email).first()

    return admin