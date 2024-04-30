from fastapi import Request
from ..logger import db_logger

async def log_database_operations(table_name: str, record_id: str, operation: str, db_manager_email: str, new_value: str = ""):
    log_message = f"{table_name} - {record_id} - {operation} - {db_manager_email} - {new_value}"
    db_logger.info(log_message)


async def log_login_operations(request: Request, call_next):
    response = await call_next(request)
    return response