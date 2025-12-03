from sqlalchemy.exc import SQLAlchemyError

class CrudError(SQLAlchemyError):
    def __init__(self, message: str = "An error occurred during a CRUD operation"):
        self._message = message
        super().__init__(self._message)

class NotFoundError(CrudError):
    def __init__(self, entity: str = "Entity", identifier: object = None):
        self.entity = entity
        self.identifier = identifier
        if identifier is None:
            message = f"{entity} not found"
        else:
            message = f"{entity} with identifier {identifier} not found"
        super().__init__(message)

class ConflictError(CrudError):
    def __init__(self, message: str = "Conflict occurred during a CRUD operation"):
        super().__init__(message)

class UserNotFoundError(NotFoundError):
    def __init__(self, id: int | None = None):
        super().__init__(entity="User", identifier=id)

class UserAlreadyExistsError(ConflictError):
    def __init__(self, message: str = "User already exists", id: int | None = None):
        if id:
            message = f"User with ID {id} already exists"
        super().__init__(message)

class ScoreNotFoundError(NotFoundError):
    def __init__(self, score_id: int | None = None):
        super().__init__(entity="Score", identifier=score_id)


class SubjectNotFoundError(NotFoundError):
    def __init__(self, subject_id: str | None = None):
        super().__init__(entity="Subject", identifier=subject_id)
