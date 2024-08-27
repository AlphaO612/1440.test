from .schema_base import ErrorAnswer
from http import HTTPStatus

NOT_FOUND = ErrorAnswer(
    status_code=HTTPStatus.NOT_FOUND,
    description="Method not found. Check docs."
)

UNAUTHORIZED = ErrorAnswer(
    status_code=HTTPStatus.UNAUTHORIZED,
    description="Authentication has failed or has not yet been provided."
)

BAD_REQUEST = ErrorAnswer(
    status_code=HTTPStatus.BAD_REQUEST,
    description="Some argument in parameters is wrong."
)

WRONG_CHANGE_STATE = ErrorAnswer(
    status_code=HTTPStatus.BAD_REQUEST,
    description="You can't change the old state to the same state it was before."
)

NOT_FOUND_TICKET = ErrorAnswer(
    status_code=HTTPStatus.NOT_FOUND,
    description="The requested ticket with the entered 'guid_ticket' doesn't exists!"
)

INTERNAL_ERROR = ErrorAnswer(
    status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
    description="Something goes wrong! Check service logs!"
)