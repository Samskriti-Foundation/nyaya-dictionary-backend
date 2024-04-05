from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.responses import JSONResponse
from app.database import get_db
from app import models, schemas
from app.middleware import auth_middleware
from sqlalchemy.orm import Session
from typing import List


router = APIRouter(
    prefix="/db-managers",
    tags=["DB Managers"],
)


@router.get("/", response_model=List[schemas.DBManagerOut])
def get_db_managers(db: Session = Depends(get_db), current_db_manager: schemas.DBManager = Depends(auth_middleware.get_current_db_manager_is_superuser)):
    db_managers = db.query(models.DBManager).all()
    return db_managers


@router.get("/{email}", response_model=schemas.DBManagerOut)
def get_db_manager(email: str, db: Session = Depends(get_db), current_db_manager: schemas.DBManager = Depends(auth_middleware.get_current_db_manager_is_admin)):
    db_manager_in_db = db.query(models.DBManager).filter(models.DBManager.email == email).first()

    auth_middleware.check_access(current_db_manager, db_manager_in_db)
    
    if not db_manager_in_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"DB Manager with email {email} not found")
    
    return db_manager_in_db


@router.put("/")
def update_db_manager(db_manager: schemas.DBManagerUpdate, db: Session = Depends(get_db), current_user: schemas.DBManager = Depends(auth_middleware.get_current_db_manager_is_admin)):
        
    
    db_db_manager = db.query(models.db_manager).filter(models.db_manager.email == db_manager.email).first()

    if not db_db_manager:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"db_manager with email {db_manager.email} not found")
    
    db_db_manager.email = db_manager.email
    db_db_manager.first_name = db_manager.first_name
    db_db_manager.last_name = db_manager.last_name
    db.commit()

    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "db_manager updated"})


@router.delete("/{email}", status_code=status.HTTP_204_NO_CONTENT)
def delete_db_manager(email: str, db: Session = Depends(get_db), current_user: int = Depends(auth_middleware.get_current_db_manager)):
    if not (current_user.is_superuser == True or current_user.email == email):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    
    db.query(models.db_manager).filter(models.db_manager.email == email).delete(synchronize_session=False)
    db.commit()