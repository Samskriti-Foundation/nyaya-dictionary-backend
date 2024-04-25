from app.schemas import Role, Access

def int_to_role(role: int) -> Role:
    if role == 3:
        return Role.SUPERUSER
    if role == 2:
        return Role.ADMIN
    if role == 1:
        return Role.EDITOR


def role_to_int(role: Role) -> int:
    if role == Role.SUPERUSER:
        return 3
    if role == Role.ADMIN:
        return 2
    if role == Role.EDITOR:
        return 1


def access_to_int(access: Access) -> int:
    if access == Access.READ_ONLY:
        return 1
    if access == Access.READ_WRITE:
        return 2
    if access == Access.READ_WRITE_MODIFY:
        return 3
    if access == Access.ALL:
        return 4
    

def int_to_access(access: int) -> Access:
    if access == 1:
        return Access.READ_ONLY
    if access == 2:
        return Access.READ_WRITE
    if access == 3:
        return Access.READ_WRITE_MODIFY
    if access == 4:
        return Access.ALL