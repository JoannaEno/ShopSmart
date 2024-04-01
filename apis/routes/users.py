from typing import List
from fastapi import APIRouter, status, Depends
from apis.prisma import prisma
from apis.utils.auth import JWTBearer, decodeJWT

router = APIRouter()


@router.get("/users", tags=["users"], status_code=status.HTTP_200_OK)
async def read_users():
    users = await prisma.user.find_many()

    # TODO: do not loop to avoid performance issues, find a better way
    for user in users:
        del user.password

    return users


@router.get("/users/me", tags=["users"], status_code=status.HTTP_200_OK)
async def read_user_me(token=Depends(JWTBearer())):
    decoded = decodeJWT(token)

    if "userId" in decoded:
        userId = decoded["userId"]
        return prisma.user.find_unique(where={"id": userId})
    return None


@router.get("/users/{userId}", tags=["users"], status_code=status.HTTP_200_OK)
async def get_user_by_id(userId: str):
    user = await prisma.user.find_unique(where={"id": userId})

    return user