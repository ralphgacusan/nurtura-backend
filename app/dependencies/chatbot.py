# dependencies/chatbot.py

# ---------------------------
# Standard Library Imports
# ---------------------------
from typing import Annotated

# ---------------------------
# FastAPI Imports
# ---------------------------
from fastapi import Depends

# ---------------------------
# SQLAlchemy Imports
# ---------------------------
from sqlalchemy.ext.asyncio import AsyncSession


from app.core.database import get_session
from app.repositories.chatbot_history import ChatbotHistorysRepository
from app.services.chatbot import ChatbotService
from app.dependencies.task import get_task_service
from app.services.task import TaskService


# ---------------------------
# Repository Dependencies
# ---------------------------
async def get_chatbot_repo(
    session: Annotated[AsyncSession, Depends(get_session)]
) -> ChatbotHistorysRepository:
    """Provide a TaskRepository instance using the current DB session."""
    return ChatbotHistorysRepository(session)


# ---------------------------
# Service Dependency
# ---------------------------
async def get_chatbot_service(
    chatbot_repo: Annotated[ChatbotHistorysRepository, Depends(get_chatbot_repo)],
    task_service: Annotated[TaskService, Depends(get_task_service)],
) -> ChatbotService:
    """
    Provide a TaskService instance with all required repositories injected.
    """
    return ChatbotService(
        chatbot_repo=chatbot_repo,
        task_service=task_service
    )
