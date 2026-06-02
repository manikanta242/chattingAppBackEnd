from fastapi import APIRouter
from auth.routes import router as auth_router
from message.routes import router as message_router
from friends.routes import router as friends_router
from message.websockets import router as websocket_router
from status.routes import router as status_router

api_router = APIRouter()

# register module routers
api_router.include_router(auth_router, prefix="/auth")
api_router.include_router(message_router, prefix="/message")
api_router.include_router(friends_router, prefix="/friends")
api_router.include_router(status_router, prefix="/status")
api_router.include_router(websocket_router, prefix="/ws")
