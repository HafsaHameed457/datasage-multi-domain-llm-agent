# DataSage - Multi-Domain LLM Agent

## 📌 Project Overview

**DataSage** is a full‑stack AI agent that answers questions about three distinct domains — Movies, Music, and Books. For each domain, it has access to:

- A **PostgreSQL** schema containing structured data (e.g., ratings, genres, popularity).
- A **MongoDB** collection containing unstructured text (e.g., reviews, lyrics, descriptions).

When a user asks a natural language question, the agent decides which domain(s) and which tools to query, then combines the results into a coherent answer.

---

## 🏗 Architecture (High‑Level)

```
User Query (plain English)
        │
        ▼
    FastAPI (/query)
        │
        ▼
    LangChain Agent (Groq)
        │
   ┌────┼──────────────────────┐
   ▼    ▼                      ▼
 Tools (6 total – 2 per domain)
   │
   ├── sql_movies  ────────► PostgreSQL (schema: movies)
   ├── mongo_movies ───────► MongoDB (movies_db.reviews)
   ├── sql_music   ────────► PostgreSQL (schema: music)
   ├── mongo_music  ───────► MongoDB (music_db.lyrics)
   ├── sql_books   ────────► PostgreSQL (schema: books)
   └── mongo_books  ───────► MongoDB (books_db.reviews)
```

---

## 🛠 Tech Stack

| Component | Technology |
| --- | --- |
| **Backend Framework** | FastAPI (Python 3.11+) |
| **LLM Framework** | LangChain + `langchain-groq` |
| **LLM Model** | Groq (`llama-3.3-70b-versatile`) |
| **SQL Database** | PostgreSQL (local Docker container) |
| **NoSQL Database** | MongoDB (local Docker container) |
| **SQL ORM/Driver** | SQLAlchemy + psycopg2‑binary |
| **MongoDB Driver** | PyMongo |
| **Data Processing** | Pandas |
| **Frontend (optional)** | Streamlit |
| **API Key** | Groq Console (free, no credit card) |

---

## 📊 Data Sources

| Domain | Purpose | Dataset Name | CSV Files |
| --- | --- | --- | --- |
| **Movies** | Structured | Movies Dataset TMDB | `tmdb_5000_movies.csv` |
| **Movies** | Unstructured | IMDB Dataset of 50K Movie Reviews | `IMDB Dataset.csv` |
| **Music** | Structured | Spotify Tracks Attributes and Popularity | `spotify_tracks.csv` |
| **Music** | Unstructured | Mood‑Based English Songs Dataset | `songs.csv` |
| **Books** | Structured | Goodreads Books Dataset | `books.csv` |
| **Books** | Unstructured | Amazon Books Dataset (20K Books + 727K Reviews) | `amazon_books_reviews_sample_20k.csv` |

---

## 📦 Implementation Plan

### Phase 0: Prerequisites
- Python 3.11+ with pip
- Docker installed and running
- Git installed
- Kaggle account
- Google AI Studio API key

### Phase 1: Environment Setup
- Get Groq API key
- Create project & Git repository
- Set up virtual environment & dependencies
- Create `.env` file

### Phase 2: Start Databases with Docker
- PostgreSQL container (`pg-datasage`) with schemas: movies, music, books
- MongoDB container (`mongo-datasage`)

### Phase 3: Download & Prepare Data
- Download all 6 datasets from Kaggle
- Create ETL scripts (`scripts/db_connections.py`, `scripts/load_movies.py`, `scripts/load_music.py`, `scripts/load_books.py`)
- Run ETL scripts to populate PostgreSQL and MongoDB

### Phase 4: Build FastAPI Backend
- Configuration (`app/config.py`)
- SQL Tool Factory (`app/tools/sql_tools.py`)
- MongoDB Tool Factory (`app/tools/mongo_tools.py`)
- Agent Setup (`app/agent.py`)
- FastAPI Application (`app/main.py`)

### Phase 5: Test the System
- Start FastAPI server
- Test via Swagger UI at `http://localhost:8000/docs`
- Sample queries for movies, music, books

### Phase 6: Optional Streamlit Frontend
- Create `frontend.py`
- Run with `streamlit run frontend.py`

### Phase 7: Final Commit & Push

---

## 🐳 Docker Setup

```bash
# PostgreSQL
docker run --name pg-datasage \
  -e POSTGRES_USER=admin \
  -e POSTGRES_PASSWORD=secret \
  -e POSTGRES_DB=datasage \
  -p 5432:5432 \
  -d postgres:16

docker exec -it pg-datasage psql -U admin -d datasage -c "CREATE SCHEMA IF NOT EXISTS movies;"
docker exec -it pg-datasage psql -U admin -d datasage -c "CREATE SCHEMA IF NOT EXISTS music;"
docker exec -it pg-datasage psql -U admin -d datasage -c "CREATE SCHEMA IF NOT EXISTS books;"

# MongoDB
docker run --name mongo-datasage \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=secret \
  -p 27017:27017 \
  -d mongo:7
```

---

## � Environment Variables (`.env`)

```
PG_USER=admin
PG_PASSWORD=secret
PG_HOST=localhost
PG_PORT=5432
PG_DB=datasage

MONGO_URI=mongodb://admin:secret@localhost:27017/

GROQ_API_KEY=gsk_...
```

---

## ✅ Completed Steps

- [x] Phase 0: Prerequisites installed
- [x] Phase 1: Environment setup (venv, dependencies, .env)
- [x] Phase 2: Docker containers running (pg-datasage, mongo-datasage)
- [x] Phase 3: Datasets downloaded & ETL scripts executed
- [x] Phase 4: FastAPI backend
- [x] Phase 5: Testing
- [x] Phase 6: Streamlit frontend (optional)
- [x] Phase 7: Final commit & push
