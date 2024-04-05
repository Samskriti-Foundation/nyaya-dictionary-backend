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