from fastapi import APIRouter
from apis.routes.auth import router as authRouter
from apis.routes.users import router as usersRouter
from apis.routes.products import router as productsRouter
from apis.routes.orders import router as ordersRouter

router = APIRouter()

router.include_router(authRouter)
router.include_router(usersRouter)
router.include_router(productsRouter)
router.include_router(ordersRouter)
