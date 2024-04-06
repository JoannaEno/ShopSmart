import math
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from prisma.models import Product

from apis.prisma import prisma
from apis.utils.auth import get_user_id

router = APIRouter()


class Order(BaseModel):
   productId: str
   userId:    str
   quantity:  int = 1


@router.post("/order/create", tags=["order"], status_code=status.HTTP_201_CREATED)
async def create_order(order: Order, user_id: str = Depends(get_user_id)):
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing token")

    product = await prisma.product.find_unique(where={"id": order.productId})

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    order_data = {
        "productId": order.productId,
        "quantity": order.quantity,
        "product": {"connect": {"id": order.productId}},
        "user": {"connect": {"id": user_id}},
        "userId": user_id,
        "totalPrice": order.quantity * product.price
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


@router.delete("/order/{orderId}", tags=["order"], status_code=status.HTTP_200_OK)
async def delete_order(orderId: str, user_id: str = Depends(get_user_id)):
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing token")
    order = await prisma.order.delete(where={"id": orderId, "userId": user_id})

    return order


@router.put("/update-order/{orderId}", tags=["order"], status_code=status.HTTP_200_OK)
async def update_order(orderId: str, order: Order, user_id: str = Depends(get_user_id)):
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing token")
    existing_order = await prisma.order.find_unique(where={"id": orderId, "userId": user_id})

    if not existing_order:
        return {"message": f"Order with id {orderId} not found"}

    updated_order = await prisma.order.update(
        where={"id": orderId, "userId": user_id},
        data={"quantity": order.quantity or existing_order.quantity}
    )

    return updated_order