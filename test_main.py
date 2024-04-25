from fastapi.testclient import TestClient
from httpx import AsyncClient
from unittest.mock import AsyncMock
from main import app  
#from models import SignUp  
from apis.prisma import prisma
from unittest.mock import MagicMock
from prisma.errors import ClientNotConnectedError

client = TestClient(app)

prisma_client = MagicMock()
prisma_client.connect.side_effect = ClientNotConnectedError("Client is not connected to the query engine")
prisma.connect()

#Mock the database interaction
# prisma.user.find_first = AsyncMock(return_value=None)
# prisma.user.create = AsyncMock(return_value={"email": "test@example.com", "name": "Test User"})

'''
# Test case for successful sign-up
def test_sign_up_success():
    signup_data = {"email": "test@example.com", "password": "password", "name": "Test User"}
    response = client.post("/auth/sign-up", json=signup_data)
    assert response.status_code == 201
    assert response.json() == {"email": "test@example.com", "name": "Test User"}

# Test case for user already exists
def test_sign_up_user_exists():
    prisma.user.find_first = AsyncMock(return_value={"email": "test@example.com", "name": "Test User"})
    signup_data = {"email": "test@example.com", "password": "password", "name": "Test User"}
    response = client.post("/auth/sign-up", json=signup_data)
    assert response.status_code == 422
    assert response.json() == {"detail": "User already exists"}
'''



def test_create_product():
    # Define test data
    test_product_data = {
        "name": "Test Product",
        "description": "Test description",
        "price": 9.99
    }

    # Send a POST request to create a new product
    response = client.post("apis/product/create", json=test_product_data)

    # Assert that the response status code is 201 CREATED
    assert response.status_code == 201

    # Assert that the response contains the created product data
    created_product = response.json()
    assert "id" in created_product
    assert created_product["name"] == test_product_data["name"]
    assert created_product["description"] == test_product_data["description"]
    assert created_product["price"] == test_product_data["price"]
    
    
def test_read_products():
        # Send a GET request to retrieve products with default pagination
        response = client.get("/products")

        # Assert that the response status code is 200 OK
        assert response.status_code == 200


        response_data = response.json()
        assert "total_products" in response_data
        assert "products" in response_data

        assert isinstance(response_data["total_products"], int)
        assert response_data["total_products"] >= 0

        assert isinstance(response_data["products"], list)

        response_custom_pagination = client.get("/products?page=2&per_page=5")
        response_custom_pagination_data = response_custom_pagination.json()

        # Assert that the response status code is 200 OK
        assert response_custom_pagination.status_code == 200

        # Assert that the response contains the expected keys
        assert "total_products" in response_custom_pagination_data
        assert "products" in response_custom_pagination_data

        assert len(response_custom_pagination_data["products"]) == 5

        assert response_custom_pagination_data["total_products"] >= 5  # Assuming there are at least 5 products in the database
        
        
def test_sign_in():
    # Define test data for sign-in
    test_sign_in_data = {
        "email": "test@example.com",
        "password": "password123"
    }

    
    response = client.post("/auth/sign-in", json=test_sign_in_data)

    # Assert that the response status code is 200 OK
    assert response.status_code == 200

    # Assert that the response contains the expected keys
    response_data = response.json()
    assert "token" in response_data
    assert "user" in response_data

    assert isinstance(response_data["token"], str)
    assert response_data["token"]

    user = response_data["user"]
    assert "id" in user
    assert "email" in user
    assert user["email"] == test_sign_in_data["email"]
    
def test_sign_up():
    # Define test data for sign-up
    test_sign_up_data = {
        "email": "test@example.com",
        "password": "password123",
        "name": "Test User"
    }

    # Send a POST request to sign up with the test data
    response = client.post("/auth/sign-up", json=test_sign_up_data)

    # Assert that the response status code is 201 CREATED
    assert response.status_code == 201

    response_data = response.json()
    assert "id" in response_data
    assert "email" in response_data
    assert "name" in response_data

    assert response_data["email"] == test_sign_up_data["email"]
    assert response_data["name"] == test_sign_up_data["name"]

    assert "createdAt" in response_data