from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

from app import schemas, models, utils,oauth2
from app.database import get_db

router = APIRouter(
    prefix='/auth',
    tags=['Authentication']
    )

@router.post('/login',response_model=schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(),db: Session = Depends(get_db)):
    user = db.query(models.Admin).filter(models.Admin.email == user_credentials.username).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail='Invalid Credentials')

    if not utils.verify(user_credentials.password,user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail='Invalid Credentials')
    
    access_token = oauth2.create_access_token(data={'email':user.email})
    
    return {'access_token':access_token,'token_type':'bearer'}


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_admin(admin: schemas.AdminBase, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    if current_user.is_superuser == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to perform requested action")
    
    db_admin = db.query(models.Admin).filter(models.Admin.email == admin.email).first()

    if db_admin:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Admin with email: {admin.email} already exists")
    
    hashed_password = utils.hash(admin.password)
    admin.password = hashed_password

    db_admin = models.Admin(**admin.model_dump(), is_superuser=False)

    db.add(db_admin)
    db.commit()
    db.refresh(db_admin)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"message": "Admin created"})


@router.post("/register/superuser", status_code=status.HTTP_201_CREATED)
def register_superuser(admin: schemas.AdminBase, db: Session = Depends(get_db)):#, current_user: int = Depends(oauth2.get_current_user)):
    # if current_user.is_superuser == False:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
    #                         detail="Not authorized to perform requested action")

    db_admin = db.query(models.Admin).filter(models.Admin.email == admin.email).first()

    if db_admin:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Superuser with email: {admin.email} already exists")


    hashed_password = utils.hash(admin.password)
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