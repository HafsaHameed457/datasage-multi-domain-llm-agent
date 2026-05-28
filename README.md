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

### Prerequisites
- Python 3.11+, Docker, Git
- [Google AI Studio API key](https://aistudio.google.com/) (free)

### 1. Start Databases

```bash
# PostgreSQL
docker run --name pg-datasage \
  -e POSTGRES_USER=admin \
  -e POSTGRES_PASSWORD=secret \
  -e POSTGRES_DB=datasage \
  -p 5432:5432 \
  -d postgres:16

# Create schemas
docker exec pg-datasage psql -U admin -d datasage -c "CREATE SCHEMA IF NOT EXISTS movies;"
docker exec pg-datasage psql -U admin -d datasage -c "CREATE SCHEMA IF NOT EXISTS music;"
docker exec pg-datasage psql -U admin -d datasage -c "CREATE SCHEMA IF NOT EXISTS books;"

# MongoDB
docker run --name mongo-datasage \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=secret \
  -p 27017:27017 \
  -d mongo:7
```

### 2. Load Data

```bash
# Ensure datasets are in data/raw/ then run:
source venv/bin/activate
python scripts/load_movies.py
python scripts/load_music.py
python scripts/load_books.py
```

### 3. Start the API

```bash
uvicorn app.main:app --reload
```

### 4. (Optional) Streamlit Frontend

```bash
streamlit run frontend.py
```

---

## Data Status

| Domain | PostgreSQL | MongoDB |
|--------|-----------|---------|
| 🎬 Movies | 4,803 movies | 50,000 reviews |
| 🎵 Music | 114,000 tracks | 1,000 lyrics |
| 📚 Books | 11,119 books | 19,996 reviews |
