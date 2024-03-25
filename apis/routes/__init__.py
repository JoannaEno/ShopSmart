from fastapi import APIRouter
from apis.routes.auth import router as authRouter
from apis.routes.users import router as usersRouter

router = APIRouter()

router.include_router(authRouter)
router.include_router(usersRouter)