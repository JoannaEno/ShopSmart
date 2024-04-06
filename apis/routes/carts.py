from fastapi import APIRouter, HTTPException, Query, status
from fastapi.params import Depends
from pydantic import BaseModel

from apis.prisma import prisma
from apis.utils.auth import get_user_id

router = APIRouter()


class Cart(BaseModel):
 orderId: str


@router.get("/cart", tags=["cart"], status_code=status.HTTP_200_OK)
async def get_cart(user_id: str = Depends(get_user_id)):

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing token")

    orders = await prisma.order.find_many(where={"userId": user_id})

    if not orders:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No orders found")

    sub_total = sum(order.totalPrice for order in orders)

    return {
        "total": sub_total,
        "orders": [order.model_dump() for order in orders]
    }