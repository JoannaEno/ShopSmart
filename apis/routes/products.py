import math
from typing import Optional
from fastapi import APIRouter, Query, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from prisma.models import User as UserModel
from openai import OpenAI

from apis.prisma import prisma

router = APIRouter()

client = OpenAI(api_key="sk-proj-X98alvw8LblcQ26u8UDxT3BlbkFJdfhuvHxn3qdVVcRBccTu")

class Product(BaseModel):
  name: str
  description: Optional[str] = None
  price: float
  
class UpdateProduct(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None


@router.post("/product/create", tags=["product"], status_code=status.HTTP_201_CREATED)
async def create_product(product: Product):
    product = await prisma.product.create(
        {
            "price": product.price,
            "name":  product.name,
            "description": product.description

        }
    )
    return product


@router.get("/product/{productId}", tags=["product"], status_code=status.HTTP_200_OK)
async def read_product(productId: str):
    product = await prisma.product.find_unique(where={"id": productId})

    return product


@router.get("/products", tags=["product"], status_code=status.HTTP_200_OK)
async def read_products(page: int = Query(default=1, ge=1),
                        per_page: int = Query(default=10, le=100)):
    offset = (page - 1) * per_page
    products_count = await prisma.order.count()
    # products_count = await prisma.order.count(distinct=["product"])
    total_pages = math.ceil(products_count / per_page)

    # If the provided page number is greater than the total number of pages, we redirect to the last page
    if page > total_pages and total_pages > 0:
        return RedirectResponse(f"/orders?page={total_pages}")

    products = await prisma.product.find_many(skip=offset, take=per_page)
    return {"total_products": products_count, "products": products}


@router.delete("/product/{productId}", tags=["product"], status_code=status.HTTP_200_OK)
async def delete_product(productId: str):
    product = await prisma.product.delete(where={"id": productId})

    return product


@router.put("/update-product/{productId}", tags=["product"], status_code=status.HTTP_200_OK)
async def update_product(productId: str, product: UpdateProduct):
    existing_product = await prisma.product.find_unique(where={"id": productId})

    if not product:
        return {"message": f"Product with id {productId} not found"}
    updatedProduct = await prisma.product.update(
        where={"id": productId},
           data={"name": product.name or existing_product.name,
              "description": product.description or existing_product.description, "price": product.price or existing_product.price}
    )

    return {"message": f"Product with id {updatedProduct.id} has been updated successfully"}

@router.post("/product/ai-info", tags=["product"], status_code=status.HTTP_201_CREATED)
async def suggest_product(product: str):
    completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful store assistant. Give more information about store products."},
        {"role": "user", "content": f"Tell me more about: {product} and suggest similar products."}
    ]
    )

    print(completion.choices[0].message)
    return {"message": completion.choices[0].message}