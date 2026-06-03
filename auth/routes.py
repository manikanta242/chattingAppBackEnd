from fastapi import APIRouter, File, Form, UploadFile, Request, Depends, Body
from auth.schemas import userSchema, loginSchema, logoutSchema
from auth.services import registerService, userService, loginService, logoutService, getProfileService, updateProfileService,verifyEmailService, forgotPasswordService, resetPasswordService,resendEmailService
from utils.commonAuth import get_current_user

router = APIRouter(
    tags=['authentication']
)

@router.post("/register")
async def register(
    request     : Request,
    name        : str        = Form(...),
    email       : str        = Form(...),
    phonenumber : str        = Form(...),
    password    : str        = Form(...),
    location    : str        = Form(...),
    image       : UploadFile = File(None)
):
    form = await request.form()
    print("Form data received:", dict(form))  # 👈 shows what Angular is sending

    return await registerService(
        userSchema(
            name=name,
            email=email,
            phonenumber=phonenumber,
            password=password,
            location=location
        ),
        image  # ✅ pass image separately
    )
    
@router.get("/verify-email")
async def verify_email(token: str):
    return await verifyEmailService(token)

@router.post("/resend-verification")
async def resend_email(body: dict = Body(...)):
    return await resendEmailService(body)

@router.post("/forgot-password")
async def forgot_password(email: str = Form(...)):
    return await forgotPasswordService(email)

@router.post("/reset-password")
async def reset_password(
    token        : str = Form(...),
    new_password : str = Form(...),
    confirm_password: str = Form(...)
):
    return await resetPasswordService(token, new_password)

@router.get("/profile")
async def get_profile(user: userSchema = Depends(get_current_user)):
    return await getProfileService(user)

@router.put("/profile")
async def update_profile(
    name        : str        = Form(...),
    phonenumber : str        = Form(...),
    location    : str        = Form(...),
    image       : UploadFile = File(None),
    tokenData       : str        = Depends(get_current_user)
):
    return await updateProfileService(name, phonenumber, location, image, tokenData)

@router.get('/user')
def user():
    return userService()

@router.post('/login')
def login(data:loginSchema):
    return loginService(data)

@router.post("/logout")
def logout(data:logoutSchema):
    return logoutService(data)