from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from uuid import UUID
from app.api.auth import create_access_token

router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    role: str

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    # Mock login logic - in a real app, verify against database
    if request.username == "admin" and request.password == "admin":
        user_id = UUID("f4ee9fed-c123-4d19-b169-08de554562a6")
        role = "credit_officer"
        token = create_access_token(user_id, role)
        return {
            "access_token": token,
            "token_type": "bearer",
            "role": role
        }
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password"
    )
