from enum import StrEnum


class ErrorLogOperation(StrEnum):
    CREATE_USER = "create_user"
    UPDATE_USER = "update_user"
    DELETE_USER = "delete_user"
