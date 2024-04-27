from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.responses import JSONResponse
from app.database import get_db
from app import models, schemas
from app.middleware import auth_middleware, logger_middleware
from sqlalchemy.orm import Session
from typing import List

router = APIRouter(
    prefix="/db-managers",
    tags=["DB Managers"],
)


@router.get("/", response_model=List[schemas.DBManagerOut])
def get_db_managers(role: schemas.Role = None, db: Session = Depends(get_db), current_db_manager: schemas.DBManager = Depends(auth_middleware.get_current_db_manager_is_admin)):
    if current_db_manager.role == schemas.Role.SUPERUSER:
        if role is None:
            db_managers = db.query(models.DBManager).all()
        else:
            db_managers = db.query(models.DBManager).filter(models.DBManager.role == role).all()
    
    elif current_db_manager.role == schemas.Role.ADMIN:
        if role is None or role == schemas.Role.EDITOR:
            db_managers = db.query(models.DBManager).filter(models.DBManager.role == schemas.Role.EDITOR).all()
            
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
        
    elif current_db_manager.role == schemas.Role.EDITOR:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")

    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role")
    
    return db_managers


@router.get("/{email}", response_model=schemas.DBManagerOut)
def get_db_manager(email: str, db: Session = Depends(get_db), current_db_manager: schemas.DBManager = Depends(auth_middleware.get_current_db_manager_is_admin)):
    db_manager_in_db = db.query(models.DBManager).filter(models.DBManager.email == email).first()

    if not db_manager_in_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"DB Manager with email {email} not found")

    auth_middleware.check_access_in_accessing_db_manager(current_db_manager, db_manager_in_db)
    
    return db_manager_in_db


@router.put("/{email}", status_code=status.HTTP_200_OK)
def update_db_manager(email: str, db_manager: schemas.DBManagerUpdate, db: Session = Depends(get_db), current_db_manager: schemas.DBManager = Depends(auth_middleware.get_current_db_manager_is_admin)):
    db_manager_in_db = db.query(models.DBManager).filter(models.DBManager.email == email).first()

    if not db_manager_in_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"db_manager with email {db_manager.email} not found")
    
    auth_middleware.check_access_in_accessing_db_manager(current_db_manager, db_manager_in_db)
    
    db_manager_in_db.first_name = db_manager.first_name
    db_manager_in_db.last_name = db_manager.last_name
    db_manager_in_db.email = db_manager.email
    db_manager_in_db.role = db_manager.role
    db_manager_in_db.access = db_manager.access

    db.commit()
    db.refresh(db_manager_in_db)

    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "db_manager updated"})


@router.delete("/{email}", status_code=status.HTTP_204_NO_CONTENT)
def delete_db_manager(email: str, db: Session = Depends(get_db), current_db_manager: int = Depends(auth_middleware.get_current_db_manager)):
    db_manager = db.query(models.DBManager).filter(models.DBManager.email == email).first()

    if not db_manager:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"db_manager with email {email} not found")
    
    auth_middleware.check_access_in_accessing_db_manager(current_db_manager, db_manager)
    
    db.delete(db_manager)
    db.commit()