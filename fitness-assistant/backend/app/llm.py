"""Google Gemini client (plain REST via httpx, so there is no fragile SDK dependency)."""
import httpx

from .config import get_settings
from .schemas import HistoryItem

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

SYSTEM_PROMPT = """You are Fitness Assistant, a friendly and knowledgeable personal trainer and nutrition coach.

Rules:
- Use the "Knowledge base excerpts" provided with each question when they are relevant, and add your own fitness knowledge when needed.
- Be practical and concise. Ask a short follow-up question if you need the user's goal, level, available equipment or schedule.
- When the user asks for a plan, answer in PLAIN TEXT (no markdown, no asterisks, no # headings) using exactly these two section headers, each on its own line:
WORKOUT PLAN:
DIET PLAN:
  Under each header write one item per line, starting with a day or meal name (for example "Monday: ..." or "Breakfast: ...").
- For normal questions, answer in short plain-text paragraphs without those headers.
- Only discuss fitness, exercise, nutrition, sleep and recovery. Politely decline other topics.
- You are not a doctor. For injuries, medical conditions, pregnancy or eating disorders, recommend consulting a professional.
"""


class LLMError(Exception):
    """Raised when the Gemini API call fails."""


def _build_contents(question: str, history: list[HistoryItem], context: list[dict]) -> list[dict]:
    settings = get_settings()
    turns = list(history)[-settings.max_history :]
    while turns and turns[0].role != "user":  # Gemini expects the first turn to be the user's
        turns.pop(0)

    contents = [
        {"role": "user" if t.role == "user" else "model", "parts": [{"text": t.text}]}
        for t in turns
    ]
    excerpts = "\n".join(f"- {d['title']} ({d['category']}): {d['text']}" for d in context)
    excerpts = excerpts or "(no matching entries)"
    contents.append(
        {
            "role": "user",
            "parts": [
                {"text": f"Knowledge base excerpts:\n{excerpts}\n\nUser question: {question}"}
            ],
        }
    )
    return contents


async def generate_reply(question: str, history: list[HistoryItem], context: list[dict]) -> str:
    settings = get_settings()
    payload = {
        "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": _build_contents(question, history, context),
        "generationConfig": {"temperature": 0.6, "maxOutputTokens": 2048},
    }
    url = GEMINI_URL.format(model=settings.gemini_model)
    headers = {"x-goog-api-key": settings.gemini_api_key, "Content-Type": "application/json"}

    try:
        async with httpx.AsyncClient(timeout=settings.request_timeout) as client:
            resp = await client.post(url, json=payload, headers=headers)
    except httpx.HTTPError as exc:
        raise LLMError(f"Network error while calling Gemini: {exc}") from exc

    if resp.status_code != 200:
        raise LLMError(f"Gemini returned HTTP {resp.status_code}: {resp.text[:300]}")

    try:
        parts = resp.json()["candidates"][0]["content"]["parts"]
        text = "".join(p.get("text", "") for p in parts).strip()
    except (KeyError, IndexError, ValueError) as exc:
        raise LLMError("Unexpected response format from Gemini") from exc

    if not text:
        raise LLMError("Gemini returned an empty answer")
    return text
