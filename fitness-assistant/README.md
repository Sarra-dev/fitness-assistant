# Fitness Assistant

A full-stack AI fitness chatbot. Ask about workouts, exercises, nutrition or recovery and get
personalized answers, including formatted **WORKOUT PLAN** and **DIET PLAN** sections.

- **Frontend:** React 19 (Create React App), plain CSS
- **Backend:** FastAPI (Python), Google Gemini for answers
- **Retrieval (RAG):** a small TF-IDF search over an exercise + nutrition knowledge base; the best matches are given to the LLM as context and shown under each answer as *Sources*
- **Offline mode:** without an API key the backend still answers with rule-based replies, so the app always works

```
fitness-assistant/
├── backend/
│   ├── app/
│   │   ├── main.py        # FastAPI app + endpoints
│   │   ├── config.py      # settings read from backend/.env
│   │   ├── schemas.py     # request / response models
│   │   ├── knowledge.py   # TF-IDF retrieval over the knowledge base
│   │   ├── llm.py         # Gemini API client
│   │   ├── fallback.py    # offline rule-based answers
│   │   └── data/          # exercises.json, nutrition.json
│   ├── tests/test_api.py  # pytest tests
│   ├── requirements.txt
│   ├── .env               # your local settings (not committed)
│   └── .env.example
├── src/                   # React app (ChatBox, Message, FitnessExercises, services/api.js)
├── public/
├── .env                   # frontend settings (REACT_APP_API_URL)
└── .env.example
```

## 1. Run the backend

Requires Python 3.10+.

```bash
cd backend
python -m venv .venv

# Windows (PowerShell):   .venv\Scripts\Activate.ps1
# Windows (cmd):          .venv\Scripts\activate.bat
# macOS / Linux:          source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Open http://localhost:8000/docs for the interactive API docs and http://localhost:8000/health to
check the mode (`gemini` or `fallback`).

### Add your Gemini key (optional but recommended)

1. Create a free key at https://aistudio.google.com/apikey
2. Open `backend/.env` and set `GEMINI_API_KEY=your_key_here`
3. Restart the backend.

If the key is empty, invalid, or Gemini is unreachable, the API automatically falls back to offline answers.

## 2. Run the frontend

Requires Node.js 18+. In a second terminal, from the project root:

```bash
npm install
npm start
```

It opens http://localhost:3000. The backend URL is set in the root `.env`
(`REACT_APP_API_URL=http://localhost:8000`). Restart `npm start` after changing it.

## API

| Method | Endpoint | Description |
|---|---|---|
| POST | `/chatFitness` | Body: `{ "question": "...", "history": [{"role": "user"\|"assistant", "text": "..."}] }` → `{ "response": "...", "sources": [{"title","category"}] }` |
| GET | `/fitness-exercises` | List of exercises. Optional `?category=Strength\|Cardio\|Core\|Mobility` |
| GET | `/health` | Status and which mode is active |

## Configuration (`backend/.env`)

| Variable | Default | Meaning |
|---|---|---|
| `GEMINI_API_KEY` | *(empty)* | Gemini key. Empty = offline mode |
| `GEMINI_MODEL` | `gemini-2.5-flash` | Gemini model name |
| `ALLOWED_ORIGINS` | `http://localhost:3000,http://127.0.0.1:3000` | Frontend origins allowed by CORS |
| `TOP_K` | `4` | Knowledge-base entries given to the LLM |
| `MAX_HISTORY` | `8` | Previous messages sent for context |
| `REQUEST_TIMEOUT` | `30` | Seconds to wait for Gemini |

## Tests

```bash
cd backend
pytest
```

## Deployment

- **Backend (Render / Railway):** root directory `backend`, build command `pip install -r requirements.txt`,
  start command `uvicorn app.main:app --host 0.0.0.0 --port $PORT`. Add `GEMINI_API_KEY` and
  `ALLOWED_ORIGINS=https://your-frontend.vercel.app` as environment variables.
- **Frontend (Vercel):** set the environment variable `REACT_APP_API_URL=https://your-backend.onrender.com`,
  then deploy (build command `npm run build`, output directory `build`).

## Notes

- Never commit `.env` files with real keys. They are already in `.gitignore`; the `.env.example` files are safe to commit.
- This app gives general fitness information, not medical advice.
