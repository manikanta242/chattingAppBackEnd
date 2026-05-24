from fastapi import APIRouter
from message.schemas import MessageListSchema, MessageSchema
from friends.schemas import FriendSchema
from message.services import sendMessageService, getmessageService
router = APIRouter(
     tags=['messages']
)

@router.post("/send_message")
def sendMessage(req: MessageSchema):
    return sendMessageService(req)

@router.post("/get-messages")
def getMessage(req: MessageListSchema):
     return getmessageService(req)

