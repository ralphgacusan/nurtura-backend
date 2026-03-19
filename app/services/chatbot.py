"""
Service layer for managing chatbot interactions with Gemini API.

Responsibilities:
- Send messages to Gemini
- Include user context: tasks, history
- Build prompts in a structured way
- Separate logic from FastAPI router
"""

from google import genai
from app.core.config import settings
from app.services.task import TaskService 
from app.repositories.chatbot_history import ChatbotHistorysRepository
from app.schemas.chatbot import ChatbotHistoryCreate
from app.models.user import User

# Initialize Gemini client (singleton)
client = genai.Client(api_key=settings.GEMINI_API_KEY)

class ChatbotService:
    """
    Service class for handling chatbot interactions.
    """

    def __init__(self, 
        chatbot_repo: ChatbotHistorysRepository, 
        task_service: TaskService = None 
    ):
        """
        Args:
            task_service (TaskService, optional): Optional reference to TaskService to fetch tasks.
        """
        self.chatbot_repo = chatbot_repo
        self.task_service = task_service

    # ---------------------------
    # Store History
    # ---------------------------
    async def add_history(
            self,
            user: User,
            query_text: str,
            ai_response_text: str,
        ) -> None:
            """
            Store a chatbot interaction in the database.

            Args:
                user_id (int): ID of the user sending the message
                user_role (str): Role of the user ("caregiver" or "dependent")
                query_text (str): Message sent by the user
                ai_response_text (str): AI response
                repo (ChatbotHistoryRepository): Repository instance to save interaction
            """
            history_data = ChatbotHistoryCreate(
                user_id=user.user_id,
                user_role=user.role,
                query_text=query_text,
                ai_response_text=ai_response_text
            )
            await self.chatbot_repo.create(history_data)

    # ---------------------------
    # GET USER HISTORY
    # ---------------------------
    async def get_user_history(
        self,
        user_id: int,
        limit: int = 50
    ) -> list[str]:
        """
        Fetch a user's chatbot history as a list of strings for context.

        Args:
            user_id (int): ID of the user
            limit (int): Max number of interactions to retrieve

        Returns:
            list[str]: List of formatted "User: ... / AI: ..." messages
        """
        history_records = await self.chatbot_repo.list_by_user(user_id, limit=limit)
        return [f"User: {h.query_text}\nAI: {h.ai_response_text}" for h in history_records]
    

    # ---------------------------
    # GET USER HISTORY (FOR UI)
    # ---------------------------
    async def get_user_history_raw(
        self,
        user_id: int,
        limit: int = 20,
        offset: int = 0
    ):
        """
        Fetch raw chatbot history for frontend display.
        Supports pagination.
        """
        records = await self.chatbot_repo.list_by_user_paginated(
            user_id=user_id,
            limit=limit,
            offset=offset
        )

        return [
            {
                "user": r.query_text,
                "ai": r.ai_response_text,
                "created_at": r.created_at
            }
            for r in records
        ]

    # ---------------------------
    # ASK GEMINI
    # ---------------------------
    def ask_gemini(self, prompt: str) -> str:
        """
        Send a prompt to Gemini and return the response.

        Args:
            prompt (str): The full prompt text

        Returns:
            str: Gemini's response text
        """
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt
        )
        return response.text
    
    def format_task_for_prompt(self, task) -> str:
        """
        Format a task for the prompt including all important details.
        """
        parts = [f"Title: {task.title}"]

        if getattr(task, "description", None):
            parts.append(f"Description: {task.description}")
        if getattr(task, "due_date", None):
            parts.append(f"Due Date: {task.due_date.isoformat()}")
        if getattr(task, "priority", None):
            parts.append(f"Priority: {task.priority}")

        # Include completion status if available
        completions = getattr(task, "completions", [])
        if completions:
            status_list = [c.status for c in completions]
            parts.append(f"Completions: {', '.join(status_list)}")

        return " | ".join(parts)
    
    # ---------------------------
    # PROMPT BUILDER
    # ---------------------------
    def build_prompt(
        self,
        user_message: str,
        assigned_tasks: list[str] = None,
        created_tasks: list[str] = None,
        history: list[str] = None
    ) -> str:
        """
        Build a structured prompt including full context of tasks.
        """
        prompt = (
            "You are a conversational assistant for task awareness.\n"
            "Your role is ONLY to help users understand, review, and discuss their tasks.\n"
            "You have NO ability to create, update, delete, assign, or complete tasks.\n"
            "You cannot perform any actions on tasks or the system.\n"
            "You only provide explanations, summaries, and suggestions based on the provided data.\n"
            "Always clearly distinguish between tasks assigned to the user and tasks created by the user.\n\n"
        )

        if history:
            prompt += "Conversation history:\n" + "\n".join(history) + "\n\n"

        if assigned_tasks:
            prompt += "Tasks currently assigned to the user:\n"
            prompt += "\n".join(f"- {t}" for t in assigned_tasks) + "\n\n"

        if created_tasks:
            prompt += "Tasks created by the user:\n"
            prompt += "\n".join(f"- {t}" for t in created_tasks) + "\n\n"

        prompt += f"User message:\n{user_message}\n\nReply naturally based on the tasks and history."
        return prompt

    # ---------------------------
    # SEND MESSAGE WITH FULL CONTEXT
    # ---------------------------
    async def send_message(
        self,
        user_message: str,
        user: User,
        history_limit: int = 50
    ) -> str:
        """
        Send a message to Gemini with full context of tasks and history.
        """
        # ---------------------------
        # 1️⃣ Fetch assigned tasks
        # ---------------------------
        tasks_assigned = []
        if self.task_service:
            assigned_tasks = await self.task_service.list_tasks_for_current_user(user)
            tasks_assigned = [self.format_task_for_prompt(t) for t in assigned_tasks]

        # ---------------------------
        # 2️⃣ Fetch tasks created by the user
        # ---------------------------
        tasks_created = []
        if self.task_service:
            created_tasks = await self.task_service.list_tasks_created_by_current_user(user)
            tasks_created = [self.format_task_for_prompt(t) for t in created_tasks]

        # ---------------------------
        # 3️⃣ Fetch conversation history
        # ---------------------------
        history_records = await self.get_user_history(user.user_id, limit=history_limit)

        # ---------------------------
        # 4️⃣ Build prompt
        # ---------------------------
        prompt = self.build_prompt(
            user_message=user_message,
            assigned_tasks=tasks_assigned,
            created_tasks=tasks_created,
            history=history_records
        )

        # ---------------------------
        # 5️⃣ Ask Gemini
        # ---------------------------
        reply = self.ask_gemini(prompt)

        # ---------------------------
        # 6️⃣ Store interaction in history
        # ---------------------------
        await self.add_history(user, user_message, reply)

        return reply