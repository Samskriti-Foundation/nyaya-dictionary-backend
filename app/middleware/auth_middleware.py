from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app import models, database, schemas
from app.oauth2 import verify_access_token
from app.utils.converter import role_to_int
from app.database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/login')

def get_current_db_manager(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail=f"Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})

    token_data = verify_access_token(token, credentials_exception)

    db_manager = db.query(models.DBManager).filter(models.DBManager.email == token_data.email).first()

    return db_manager


def get_current_db_manager_is_admin(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    db_manager = get_current_db_manager(token, db)
    
    if role_to_int(db_manager.role) < role_to_int(schemas.Role.ADMIN):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")

    return db_manager


def get_current_db_manager_is_superuser(db_manager: schemas.DBManager):
    if role_to_int(db_manager.role) < role_to_int(schemas.Role.SUPERUSER):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")

    return db_manager


def check_access_in_accessing_db_manager(current_db_manager: schemas.DBManager, db_manager_in_db: schemas.DBManager):
    if role_to_int(db_manager_in_db.role) > role_to_int(current_db_manager.role):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    
    if role_to_int(db_manager_in_db.role) == role_to_int(current_db_manager.role) and db_manager_in_db.email != current_db_manager.email:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")