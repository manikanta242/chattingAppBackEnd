from friends.models import FriendRequest
from auth.models import Users
from core.database import sessionLocal
from sqlalchemy import and_, or_, join
from sqlalchemy.orm import aliased
from fastapi import HTTPException
from message.websockets import active_connections
import asyncio


async def connectService(data: FriendRequest):
    db = sessionLocal()
    try:
        from_user_id = data.from_user
        to_user_id   = data.to_user

        # Fetch sender name for the notification
        sender = db.query(Users).filter(Users.id == from_user_id).first()
        sender_name = sender.name if sender else "Someone"

        req = FriendRequest(from_user=from_user_id, to_user=to_user_id)
        db.add(req)
        db.commit()

        # Push real-time WS notification to receiver if online
        if to_user_id in active_connections:
            await active_connections[to_user_id].send_json({
                "type":           "friend_request",
                "from_user_id":   from_user_id,
                "from_user_name": sender_name,
            })

        return {"response": "request sent successfully"}
    finally:
        db.close()
    
def pendingReqService(data: FriendRequest):
    db = sessionLocal()
    FromUser = aliased(Users)
    ToUser = aliased(Users)
    current_user = data.to_user

    rows = (db.query(
            FriendRequest,
            FromUser.id.label("from_user_id"),
            FromUser.name.label("from_user_name"),
            FromUser.email.label("from_user_email"),
            FromUser.status.label("from_user_status"),
            FromUser.image.label("from_user_image"),
            
            ToUser.id.label("to_user_id"),
            ToUser.name.label("to_user_name"),
            ToUser.email.label("to_user_email"),
            ToUser.status.label("to_user_status"),
            ToUser.image.label("to_user_image"),
        )
        .join(FromUser, FriendRequest.from_user == FromUser.id)
        .join(ToUser, FriendRequest.to_user == ToUser.id)
        .filter(
            FriendRequest.to_user == current_user,
            FriendRequest.status == "pending"
        )
        .all()
    )
    
    # ✅ Build serializable response
    friends = []
    for row in rows:
        req = row.FriendRequest
        if req.from_user == current_user:
            friend = {
                "request_id": req.id,
                "friend_request": req.status,
                "friend_id": row.to_user_id,
                "name": row.to_user_name,
                "email": row.to_user_email,
                "status":row.to_user_status, 
                "image":row.to_user_image,
                
            }
        else:
            friend = {
                "request_id": req.id,
                "friend_request": req.status,
                "friend_id": row.from_user_id,
                "name": row.from_user_name,
                "email": row.from_user_email,
                "status":row.from_user_status, 
                "image":row.from_user_image,
            }
        friends.append(friend)

    return {"response": friends}

    
def friendReqStatusChangeService(data: FriendRequest):
    db = sessionLocal()
    data  = db.query(FriendRequest).filter(
     FriendRequest.from_user == data.from_user,
     FriendRequest.to_user == data.to_user,
     FriendRequest.status == "pending"
    ).first()
    
    if not data :
        return {'response' : "request not found"}
    data.status = "accepted"
    db.commit()
    db.refresh(data)
    return {"response": "Friend request accepted"}

def friendsListService(data: FriendRequest):
    db = sessionLocal()
    
    FromUser = aliased(Users)
    ToUser = aliased(Users)

    # ✅ Save from_user before overwriting data
    current_user = data.from_user

    rows = (db.query(
            FriendRequest,
            FromUser.id.label("from_user_id"),
            FromUser.name.label("from_user_name"),
            FromUser.email.label("from_user_email"),
            FromUser.status.label("from_user_status"),
            FromUser.image.label("from_user_image"),
            
            ToUser.id.label("to_user_id"),
            ToUser.name.label("to_user_name"),
            ToUser.email.label("to_user_email"),
            ToUser.status.label("to_user_status"),
            ToUser.image.label("to_user_image"),
        )
        .join(FromUser, FriendRequest.from_user == FromUser.id)
        .join(ToUser, FriendRequest.to_user == ToUser.id)
        .filter(
            or_(
                and_(
                    FriendRequest.from_user == current_user,
                    FriendRequest.status == "accepted"
                ),
                and_(
                    FriendRequest.to_user == current_user,
                    FriendRequest.status == "accepted"
                )
            )
        )
        .all()
    )

    # ✅ Build serializable response
    friends = []
    for row in rows:
        req = row.FriendRequest
        if req.from_user == current_user:
         friend = {
                "request_id": req.id,
                "friend_request": req.status,
                "friend_id": row.to_user_id,
                "name": row.to_user_name,
                "email": row.to_user_email,
                "status":row.to_user_status, 
                "image":row.to_user_image,
                
            }
        else:
            friend = {
                "request_id": req.id,
                "friend_request": req.status,
                "friend_id": row.from_user_id,
                "name": row.from_user_name,
                "email": row.from_user_email,
                "status":row.from_user_status, 
                "image":row.from_user_image,
            }
        friends.append(friend)

    return {"response": friends}

def registeredUsersService(current_user_id: int):
    db = sessionLocal()
    try:
        # ✅ Get all user IDs who already have a friend request (sent or received)
        existing_requests = (
            db.query(FriendRequest)
            .filter(
                or_(
                    FriendRequest.from_user == current_user_id,
                    FriendRequest.to_user == current_user_id
                ),
                FriendRequest.status != "rejected"  # ✅ don't exclude rejected
            )
            .all()
        )

        # ✅ Collect all user IDs to exclude
        excluded_ids = set()
        for req in existing_requests:
            excluded_ids.add(req.from_user)
            excluded_ids.add(req.to_user)

        # ✅ Also exclude current user
        excluded_ids.add(current_user_id)

        print("Excluded IDs:", excluded_ids)  # debug

        # ✅ Get users not in excluded list
        users = (
            db.query(Users)
            .filter(Users.id.notin_(excluded_ids))
            .all()
        )

        return {
            "response": [
                {
                    "id"      : user.id,
                    "name"    : user.name,
                    "email"   : user.email,
                    "status"  : user.status,
                    "location": user.location,
                    "image"   : user.image
                }
                for user in users
            ]
        }

    except Exception as e:
        print("Error:", e)
        raise HTTPException(status_code=500, detail="Internal server error")

    finally:
        db.close()

def declineRequestService(data: FriendRequest):
    db = sessionLocal()
    try:
        req = db.query(FriendRequest).filter(
            FriendRequest.from_user == data.from_user,
            FriendRequest.to_user   == data.to_user,
            FriendRequest.status    == "pending"
        ).first()

        if not req:
            raise HTTPException(status_code=404, detail="Request not found")

        req.status = "rejected"
        db.commit()
        return {"response": "Friend request declined"}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        db.close()