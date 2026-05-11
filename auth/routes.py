from fastapi import APIRouter
from auth.schemas import userSchema, loginSchema
from auth.services import registerService, userService, loginService
router = APIRouter(
    prefix="/auth",
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