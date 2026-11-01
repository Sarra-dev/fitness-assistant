# Fitness Assistant

An AI-powered fitness chatbot that generates **personalized workout plans** and gives **nutrition advice** tailored to each user's goals (weight loss, muscle gain, endurance).

Built with **FastAPI**, **LangChain** and a **RAG** pipeline (ChromaDB + Hugging Face embeddings), with support for **Groq** (cloud) and **Ollama** (local) LLMs.

**Live demo:** <frontend-url> | **API:** <backend-url>

---

## Features

- **Fitness chatbot**: ask about exercises, diets and health tips, with streamed responses
- **4-week workout plan generation** (async, with status polling)
- **User profiles**: height, weight, age, goal, dietary restrictions, workout history
- **Exercise recommendations** based on the user's goal
- **RAG**: answers grounded in indexed documents and scraped exercise data
- **Latency optimizations**: response caching (TTL), persisted vector store, streaming, smaller/faster models

---

## Tech Stack

| Layer | Technologies |
|---|---|
| Backend | Python, FastAPI, Pydantic |
| LLM orchestration | LangChain |
| LLMs | Groq (`llama-3.1-8b-instant`), Ollama (`llama3:8b`) |
| Embeddings | `sentence-transformers/multi-qa-MiniLM-L6-cos-v1` |
| Vector store | ChromaDB |
| Data | PDF loading (PyPDF), web scraping (fitness exercises) |
| Caching | `cachetools` (TTLCache) |
| Frontend | React |

---

## Architecture

```
User --> React frontend --> FastAPI --> Cache (TTL)
                                |
                                |--> Retriever (ChromaDB) --> relevant chunks
                                |
                                |--> LLM (Groq / Ollama) --> streamed answer
```

1. PDFs and scraped exercises are cleaned, split into chunks and embedded.
2. Embeddings are stored in a persistent ChromaDB (`MyVectorDB1.0/`).
3. At query time, the top-k chunks are retrieved and injected into the prompt.
4. The LLM generates the answer, which is streamed to the client and cached.

---

## Getting Started

### Prerequisites

- Python 3.10+
- A [Groq API key](https://console.groq.com/)
- (Optional) [Ollama](https://ollama.com/) for local models: `ollama pull llama3:8b`

### Installation

```bash
git clone <your-repo-url>
cd <your-repo-name>

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Environment variables

Create a `.env` file (or export the variable):

```env
GROQ_API_KEY=your_groq_api_key
```

### Run the API

```bash
uvicorn app.main:app --reload
```

Interactive docs: http://localhost:8000/docs

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/fitness-exercises` | List scraped fitness exercises |
| `POST` | `/chatFitness` | Chat with the assistant (streamed, cached) |
| `POST` | `/generate/workout-plan` | Start async generation of a 4-week plan |
| `GET` | `/workout-plan/{request_id}` | Get the status/result of a plan |
| `POST` | `/user/profile` | Create or update a user profile |
| `GET` | `/user/profile/{user_id}` | Get a user profile |
| `GET` | `/recommend/exercises/{user_id}` | Exercise recommendations for a user |
| `POST` | `/update-knowledge-base` | Rebuild the vector store in the background |

### Example

```bash
curl -X POST http://localhost:8000/chatFitness \
  -H "Content-Type: application/json" \
  -d '{"question": "I want to lose weight, what workout do you recommend?"}'
```

---

## Project Structure

```
.
├── app/
│   ├── main.py
│   ├── routes.py          # API routes, RAG chain, LLM setup
│   ├── scraper.py         # Fitness exercises scraper
│   └── documents/         # PDFs to index
├── MyVectorDB1.0/         # Persisted ChromaDB (generated)
├── requirements.txt
└── README.md
```

---

## Disclaimer

This project provides general fitness and nutrition information and is **not a substitute for professional medical advice**. Consult a qualified professional before starting a new training or diet program.

---

## Roadmap

- [ ] Dockerize the application
- [ ] Replace in-memory user profiles with a real database
- [ ] Add authentication (OAuth2)
- [ ] Return real sources/citations from the RAG pipeline
- [ ] Nutrition plan generation

---

## Author

**Sarra Ben Bettaieb**: Data Science & AI Engineering student at Tek-Up University
[LinkedIn](<your-linkedin>) | [GitHub](<your-github>)
