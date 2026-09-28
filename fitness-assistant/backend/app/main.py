"""Fitness Assistant API (FastAPI).

Endpoints used by the React frontend:
  POST /chatFitness        -> chat with the assistant
  GET  /fitness-exercises  -> list of exercises (optional ?category=)
  GET  /health             -> health check
"""
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .fallback import build_reply
from .knowledge import KnowledgeBase
from .llm import LLMError, generate_reply
from .schemas import ChatRequest, ChatResponse, Exercise, Source

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("fitness-api")

settings = get_settings()
kb = KnowledgeBase()

app = FastAPI(title="Fitness Assistant API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "llm": "gemini" if settings.llm_enabled else "fallback (no GEMINI_API_KEY set)",
        "model": settings.gemini_model if settings.llm_enabled else None,
    }


@app.get("/fitness-exercises", response_model=list[Exercise])
def fitness_exercises(category: str | None = None) -> list[dict]:
    return kb.list_exercises(category)


@app.post("/chatFitness", response_model=ChatResponse)
async def chat_fitness(req: ChatRequest) -> ChatResponse:
    question = req.question.strip()
    context = kb.search(question, settings.top_k)

    answer: str | None = None
    if settings.llm_enabled:
        try:
            answer = await generate_reply(question, req.history, context)
        except LLMError as exc:
            logger.warning("LLM unavailable, using fallback answer: %s", exc)

    if answer is None:
        answer = build_reply(question, context, kb)

    return ChatResponse(
        response=answer,
        sources=[Source(title=d["title"], category=d["category"]) for d in context],
    )
