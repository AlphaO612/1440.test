import os

from fastapi import FastAPI, APIRouter
from pydantic import BaseModel
from http import HTTPStatus

from addiction import Responses, Errors
from addiction import ResPattern, ErrorAnswer

URL_AUTH = os.getenv("URL_AUTH")
router = APIRouter()


@router.get("/auth", status_code=200, response_model=Responses.AuthResponseGET)
async def return_link():
    response = Responses.AuthResponseGET(
        link=URL_AUTH
    )

    return ResPattern(
        success=response.code == HTTPStatus.OK,
        response=response
    )


@router.post("/auth", status_code=200, response_model=Responses.AuthResponsePOST)
async def return_link(
        code,
        state
):
    response = Responses.AuthResponsePOST(
        link=URL_AUTH
    )

    return ResPattern(
        success=response.code == HTTPStatus.OK,
        response=response
    )
