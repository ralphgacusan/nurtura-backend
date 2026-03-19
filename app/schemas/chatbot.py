# schemas/chatbot_history.py

"""
Pydantic schemas for ChatbotHistory operations.

This schema is specifically for creating a new chatbot interaction.
"""

from pydantic import BaseModel, Field
from enum import Enum
from app.models.user import UserRole


# ---------------------------
# BASE CREATE SCHEMAs
# ---------------------------
class ChatbotHistoryCreate(BaseModel):
    """
    Schema for creating a new chatbot interaction.

    Attributes:
        user_id (int): ID of the user sending the message
        user_role (UserRole): Role of the user
        query_text (str): Text message sent by user
        ai_response_text (str): Response from the AI
    """
    user_id: int 
    user_role: UserRole
    query_text: str
    ai_response_text: str


# ---------------------------
# Request schema
# ---------------------------
class ChatMessageRequest(BaseModel):
    message: str

