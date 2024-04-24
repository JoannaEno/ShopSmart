from fastapi.testclient import TestClient
from httpx import AsyncClient
from unittest.mock import AsyncMock
from app.main import app  # assuming your FastAPI app instance is named `app`
from app.models import SignUp  # Assuming SignUp is a Pydantic model for the request body
from apis.prisma import prisma  # assuming prisma is your database client

client = TestClient(app)

# Mock the database interaction
prisma.user.find_first = AsyncMock(return_value=None)
prisma.user.create = AsyncMock(return_value={"email": "test@example.com", "name": "Test User"})

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
