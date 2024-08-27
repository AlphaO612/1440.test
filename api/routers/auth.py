import os, requests

from fastapi import FastAPI, APIRouter
from pydantic import BaseModel
from http import HTTPStatus

from addiction import Responses, Errors
from addiction import ResPattern, ErrorAnswer

URL_AUTH = os.getenv("URL_AUTH")
router = APIRouter()

API_ENDPOINT = 'https://discord.com/api/v10'
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = 'http://localhost/'


def exchange_code(code):
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI
    }

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    r = requests.post('%s/oauth2/token' % API_ENDPOINT, data=data, headers=headers, auth=(CLIENT_ID, CLIENT_SECRET))
    r.raise_for_status()
    return r.json()


def refresh_token(refresh_token):
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    r = requests.post('%s/oauth2/token' % API_ENDPOINT, data=data, headers=headers, auth=(CLIENT_ID, CLIENT_SECRET))
    r.raise_for_status()
    return r.json()


@router.get("/auth_link", status_code=200, response_model=Responses.AuthResponseGET)
async def return_link():
    response = Responses.AuthResponseGET(
        link=URL_AUTH
    )

    return ResPattern(
        success=response.code == HTTPStatus.OK,
        response=response
    )


@router.get("/auth", status_code=200, response_model=Responses.AuthResponsePOST)
async def return_link(code: str):
    response = Responses.AuthResponsePOST(
        link=URL_AUTH
    )

    return ResPattern(
        success=response.code == HTTPStatus.OK,
        response=response
    )
