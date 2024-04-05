import pytest
from app import schemas
from app.middleware.auth_middleware import check_access_in_accessing_db_manager
from fastapi import HTTPException

@pytest.fixture
def current_db_manager():
    return {
        "email": "test@gmail.com",
        "first_name": "test",
        "last_name": "test",
        "access": schemas.Access.ALL
    }


@pytest.fixture
def db_manager_in_db_same():
    return {
        "email": "test@gmail.com",
        "first_name": "test",
        "last_name": "test",
        "access": schemas.Access.READ_WRITE
    }


@pytest.fixture
def db_manager_in_db_different():
    return {
        "email": "tes2t@gmail.com",
        "first_name": "test2",
        "last_name": "test2",
        "access": schemas.Access.READ_WRITE
    }

@pytest.fixture
def roles():
    return [schemas.Role.EDITOR, schemas.Role.EDITOR, schemas.Role.EDITOR]

def test_check_access_in_accessing_db_manager(current_db_manager, db_manager_in_db_same, db_manager_in_db_different):
    # Test when db_manager_in_db has a higher role
    db_manager_in_db_same["role"] = schemas.Role.ADMIN
    current_db_manager["role"] = schemas.Role.EDITOR
    with pytest.raises(HTTPException):
        check_access_in_accessing_db_manager(current_db_manager, db_manager_in_db_same)

    # Test when db_manager_in_db has the same role but different email
    db_manager_in_db_same["role"] = schemas.Role.EDITOR
    current_db_manager["role"] = schemas.Role.EDITOR
    current_db_manager["email"] = "different@gmail.com"
    with pytest.raises(HTTPException):
        check_access_in_accessing_db_manager(current_db_manager, db_manager_in_db_same)

    # Test when db_manager_in_db has the same role and email
    current_db_manager["email"] = "test@gmail.com"
    check_access_in_accessing_db_manager(current_db_manager, db_manager_in_db_same)

    # Test when db_manager_in_db has a different role
    current_db_manager["role"] = schemas.Role.ADMIN
    db_manager_in_db_same["role"] = schemas.Role.EDITOR
    check_access_in_accessing_db_manager(current_db_manager, db_manager_in_db_same)

    # Test when db_manager_in_db has the same role and email but different access
    db_manager_in_db_different["role"] = schemas.Role.EDITOR
    current_db_manager["role"] = schemas.Role.EDITOR
    with pytest.raises(HTTPException):
        check_access_in_accessing_db_manager(current_db_manager, db_manager_in_db_different)
