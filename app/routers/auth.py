from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

from app import schemas, models, oauth2
from app.utils import encrypt
from app.database import get_db
from app.middleware import auth_middleware, logger_middleware


router = APIRouter(
    prefix='/auth',
    tags=['Authentication']
    )

@router.post('/login',response_model=schemas.Token)
async def login(request: Request, user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Logs in a user with the provided credentials and returns an access token and a refresh token.

    Parameters:
        - request (Request): The incoming request object.
        - user_credentials (OAuth2PasswordRequestForm): The user credentials provided for authentication.
        - db (Session): The database session object.

    Returns:
        - dict: A dictionary containing the access token, refresh token, and token type.

    Raises:
        - HTTPException: If the provided credentials are invalid.

    Description:
        This function is an API endpoint that handles user login. It takes in the request object, user credentials,
        and a database session object as parameters. It queries the database to check if the provided email exists in the
        DBManager table. If the email does not exist, it raises an HTTPException with a status code of 403 (Forbidden)
        and the message 'Invalid Credentials'. If the email exists, it verifies the provided password using the encrypt
        module's verify function. If the password is incorrect, it raises an HTTPException with the same status code and
        message. If the credentials are valid, it creates an access token and a refresh token using the oauth2 module's
        create_access_token and create_refresh_token functions, respectively. It then logs the login operation using the
        logger_middleware module's log_login_operations function. Finally, it returns a dictionary containing the access
        token, refresh token, and token type.
    """
    db_manager = db.query(models.DBManager).filter(models.DBManager.email == user_credentials.username).first()

    if not db_manager:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail='Invalid Credentials')
    
    if not encrypt.verify(user_credentials.password, db_manager.password[2:-1].encode('utf-8')):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail='Invalid Credentials')
    
    access_token = oauth2.create_access_token(data={'email': db_manager.email, 'role': db_manager.role, 'access': db_manager.access})
    refresh_token = oauth2.create_refresh_token(data={'email': db_manager.email, 'role': db_manager.role, 'access': db_manager.access})
    
    client = request.scope["client"]
    await logger_middleware.log_login_operations(client, db_manager.email)

    return {'access_token':access_token, 'refresh_token':refresh_token,'token_type':'bearer'}


@router.post("/refresh")
def refresh(refresh_token: schemas.RefreshToken, db: Session = Depends(get_db)):
    """
    This function refreshes the access token using the provided refresh token.
    It verifies the access token and retrieves the associated DBManager from the database.
    If the DBManager does not exist, it raises an HTTPException with a 404 status code.
    It then creates a new access token based on the retrieved data and returns it.
    
    Parameters:
        - refresh_token (schemas.RefreshToken): The refresh token used to generate a new access token.
        - db (Session): The database session object.

    Returns:
        - dict: A dictionary containing the new access token and the token type 'bearer'.
    """
    data = oauth2.verify_access_token(refresh_token.refresh_token, credentials_exception=HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"}))
    
    db_manager = db.query(models.DBManager).filter(models.DBManager.email == data.email).first()

    if not db_manager:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    access_token = oauth2.create_access_token(data={'email': data.email, 'role': data.role, 'access': data.access})
    return {'access_token':access_token, 'token_type':'bearer'}


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_db_manager(db_manager: schemas.DBManagerIn, db: Session = Depends(get_db), current_db_manager: schemas.DBManager = Depends(auth_middleware.get_current_db_manager_is_admin)):
    """
    Endpoint to register a new DB Manager. 
    Validates access permissions, checks if the DB Manager already exists, hashes the password, assigns access based on role, 
    creates a new DB Manager entry, and returns a JSON response with the created DB Manager's role information.
    
    Parameters:
    - db_manager: schemas.DBManagerIn - The input data for creating a new DB Manager.
    - db: Session - The database session.
    - current_db_manager: schemas.DBManager - The current DB Manager performing the registration.
    
    Returns:
    - JSONResponse: The response containing the status code and a message indicating the role of the created DB Manager.
    """
    auth_middleware.check_access_in_accessing_db_manager(current_db_manager, db_manager)
    
    db_manager_in_db = db.query(models.DBManager).filter(models.DBManager.email == db_manager.email).first()

    if db_manager_in_db:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"DB Manager with email: {db_manager.email} already exists")
    
    hashed_password = encrypt.hash(db_manager.password)
    db_manager.password = hashed_password.decode('utf-8')

    if db_manager.role in (schemas.Role.ADMIN, schemas.Role.SUPERUSER):
        db_manager.access = schemas.Access.ALL

    db_manager = models.DBManager(**db_manager.model_dump())

    db.add(db_manager)
    db.commit()
    db.refresh(db_manager)

    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"message": f"{db_manager.role} created"})


@router.post("/register/superuser", status_code=status.HTTP_201_CREATED)
def register_superuser(superuser: schemas.DBManagerIn, db: Session = Depends(get_db)):
    """
    Registers a superuser in the system.

    Parameters:
    - superuser (schemas.DBManagerIn): The superuser information to be registered.
    - db (Session): The database session.

    Returns:
    - JSONResponse: The response containing the status code and a message indicating the role of the created superuser.
    """
    db_superuser = db.query(models.DBManager).filter(models.DBManager.email == superuser.email).first()
    
    if db_superuser:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Superuser with email: {superuser.email} already exists")
    

    hashed_password = str(encrypt.hash(superuser.password))
    print(hashed_password)

    superuser.password = hashed_password
    superuser.role = schemas.Role.SUPERUSER
    superuser.access = schemas.Access.ALL

    db_superuser = models.DBManager(**superuser.model_dump())
    db.add(db_superuser)
    db.commit()
    db.refresh(db_superuser)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"message": "Superuser created"})