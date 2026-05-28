from fastapi import APIRouter, Depends
from message.schemas import MessageListSchema, MessageSchema
from friends.schemas import FriendSchema
from message.services import sendMessageService, getmessageService
from utils.commonAuth import get_current_user
router = APIRouter(
     tags=['messages'],
     dependencies=[Depends(get_current_user)]  # ✅ protects all message routes

)

@router.post("/send_message")
def sendMessage(req: MessageSchema):
    return sendMessageService(req)

@router.post("/get-messages")
def getMessage(req: MessageListSchema):
     return getmessageService(req)

