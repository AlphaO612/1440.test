import enum

from .schema_base import ErrorAnswer
from http import HTTPStatus

class Errors(enum.Enum):
    NOT_FOUND = ErrorAnswer(
        status_code=HTTPStatus.NOT_FOUND.value,
        description="Method not found. Check docs."
    )

    UNAUTHORIZED = ErrorAnswer(
        status_code=HTTPStatus.UNAUTHORIZED.value,
        description="Authentication has failed or has not yet been provided."
    )

    BAD_REQUEST = ErrorAnswer(
        status_code=HTTPStatus.BAD_REQUEST.value,
        description="Some argument in parameters is wrong."
    )

    WRONG_CHANGE_STATE = ErrorAnswer(
        status_code=HTTPStatus.BAD_REQUEST.value,
        description="You can't change the old state to the same state it was before."
    )

    NOT_FOUND_TICKET = ErrorAnswer(
        status_code=HTTPStatus.NOT_FOUND.value,
        description="The requested ticket with the entered 'guid_ticket' doesn't exists!"
    )

    INTERNAL_ERROR = ErrorAnswer(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR.value,
        description="Something goes wrong! Try again. Check service logs!"
    )