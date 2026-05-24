from message.models import Message
from friends.models import FriendRequest
from core.database import sessionLocal
from sqlalchemy import and_, or_

def sendMessageService(req: Message):
    db = sessionLocal()
    # 🔐 check friendship
    friend = db.query(FriendRequest).filter(
         or_(
            and_(
                FriendRequest.from_user == req.sender_id,
                FriendRequest.to_user == req.receiver_id,
                FriendRequest.status == "accepted"
            ),
            and_(
                FriendRequest.from_user == req.receiver_id,
                FriendRequest.to_user == req.sender_id,
                FriendRequest.status == "accepted"
            )
        )
    ).first()

    if not friend:
        return {"response" : "Not a friend"}

    msg = Message(
        sender_id=req.sender_id,
        receiver_id=req.receiver_id,
        context=req.context
    )

    db.add(msg)
    db.commit()
    db.refresh(msg)

    return msg

def getmessageService(req: Message):
    db = sessionLocal()
    messages = db.query(Message).filter(
        or_(
            and_(
                Message.sender_id == req.sender_id,
                Message.receiver_id == req.receiver_id
            ),
            and_(
                Message.sender_id == req.receiver_id,
                Message.receiver_id == req.sender_id
            )
        )

    ).order_by(Message.created_at.asc()).all()
    
    return {
        "response":messages
    }