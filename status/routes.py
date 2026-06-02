from fastapi import APIRouter, File, Form, UploadFile, Depends
from auth.models import Users
from utils.commonAuth import get_current_user
from .services import createStatusService, getFriendsStatusService, deleteStatusService
from typing import Optional

router = APIRouter(
        tags=['status'],
        dependencies  = [Depends(get_current_user)]  # ✅ protects ALL routes in this router
)

@router.post("")
async def create_status(
    content : Optional[str]      = Form(None),
    image   : Optional[UploadFile] = File(None),
    current_user: Users          = Depends(get_current_user)
):
    return await createStatusService(content, image, current_user)

@router.get("/friends")
async def get_friends_status(current_user: Users = Depends(get_current_user)):
    return await getFriendsStatusService(current_user)

@router.delete("/{status_id}")
async def delete_status(status_id: int, current_user: Users = Depends(get_current_user)):
    return await deleteStatusService(status_id, current_user)