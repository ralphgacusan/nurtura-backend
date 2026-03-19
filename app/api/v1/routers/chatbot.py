# routers/chatbot.py
from fastapi import APIRouter, Depends, Query
from app.dependencies.chatbot import get_chatbot_service
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.chatbot import ChatMessageRequest


router = APIRouter()


# ---------------------------
# Send message endpoint
# ---------------------------
@router.post(
    "/chat",
    summary="Send a message to the chatbot",
    description="""
Send a message to the chatbot and receive an AI-generated response.

The chatbot automatically includes:
- Tasks assigned to the user
- Tasks created by the user
- Recent conversation history

This endpoint powers the main chat interaction experience.
"""
)
async def chat_with_context(
    request: ChatMessageRequest,
    current_user: User = Depends(get_current_user),
    chatbot_service = Depends(get_chatbot_service)
):
    """
    Send a message to the chatbot including full context:
    - Tasks assigned to the user
    - Tasks created by the user (optional)
    - Recent conversation history
    """
    try:
        reply = await chatbot_service.send_message(
            user_message=request.message,
            user=current_user
        )
        return {"reply": reply}

    except Exception as e:
        return {"error": str(e)}
    
# ---------------------------
# Get chat history (paginated)
# ---------------------------
@router.get(
    "/chat/history",
    summary="Get chat history",
    description="""
Retrieve the chatbot conversation history for the currently authenticated user.

This endpoint supports pagination for efficient loading:
- **limit**: Number of messages to return (default: 20, max: 100)
- **offset**: Number of messages to skip (used for pagination)

Results are returned in **descending order (newest first)**.

Frontend should reverse the list to display messages chronologically.
"""
)
async def get_chat_history(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    chatbot_service = Depends(get_chatbot_service)
):
    """
    Get chat history for the current user (paginated).

    - limit: number of messages to fetch
    - offset: for pagination (skip)
    """
    try:
        history = await chatbot_service.get_user_history_raw(
            user_id=current_user.user_id,
            limit=limit,
            offset=offset
        )

        return {
            "history": history,
            "limit": limit,
            "offset": offset
        }

    except Exception as e:
        return {"error": str(e)}