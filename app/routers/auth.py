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
    db_manager = db.query(models.DBManager).filter(models.DBManager.email == user_credentials.username).first()

    if not db_manager:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail='Invalid Credentials')

    if not encrypt.verify(user_credentials.password, db_manager.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail='Invalid Credentials')
    
    access_token = oauth2.create_access_token(data={'email': db_manager.email, 'role': db_manager.role, 'access': db_manager.access})
    refresh_token = oauth2.create_refresh_token(data={'email': db_manager.email, 'role': db_manager.role, 'access': db_manager.access})
    
    client = request.scope["client"]
    await logger_middleware.log_login_operations(client, db_manager.email)

    return {'access_token':access_token, 'refresh_token':refresh_token,'token_type':'bearer'}


@router.post("/refresh")
def refresh(refresh_token: schemas.RefreshToken, db: Session = Depends(get_db)):
    data = oauth2.verify_access_token(refresh_token.refresh_token, credentials_exception=HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"}))
    
    db_manager = db.query(models.DBManager).filter(models.DBManager.email == data.email).first()

    if not db_manager:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    access_token = oauth2.create_access_token(data={'email': data.email, 'role': data.role, 'access': data.access})
    return {'access_token':access_token, 'token_type':'bearer'}


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_db_manager(db_manager: schemas.DBManagerIn, db: Session = Depends(get_db), current_db_manager: schemas.DBManager = Depends(auth_middleware.get_current_db_manager_is_admin)):
    auth_middleware.check_access_in_accessing_db_manager(current_db_manager, db_manager)
    
    db_manager_in_db = db.query(models.DBManager).filter(models.DBManager.email == db_manager.email).first()

    if db_manager_in_db:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"DB Manager with email: {db_manager.email} already exists")
    
    hashed_password = encrypt.hash(db_manager.password)
    db_manager.password = hashed_password

    if db_manager.role in (schemas.Role.ADMIN, schemas.Role.SUPERUSER):
        db_manager.access = schemas.Access.ALL

    db_manager = models.DBManager(**db_manager.model_dump())

    db.add(db_manager)
    db.commit()
    db.refresh(db_manager)

    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"message": f"{db_manager.role} created"})


@router.post("/register/superuser", status_code=status.HTTP_201_CREATED)
def register_superuser(superuser: schemas.DBManagerIn, db: Session = Depends(get_db)):
    db_superuser = db.query(models.DBManager).filter(models.DBManager.email == superuser.email).first()
    
    if db_superuser:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Superuser with email: {superuser.email} already exists")
    
    superuser.password = encrypt.hash(superuser.password)
    superuser.role = schemas.Role.SUPERUSER
    superuser.access = schemas.Access.ALL

    db_superuser = models.DBManager(**superuser.model_dump())
    db.add(db_superuser)
    db.commit()
    db.refresh(db_superuser)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"message": "Superuser created"})