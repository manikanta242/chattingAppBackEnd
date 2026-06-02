from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from core.database import sessionLocal
from auth.models import Users
from .models import Status
from datetime import datetime
from friends.models import FriendRequest

import os, uuid

UPLOAD_FOLDER = "uploads"

async def createStatusService(content, image, current_user: Users):
    db = sessionLocal()
    try:
        image_path = None
        if image:
            ext       = os.path.splitext(image.filename)[1]
            filename  = f"{uuid.uuid4()}{ext}"
            image_path = os.path.join(UPLOAD_FOLDER, filename).replace("\\", "/")
            with open(image_path, "wb") as f:
                f.write(await image.read())

        status = Status(
            user_id  = current_user.id,
            content  = content,
            image    = image_path
        )
        db.add(status)
        db.commit()
        return {"response": "Status posted successfully"}
    finally:
        db.close()

async def getFriendsStatusService(current_user: Users):
    db = sessionLocal()
    try:

        # get accepted friends
        friends = db.query(FriendRequest).filter(
            ((FriendRequest.from_user   == current_user.id) |
             (FriendRequest.to_user == current_user.id)),
            FriendRequest.status == "accepted"
        ).all()

        friend_ids = []
        for f in friends:
            fid = f.to_user if f.from_user == current_user.id else f.from_user
            friend_ids.append(fid)

        # also include current user's own status
        friend_ids.append(current_user.id)

        # get active statuses (not expired)
        now      = datetime.utcnow()
        statuses = db.query(Status, Users).join(
            Users, Users.id == Status.user_id
        ).filter(
            Status.user_id.in_(friend_ids),
            Status.expires_at > now
        ).order_by(Status.created_at.desc()).all()

        # group by user
        grouped = {}
        for status, user in statuses:
            uid = user.id
            if uid not in grouped:
                grouped[uid] = {
                    "user_id"  : user.id,
                    "name"     : user.name,
                    "image"    : user.image,
                    "statuses" : []
                }
            grouped[uid]["statuses"].append({
                "id"         : status.id,
                "content"    : status.content,
                "image"      : status.image,
                "created_at" : status.created_at.strftime("%H:%M"),
                "expires_at" : status.expires_at.isoformat()
            })

        return list(grouped.values())
    finally:
        db.close()

async def deleteStatusService(status_id: int, current_user: Users):
    db = sessionLocal()
    try:
        status = db.query(Status).filter(
            Status.id      == status_id,
            Status.user_id == current_user.id
        ).first()
        if not status:
            raise HTTPException(status_code=404, detail="Status not found")
        db.delete(status)
        db.commit()
        return {"response": "Status deleted"}
    finally:
        db.close()