from fastapi import HTTPException, status
from pydantic import UUID4


class ObjectNotFound(HTTPException):
    def __init__(self, object_name: str, obj_id: int | UUID4):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{object_name} id={obj_id} not found.",
        )
