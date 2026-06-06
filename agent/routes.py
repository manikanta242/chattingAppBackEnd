from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from groq import Groq
from utils.commonAuth import get_current_user
from core.config import GROQ_API_KEY

router = APIRouter(tags=["agent"])

client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = (
    "You are a helpful AI assistant inside a chat application. "
    "Answer clearly and concisely."
)


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]


@router.post("/chat")
def agent_chat(req: ChatRequest, current_user=Depends(get_current_user)):
    def stream():
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}]
            + [m.model_dump() for m in req.messages],
            stream=True,
        )
        for chunk in response:
            text = chunk.choices[0].delta.content
            if text:
                yield text

    return StreamingResponse(stream(), media_type="text/plain")


# ── Autocorrect ───────────────────────────────────────────────

class AutocorrectRequest(BaseModel):
    text: str


@router.post("/autocorrect")
def autocorrect(req: AutocorrectRequest, current_user=Depends(get_current_user)):
    """Fix spelling and grammar. Returns corrected text and whether it changed."""
    if not req.text.strip():
        return JSONResponse({"corrected": "", "changed": False})

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a spell-checker and grammar corrector for a chat app. "
                    "Fix ONLY spelling mistakes and obvious grammar errors. "
                    "Keep the same tone, style, and meaning — do NOT add words or change intent. "
                    "Return ONLY the corrected sentence, nothing else. "
                    "If the text is already correct, return it exactly as is."
                ),
            },
            {"role": "user", "content": req.text},
        ],
        max_tokens=150,
        temperature=0.1,
    )

    corrected = response.choices[0].message.content.strip()
    changed = corrected.lower() != req.text.strip().lower()
    return JSONResponse({"corrected": corrected, "changed": changed})
