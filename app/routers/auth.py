from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

from app import schemas, models ,oauth2
from app.utils import encrypt
from app.database import get_db

router = APIRouter(
    prefix='/auth',
    tags=['Authentication']
    )

@router.post('/login',response_model=schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(),db: Session = Depends(get_db)):
    """
    Logs in a user with the provided credentials.

    Parameters:
        user_credentials (OAuth2PasswordRequestForm): The user's credentials for authentication.
        db (Session): The database session to query the user.

    Returns:
        dict: A dictionary containing the access token and token type.

    Raises:
        HTTPException: If the user credentials are invalid.
    """
    user = db.query(models.Admin).filter(models.Admin.email == user_credentials.username).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail='Invalid Credentials')

    if not encrypt.verify(user_credentials.password,user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail='Invalid Credentials')
    
    access_token = oauth2.create_access_token(data={'email':user.email})
    
    return {'access_token':access_token,'token_type':'bearer'}


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_admin(admin: schemas.AdminBase, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    """
    Registers a new admin user.

    Parameters:
        - admin (schemas.AdminBase): The admin user information.
        - db (Session, optional): The database session. Defaults to the result of the `get_db` dependency.
        - current_user (int, optional): The current user's ID. Defaults to the result of the `oauth2.get_current_user` dependency.

    Raises:
        - HTTPException: If the current user is not a superuser or if an admin with the same email already exists.

    Returns:
        - JSONResponse: A JSON response with a status code of 201 and a message indicating that the admin was created.
    """
    if current_user.is_superuser == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to perform requested action")
    
    db_admin = db.query(models.Admin).filter(models.Admin.email == admin.email).first()

    if db_admin:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Admin with email: {admin.email} already exists")
    
    hashed_password = encrypt.hash(admin.password)
    admin.password = hashed_password

    db_admin = models.Admin(**admin.model_dump(), is_superuser=False)

    db.add(db_admin)
    db.commit()
    db.refresh(db_admin)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"message": "Admin created"})


@router.post("/register/superuser", status_code=status.HTTP_201_CREATED)
def register_superuser(admin: schemas.AdminBase, db: Session = Depends(get_db)):#, current_user: int = Depends(oauth2.get_current_user)):
    """
    Register a superuser with the provided admin details in the database.

    Args:
        admin (schemas.AdminBase): The admin details for the superuser registration.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Raises:
        HTTPException: If the current user is not authorized or if a superuser with the same email already exists.

    Returns:
        JSONResponse: A JSON response indicating the superuser creation status.
    """
    # if current_user.is_superuser == False:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
    #                         detail="Not authorized to perform requested action")

    db_admin = db.query(models.Admin).filter(models.Admin.email == admin.email).first()

    if db_admin:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Superuser with email: {admin.email} already exists")


    hashed_password = encrypt.hash(admin.password)
    db_admin = models.Admin(
        email=admin.email,
        password=hashed_password,
        first_name=admin.first_name,
        last_name=admin.last_name,
        is_superuser=True)
    db.add(db_admin)
    db.commit()
    db.refresh(db_admin)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"message": "Superuser created"})