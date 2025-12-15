from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

class Message(BaseModel):
    role: str
    content: str
    timestamp: Optional[str] = None

class ChatRequest(BaseModel):
    messages: List[Message]
    context: Optional[dict] = None

class ChatResponse(BaseModel):
    message: Message
    suggested_actions: List[str] = []

from services.llm import LLMService
from agents.legal import LegalAgent
from agents.conversational import ConversationalAgent

# Dependency Injection (Simple for MVP)
llm_service = LLMService()
legal_agent = LegalAgent(llm_service)
conversational_agent = ConversationalAgent(llm_service, legal_agent)

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        # Get response from the Conversational Agent
        # Convert Pydantic models to dicts for the agent
        messages_dicts = [{"role": m.role, "content": m.content} for m in request.messages]
        
        response_dict = await conversational_agent.chat(messages_dicts, request.context)
        
        return ChatResponse(
            message=Message(
                role=response_dict["role"],
                content=response_dict["content"]
            ),
            suggested_actions=[]
        )
            
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        # Graceful fallback safe mode
        return ChatResponse(
            message=Message(
                role="assistant",
                content="Desculpe, estou tendo dificuldades para processar sua mensagem agora. Pode tentar novamente em alguns instantes?"
            ),
            suggested_actions=[]
        )
