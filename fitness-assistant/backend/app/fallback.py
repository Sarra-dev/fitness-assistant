"""Rule-based answers used when no Gemini API key is configured (or the API is down).

This keeps the whole app usable offline and makes it easy to demo / test.
"""
import re

from .knowledge import KnowledgeBase


def _has(text: str, words: tuple[str, ...]) -> bool:
    """True if any of the words appears as a whole word (so "plank" does not match "plan")."""
    return re.search(r"\b(?:" + "|".join(map(re.escape, words)) + r")(?:s|es)?\b", text) is not None

DISCLAIMER = "Note: this is general fitness information, not medical advice."


def _detect_goal(q: str) -> str:
    if _has(q, ("lose", "loss", "fat", "slim", "weight", "cut", "cutting")):
        return "fat_loss"
    if _has(q, ("muscle", "bulk", "bulking", "gain", "strong", "mass", "build")):
        return "muscle"
    if _has(q, ("endurance", "stamina", "cardio", "run", "running", "marathon")):
        return "endurance"
    return "general"


def _detect_level(q: str) -> str:
    if _has(q, ("advanced", "expert", "experienced")):
        return "Advanced"
    if _has(q, ("intermediate",)):
        return "Intermediate"
    return "Beginner"


def _lines(exercises: list[dict], reps: str) -> list[str]:
    return [f"- {e['title']}: {reps}" for e in exercises]


def build_reply(question: str, context: list[dict], kb: KnowledgeBase) -> str:
    q = question.lower()

    if re.match(r"\s*(hello|hi|hey|good (morning|evening))\b", q):
        return (
            "Hi! I'm your fitness assistant. Tell me your goal (lose fat, build muscle, "
            "improve endurance), your level and how many days a week you can train, "
            "and I'll build a workout and diet plan for you."
        )

    if _has(q, ("plan", "program", "routine", "schedule", "workout", "diet")):
        goal, level = _detect_goal(q), _detect_level(q)
        strength = kb.exercises_for("Strength", level, 4)
        cardio = kb.exercises_for("Cardio", level, 3)
        core = kb.exercises_for("Core", level, 2)
        mobility = kb.exercises_for("Mobility", None, 2)

        if goal == "fat_loss":
            workout = (
                ["Monday (strength): 3 sets of 12 reps"] + _lines(strength, "3 x 12")
                + ["Tuesday (cardio): 30 minutes"] + _lines(cardio[:2], "5 rounds of 1 minute hard, 1 minute easy")
                + ["Thursday (strength + core): 3 sets of 12 reps"] + _lines(core, "3 x 30-40 seconds")
                + ["Saturday (cardio): 40 minutes brisk walk or easy run"]
            )
            diet = [
                "Breakfast: eggs or Greek yogurt with fruit and oats",
                "Lunch: grilled chicken or fish, large salad, a small portion of rice or bulgur",
                "Snack: fruit with a handful of almonds",
                "Dinner: vegetable soup or lentils with a light protein",
                "Tip: aim for a moderate deficit of about 300-500 kcal per day and drink 2-3 liters of water.",
            ]
        elif goal == "muscle":
            upper = kb.exercises_by_muscles({"chest", "back", "shoulders", "triceps", "biceps", "lats"}, level, 3)
            lower = kb.exercises_by_muscles(
                {"legs", "glutes", "quads", "hamstrings"}, level, 3, exclude={e["title"] for e in upper}
            )
            workout = (
                ["Monday (upper body): 4 sets of 8-10 reps"] + _lines(upper, "4 x 8-10")
                + ["Wednesday (lower body): 4 sets of 10 reps"] + _lines(lower, "4 x 10")
                + ["Friday (full body + core): 3 sets"] + _lines(upper[:1] + lower[:1] + core[:1], "3 x 10-12")
                + ["Weekend: 20 minutes light cardio and stretching"]
            )
            diet = [
                "Breakfast: omelette with whole-grain bread and a banana",
                "Lunch: chicken or tuna with rice and vegetables",
                "Snack: yogurt or cottage cheese with nuts",
                "Dinner: lean meat or fish with potatoes and salad",
                "Tip: eat about 1.6-2.2 g of protein per kg of body weight and a small calorie surplus.",
            ]
        elif goal == "endurance":
            workout = (
                ["Monday: 30 minutes steady cardio"] + _lines(cardio[:1], "easy pace")
                + ["Wednesday: interval session, 8 rounds of 1 minute fast, 90 seconds easy"]
                + ["Friday: full-body strength, 3 sets of 12"] + _lines(strength[:3], "3 x 12")
                + ["Sunday: long easy session, 45-60 minutes"]
            )
            diet = [
                "Breakfast: oats with fruit and a spoon of peanut butter",
                "Lunch: pasta or rice with lean protein and vegetables",
                "Snack: banana or dates before training",
                "Dinner: fish or chicken with whole grains and salad",
                "Tip: eat carbohydrates before long sessions and add protein afterwards to recover.",
            ]
        else:
            workout = (
                ["Monday (full body): 3 sets of 10-12 reps"] + _lines(strength[:3], "3 x 10-12")
                + ["Wednesday (cardio + core): 25 minutes"] + _lines(cardio[:1] + core[:1], "3 rounds")
                + ["Friday (full body): 3 sets"] + _lines(strength[1:4], "3 x 10-12")
                + ["Daily: 5-10 minutes of mobility"] + _lines(mobility, "hold 30 seconds")
            )
            diet = [
                "Breakfast: eggs or yogurt, fruit and whole-grain bread",
                "Lunch: half vegetables, a quarter lean protein, a quarter whole grains",
                "Snack: fruit with nuts or hummus with vegetables",
                "Dinner: light protein with vegetables and a little healthy fat",
                "Tip: drink water regularly and sleep 7-9 hours.",
            ]

        return (
            f"Here is a plan for {level.lower()} level. Warm up for 5-10 minutes before each session.\n"
            "WORKOUT PLAN:\n" + "\n".join(workout) + "\n"
            "DIET PLAN:\n" + "\n".join(diet) + "\n"
            + DISCLAIMER
        )

    if context:
        best = context[0]
        extra = f" Related: {', '.join(d['title'] for d in context[1:3])}." if len(context) > 1 else ""
        return f"{best['text']}{extra}\n{DISCLAIMER}"

    return (
        "I can help with workouts, exercises, nutrition and recovery. "
        "Try asking for a workout plan for your goal, how to do an exercise, or what to eat before training."
    )
