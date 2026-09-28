import os

os.environ["GEMINI_API_KEY"] = ""  # force offline mode for tests

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_exercises_list_and_filter():
    all_ex = client.get("/fitness-exercises").json()
    assert len(all_ex) > 10
    assert {"title", "description", "category"} <= set(all_ex[0])
    cardio = client.get("/fitness-exercises", params={"category": "cardio"}).json()
    assert cardio and all(e["category"] == "Cardio" for e in cardio)


def test_chat_plan_has_headers():
    r = client.post("/chatFitness", json={"question": "I want a plan to lose weight"})
    assert r.status_code == 200
    body = r.json()
    assert "WORKOUT PLAN:" in body["response"] and "DIET PLAN:" in body["response"]
    assert isinstance(body["sources"], list)


def test_chat_returns_sources_for_exercise_question():
    r = client.post("/chatFitness", json={"question": "How do I do a plank?"})
    body = r.json()
    assert any(s["title"] == "Plank" for s in body["sources"])


def test_chat_validation():
    assert client.post("/chatFitness", json={"question": ""}).status_code == 422
    assert client.post("/chatFitness", json={}).status_code == 422


def test_plank_question_is_not_treated_as_plan_request():
    body = client.post("/chatFitness", json={"question": "how to do a plank"}).json()
    assert "WORKOUT PLAN:" not in body["response"]
    assert "plank" in body["response"].lower()


def test_muscle_plan_lower_body_day_uses_leg_exercises():
    text = client.post(
        "/chatFitness", json={"question": "muscle gain plan, intermediate"}
    ).json()["response"]
    lower_day = text.split("Wednesday (lower body)")[1].split("Friday")[0]
    assert any(x in lower_day for x in ("Squats", "Lunges", "Glute Bridge", "Deadlift"))
    assert "Push-ups" not in lower_day and "Overhead Press" not in lower_day
