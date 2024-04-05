import pytest
from app import schemas
from app.middleware.auth_middleware import check_access_in_accessing_db_manager
from fastapi import HTTPException, status

# def test_check_access_in_accessing_db_manager():
#     # Test for superuser
#     current_db_manager_superuser = schemas.DBManager(role=schemas.Role.SUPERUSER)
#     db_manager_in_db_superuser = schemas.DBManager(role=schemas.Role.SUPERUSER)
#     assert check_access_in_accessing_db_manager(current_db_manager_superuser, db_manager_in_db_superuser) is None

#     # Test for insufficient role
#     current_db_manager_admin = schemas.DBManager(role=schemas.Role.ADMIN)
#     db_manager_in_db_superuser = schemas.DBManager(role=schemas.Role.SUPERUSER)
#     with pytest.raises(HTTPException) as exc_info:
#         check_access_in_accessing_db_manager(current_db_manager_admin, db_manager_in_db_superuser)
#     assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN

#     # Test for same role but different email
#     current_db_manager = schemas.DBManager(role=schemas.Role.ADMIN, email="admin@example.com")
#     db_manager_in_db = schemas.DBManager(role=schemas.Role.ADMIN, email="another_admin@example.com")
#     with pytest.raises(HTTPException) as exc_info:
#         check_access_in_accessing_db_manager(current_db_manager, db_manager_in_db)
#     assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN

    
