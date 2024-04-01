from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from prisma.models import Product

from apis.prisma import prisma
from apis.utils.auth import get_user_id

router = APIRouter()


class Order(BaseModel):
  productId: str
  userId:    str
  quantity:  int


@router.post("/order/create", tags=["order"], status_code=status.HTTP_201_CREATED)
async def create_order(order: Order, user_id: str = Depends(get_user_id)):
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing token")

    order_data = {
        "productId": order.productId,
        "userId": user_id,
        "quantity": order.quantity,
        "product": {"connect": {"id": order.productId}}
    }
    created_order = await prisma.order.create(**order_data)
    return created_order


@router.get("/order/{orderId}", tags=["order"], status_code=status.HTTP_200_OK)
async def read_order(orderId: str, user_id: str = Depends(get_user_id)):
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing token")
    order = await prisma.order.find_unique(where={"id": orderId, "userId": user_id}, include={"product": True})

    return order


@router.get("/orders", tags=["order"], status_code=status.HTTP_200_OK)
async def read_orders(user_id: str = Depends(get_user_id)):
    products = await prisma.order.find_many(where={"userId": user_id}, include={"product": True})
    # TODO: Add pagination to this endpoint

    return products