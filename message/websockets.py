from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import Dict
from core.database import sessionLocal
from message.models import Message
from auth.models import Users
from utils.token import decode_token
router = APIRouter()
active_connections: Dict[int, WebSocket] = {}

# ✅ Save message to DB
def save_message(sender_id: int, receiver_id: int, context: str) -> Message:
    db = sessionLocal()
    try:
        msg = Message(
            sender_id   = sender_id,
            receiver_id = receiver_id,
            context     = context
        )
        db.add(msg)
        db.commit()
        db.refresh(msg)
        return msg
    finally:
        db.close()

def get_user_from_token(token: str) -> Users | None:
    db = sessionLocal()
    try:
        # ── Step 1: Decode token ──────────────────────────────
        payload = decode_token(token)
        if not payload:
            return None

        # ── Step 2: Extract fields ────────────────────────────
        email   : str = payload.get("sub")
        user_id : int = payload.get("user_id")
        print(f"📧 Email: {email}, ID: {user_id}")

        if not email:
            return None

        # ── Step 3: Get user from DB ──────────────────────────
        user = db.query(Users).filter(Users.email == email).first()
        if not user:
            print(f"❌ User not found: {email}")
            return None

        return user   # ✅ full Users object

    except Exception as e:
        print(f"❌ Error: {e}")
        return None

    finally:
        db.close()
 
# ============================================================
#  SEND PRESENCE TO ALL CONNECTED USERS
# ============================================================
async def broadcast_presence(user_id: int, name: str, status: str):
    message = {
        "type"   : "presence",
        "user_id": user_id,
        "name"   : name,
        "status" : status       # "online" or "offline"
    }
    print(f"📢 Broadcasting: {message}")

    # ✅ Send to ALL users except self
    for uid, ws in list(active_connections.items()):
        if uid != user_id:
            try:
                await ws.send_json(message)
                print(f"📤 Sent presence to user {uid}")
            except Exception as e:
                print(f"❌ Failed to send to {uid}: {e}")       

# ============================================================
#  UPDATE STATUS IN MYSQL
# ============================================================
def update_status(user_id: int, status: str):
    db = sessionLocal()
    try:
        user = db.query(Users).filter(Users.id == user_id).first()
        if user:
            user.status = status
            db.commit()
            print(f"💾 DB updated: user {user_id} → {status}")
    except Exception as e:
        db.rollback()
        print(f"❌ DB Error: {e}")
    finally:
        db.close()


# ============================================================
#  WEBSOCKET ENDPOINT
# ============================================================
@router.websocket("/chat")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...)
):
    # ── Step 1: Verify token ──────────────────────────────────
    current_user = get_user_from_token(token)

    if not current_user:
        await websocket.close(code=4001)
        print("⛔ Invalid token")
        return

    user_id     = current_user.id
    sender_name = current_user.name
    print(f"✅ {sender_name} (id={user_id}) connecting...")

    # ── Step 2: Accept & Register ─────────────────────────────
    await websocket.accept()
    active_connections[user_id] = websocket
    print(f"✅ {sender_name} connected")

    # ── Step 3: Update DB → online ────────────────────────────
    update_status(user_id, "online")

    # ── Step 4: Broadcast online to all ──────────────────────
    await broadcast_presence(user_id, sender_name, "online")

    # ── Step 5: Send current online users to NEW user ─────────
    # So new user knows who is already online
    for uid in active_connections:
        if uid != user_id:
            try:
                await websocket.send_json({
                    "type"   : "presence",
                    "user_id": uid,
                    "status" : "online"
                })
            except Exception:
                pass

    # ── Step 6: Listen for events ─────────────────────────────
    try:
        while True:
            data        = await websocket.receive_json()
            event_type  = data.get("type")
            receiver_id = data.get("receiver_id")
            context     = data.get("context")

            # ── Handle message ────────────────────────────────
            if event_type == "message":
                if not receiver_id:
                    await websocket.send_json({
                        "type"   : "error",
                        "message": "receiver_id is required"
                    })
                    continue

                if not context:
                    await websocket.send_json({
                        "type"   : "error",
                        "message": "context cannot be empty"
                    })
                    continue

                # ✅ Save to DB
                msg = save_message(user_id, receiver_id, context)

                response_payload = {
                    "type"       : "message",
                    "id"         : msg.id,
                    "sender_id"  : user_id,
                    "sender_name": sender_name,
                    "receiver_id": receiver_id,
                    "context"    : context,
                    "created_at" : str(msg.created_at)
                }

                # ✅ Deliver to receiver if online
                if receiver_id in active_connections:
                    await active_connections[receiver_id].send_json(response_payload)

                # ✅ Echo back to sender
                await websocket.send_json(response_payload)

            else:
                await websocket.send_json({
                    "type"   : "error",
                    "message": f"Unknown type: {event_type}"
                })

    # ── Step 7: Disconnect ────────────────────────────────────
    except WebSocketDisconnect:
        # ✅ Remove from active
        if user_id in active_connections:
            del active_connections[user_id]

        # ✅ Update DB → offline
        update_status(user_id, "offline")

        # ✅ Broadcast offline to all
        await broadcast_presence(user_id, sender_name, "offline")

        print(f"👋 {sender_name} disconnected")