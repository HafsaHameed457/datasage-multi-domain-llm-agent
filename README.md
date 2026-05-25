# 🧠 DataSage — Multi-Domain LLM Agent

> Query movies, music, and books using natural language. DataSage bridges structured (PostgreSQL) and unstructured (MongoDB) data with a Gemini-powered LangChain agent.

---

## Architecture

```
User Query (plain English)
        │
        ▼
    FastAPI (/query)
        │
        ▼
    LangChain Agent (Gemini)
        │
   ┌────┼──────────────────────────┐
   ▼    ▼                          ▼
 Tools (6 total — 2 per domain)
   │
   ├── sql_movies   ────────► PostgreSQL (schema: movies)
   ├── mongo_movies ────────► MongoDB  (movies_db.reviews)
   ├── sql_music    ────────► PostgreSQL (schema: music)
   ├── mongo_music  ────────► MongoDB  (music_db.lyrics)
   ├── sql_books    ────────► PostgreSQL (schema: books)
   └── mongo_books  ────────► MongoDB  (books_db.reviews)
```

---

## Problem

Users want cross-domain answers like *"Find an energetic track with good danceability and show its lyrics"* or *"What's a highly rated sci-fi movie with positive reviews?"* Traditional setups make you stitch together structured DB queries and unstructured text searches manually — DataSage does it in one shot.

---

## Tech Stack

| Layer             | Technology                          |
|-------------------|-------------------------------------|
| 🧠 LLM            | Google Gemini 1.5 Flash             |
| ⚙️ Framework      | LangChain + FastAPI                 |
| 🗃️ Structured DB  | PostgreSQL (3 schemas)              |
| 📄 Unstructured DB| MongoDB (3 collections)             |
| 🖥️ Frontend       | Streamlit (optional)                |
| 🐳 Infra          | Docker, Python, Uvicorn             |

---

## How It Works

| Step | Description |
|------|-------------|
| **1. Data** | Movie, music, and book datasets are loaded into PostgreSQL (ratings, genres, popularity) and MongoDB (reviews, lyrics). |
| **2. Agent** | LangChain builds an OpenAI-style tools agent backed by Gemini with **6 tools** — one SQL + one Mongo tool per domain. |
| **3. Query** | User asks a question → FastAPI receives it → Agent picks relevant tools → Gathers structured + unstructured data → Gemini synthesizes the answer. |
| **4. Example** | *"Highest rated sci-fi movie? Show a review."* → `sql_movies` finds the movie → `mongo_movies` fetches a review → combined response. |

### Domain → Tool Mapping

| Domain | SQL (PostgreSQL)       | NoSQL (MongoDB)          |
|--------|------------------------|--------------------------|
| 🎬 Movies | `sql_movies`         | `mongo_movies` (reviews) |
| 🎵 Music  | `sql_music`          | `mongo_music` (lyrics)   |
| 📚 Books  | `sql_books`          | `mongo_books` (reviews)  |

---

## Setup

```bash
# 1. Start databases (Docker)
docker compose up -d

# 2. Load data
python etl/load_all.py

# 3. Start the API
uvicorn app.main:app --reload
```

See the project plan for detailed instructions.
