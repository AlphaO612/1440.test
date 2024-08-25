from fastapi import FastAPI, APIRouter
from pydantic import BaseModel


router = APIRouter()


@router.get("/auth", response_model=ActionResponse)
async def return_link():
    metadata = dict(
        user_id=user_id,
    )


    return ActionResponse(metadata=metadata)


