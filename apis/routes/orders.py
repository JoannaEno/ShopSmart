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
async def read_orders(user_id: str = Depends(get_user_id), page: int = Query(default=1, ge=1),
                      per_page: int = Query(default=10, le=100)):
    offset = (page - 1) * per_page
    orders_count = await prisma.order.count(where={"userId": user_id})
    total_pages = math.ceil(orders_count / per_page)

    # If the provided page number is greater than the total number of pages, we redirect to the last page
    if page > total_pages and total_pages > 0:
        return RedirectResponse(f"/orders?page={total_pages}")

    orders = await prisma.order.find_many(where={"userId": user_id}, include={"product": True}, skip=offset, take=per_page)
    
    # TODO: Add pagination to this endpoint

    return {"total_orders": orders_count, "orders": orders}