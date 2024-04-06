from datetime import datetime
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from prisma.models import User as UserModel

from apis.prisma import prisma
from apis.utils.auth import encryptPassword, signJWT, validatePassword

router = APIRouter()


class SignUp(BaseModel):
    email: str
    password: str
    name: str


class SignIn(BaseModel):
    email: str
    password: str


class SignInOut(BaseModel):
    token: str
    user: UserModel


@router.post("/auth/sign-in", tags=["auth"])
async def sign_in(signIn: SignIn):
    user = await prisma.user.find_first(
        where={
            "email": signIn.email,
        }
    )

    validated = validatePassword(signIn.password, user.password)
    del user.password

    if validated:
        token = signJWT(user.id)
        return SignInOut(token=token, user=user)

    return None


@router.post("/auth/sign-up", tags=["auth"], status_code=status.HTTP_201_CREATED)
async def sign_up(user: SignUp):
    existing_user = await prisma.user.find_first(
        where={
            "email": user.email,
        }
    )
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="User already exists")
    user = await prisma.user.create(
        {
            "createdAt": datetime.now(),
            "email": user.email,
            "password": encryptPassword(user.password),
            "name": user.name,
        }
    )
    return user
