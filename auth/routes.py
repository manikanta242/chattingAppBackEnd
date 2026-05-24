from fastapi import APIRouter
from auth.schemas import userSchema, loginSchema, logoutSchema
from auth.services import registerService, userService, loginService, logoutService
router = APIRouter(
    tags=['authentication']
)

@router.post("/register")
def register(data: userSchema):
    return registerService(data)

@router.get('/user')
def user():
    return userService()

@router.post('/login')
def login(data:loginSchema):
    return loginService(data)

@router.post("/logout")
def logout(data:logoutSchema):
    return logoutService(data)