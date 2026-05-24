from pydantic import BaseModel
class MessageSchema(BaseModel):
    sender_id: int
    receiver_id: int
    context: str
    
class MessageListSchema(BaseModel):
    sender_id: int
    receiver_id: int