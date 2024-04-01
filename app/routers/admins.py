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
    """
    Get a list of all admins.
    
    Parameters:
        db (Session): The database session.
        current_user (int): The ID of the current user.
        
    Returns:
        List[schemas.AdminOut]: A list of admin objects.
    """
    if current_user.is_superuser == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    
    admins = db.query(models.Admin).all()
    return admins


@router.get("/{email}", response_model=schemas.AdminOut)
def get_admin(email: str, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    """
    Retrieves an admin from the database based on their email.

    Parameters:
        email (str): The email of the admin to retrieve.
        db (Session, optional): The database session. Defaults to Depends(get_db).
        current_user (int, optional): The current user. Defaults to Depends(oauth2.get_current_user).

    Returns:
        AdminOut: The retrieved admin object.

    Raises:
        HTTPException: If the current user is not authorized to perform the action or if the admin with the specified email is not found.
    """
    if not (current_user.is_superuser == True or current_user.email == email):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    
    admin = db.query(models.Admin).filter(models.Admin.email == email).first()

    if not admin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Admin with email {email} not found")
    
    return admin


@router.put("/", response_model=schemas.AdminOut)
def update_admin(admin: schemas.AdminUpdate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    """
    Update an admin in the database.

    Parameters:
    - admin: schema representing the updated admin data
    - db: database session dependency
    - current_user: the current user making the request

    Returns:
    - JSONResponse with a message indicating successful admin update
    """
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
    """
    Delete an admin user from the database.

    Parameters:
        email (str): The email of the admin user to be deleted.
        db (Session, optional): The database session. Defaults to Depends(get_db).
        current_user (int, optional): The current user ID. Defaults to Depends(oauth2.get_current_user).

    Raises:
        HTTPException: If the current user is not authorized to perform the requested action.

    Returns:
        None
    """
    if not (current_user.is_superuser == True or current_user.email == email):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    
    db.query(models.Admin).filter(models.Admin.email == email).delete(synchronize_session=False)
    db.commit()