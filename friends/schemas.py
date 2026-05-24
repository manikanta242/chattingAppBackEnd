from pydantic import BaseModel

class FriendSchema(BaseModel):
    from_user: int
    to_user: int
    status: str

class FriendRequestSchema(BaseModel):
    from_user: int
    to_user: int
    
class FriendReqPendingSchema(BaseModel):
    to_user:int
    
class friendsListSchema(BaseModel):
    from_user: int
