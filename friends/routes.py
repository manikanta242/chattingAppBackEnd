from fastapi import APIRouter, Depends
from friends.schemas import FriendRequestSchema, FriendReqPendingSchema, friendsListSchema
from friends.services import connectService, friendReqStatusChangeService, pendingReqService, friendsListService, registeredUsersService, declineRequestService
from utils.commonAuth import get_current_user
from auth.models             import Users

router = APIRouter(
        tags=['friends'],
        dependencies  = [Depends(get_current_user)]  # ✅ protects ALL routes in this router
)

@router.post("/connect")
async def connect(req: FriendRequestSchema):
    return await connectService(req)

@router.post("/pending-request")
def pendingRequest(req: FriendReqPendingSchema):
        return pendingReqService(req)

@router.post("/request")
def request(req:FriendRequestSchema):
        return friendReqStatusChangeService(req)

@router.post("/friend-list")
def friendsList(req:friendsListSchema):
        return friendsListService(req)

@router.get('/registered-users')
def registeredUsers(current_user: Users = Depends(get_current_user)):
    return registeredUsersService(current_user.id)

@router.post("/decline")
def declineRequest(req: FriendRequestSchema):
    return declineRequestService(req)
