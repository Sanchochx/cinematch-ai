import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Request

from api.schemas import ChatRequest, ChatResponse, HealthResponse
from api.service import ChatService

logger = logging.getLogger("ai_engine.api")
router = APIRouter()


def get_chat_service(request: Request) -> ChatService:
    return request.app.state.chat_service


@router.get("/health")
async def health() -> HealthResponse:
    return HealthResponse()


@router.post("/chat")
async def chat(
    body: ChatRequest, service: Annotated[ChatService, Depends(get_chat_service)]
) -> ChatResponse:
    # Solo longitudes: el mensaje del usuario no se escribe en los logs.
    logger.info("chat request: message_chars=%d history_items=%d", len(body.message), len(body.history))
    return ChatResponse(reply=await service.chat(body))
