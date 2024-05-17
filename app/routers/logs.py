from fastapi import APIRouter, Depends, status
from datetime import datetime
from typing import List
from app.schemas import DBLog, AuthLog
from app.middleware import auth_middleware

router = APIRouter(
    prefix='/logs',
    tags=['Logs']
    )

@router.get('/db-ops/{month}', status_code=status.HTTP_200_OK, response_model=List[DBLog])
def get_database_operation_logs(month: str = f'{datetime.now().strftime("%m")}_{datetime.now().strftime("%h")}', current_db_manager = Depends(auth_middleware.get_current_db_manager_is_admin)):
    """
    Retrieves the database operation logs for a specified month.
    
    Parameters:
        month (str): The month for which the logs are retrieved. Defaults to the current month and year.
        current_db_manager: The current database manager with admin privileges.
    
    Returns:
        List[DBLog]: A list of DBLog objects representing the database operation logs.
    """
    output = []
    with open (f"logs/{month}.log", "r", encoding="utf8") as f:
        for line in f:
            log_split = line.split(" - ")
            db_log = DBLog(timestamp=log_split[1], table_name=log_split[3], record_id=log_split[4], operation=log_split[5], db_manager_email=log_split[6], affected_value=" ".join(log_split[7:])[:-1])
            output.append(db_log)
    return output


@router.get('/login-audits/', status_code=status.HTTP_200_OK, response_model=List[AuthLog])
def get_login_audit_logs(current_db_manager = Depends(auth_middleware.get_current_db_manager_is_admin)):
    """
    Retrieves the login audit logs from the auth.log file.
    
    Parameters:
        current_db_manager: The current database manager with admin privileges.
    
    Returns:
        List[AuthLog]: A list of AuthLog objects representing the login audit logs.
    """
    output = []
    with open ("logs/auth.log", "r") as f:
        for line in f:
            log_split = line.split(" - ")
            auth_log = AuthLog(timestamp=log_split[1], client_ip=log_split[3], db_manager_email="".join(log_split[4])[:-1])
            output.append(auth_log)
    return output