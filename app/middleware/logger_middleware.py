from fastapi import Request
from ..logger import db_logger
from pprint import pprint

async def log_database_operations(request: Request, call_next):
    response = await call_next(request)
    
    # if request.method not in {"POST", "PUT", "DELETE", "PATCH"}:
    #     return response

    db_logger.info("Data inserted successfully", extra={"response": "hi"})
    return response


async def log_login_operations(request: Request, call_next):
    response = await call_next(request)
    return response