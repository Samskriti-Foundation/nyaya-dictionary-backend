from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.responses import JSONResponse
from app.database import get_db
from app import models, schemas, oauth2
from sqlalchemy.orm import Session
from typing import List


router = APIRouter(
    prefix="/admins",
    tags=["Admins"],
)


@router.get("/", response_model=List[schemas.AdminOut])
def get_admins(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    if current_user.is_superuser == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    
    admins = db.query(models.Admin).all()
    return admins


@router.get("/{email}", response_model=schemas.AdminOut)
def get_admin(email: str, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    if not (current_user.is_superuser == True or current_user.email == email):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    
    admin = db.query(models.Admin).filter(models.Admin.email == email).first()

    if not admin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Admin with email {email} not found")
    
    return admin


@router.put("/", response_model=schemas.AdminOut)
def update_admin(admin: schemas.AdminUpdate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    if not (current_user.is_superuser == True or current_user.email == admin.email):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    
    db_admin = db.query(models.Admin).filter(models.Admin.email == admin.email).first()

    if not db_admin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Admin with email {admin.email} not found")
    
    db_admin.email = admin.email
    db_admin.first_name = admin.first_name
    db_admin.last_name = admin.last_name
    db.commit()

    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Admin updated"})


@router.delete("/{email}", status_code=status.HTTP_204_NO_CONTENT)
def delete_admin(email: str, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    if not (current_user.is_superuser == True or current_user.email == email):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    
    db.query(models.Admin).filter(models.Admin.email == email).delete(synchronize_session=False)
    db.commit()