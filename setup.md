# Setup

## Prerequisites

- Python 3.11+, Docker, Git
- [Groq API key](https://console.groq.com/keys) (free, no credit card)

## 1. Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 2. Configure

Create `.env` in the project root:

```ini
PG_URI=postgresql://admin:secret@localhost:5432/datasage
MONGO_URI=mongodb://admin:secret@localhost:27017/
GROQ_API_KEY=gsk_your_key_here
```

## 3. Start Databases

If containers already exist:

```bash
docker start pg-datasage mongo-datasage
```

If first time, create them:

```bash
docker run --name pg-datasage -e POSTGRES_USER=admin -e POSTGRES_PASSWORD=secret -e POSTGRES_DB=datasage -p 5432:5432 -d postgres:16

docker exec pg-datasage psql -U admin -d datasage -c "CREATE SCHEMA IF NOT EXISTS movies;"
docker exec pg-datasage psql -U admin -d datasage -c "CREATE SCHEMA IF NOT EXISTS music;"
docker exec pg-datasage psql -U admin -d datasage -c "CREATE SCHEMA IF NOT EXISTS books;"

docker run --name mongo-datasage -e MONGO_INITDB_ROOT_USERNAME=admin -e MONGO_INITDB_ROOT_PASSWORD=secret -p 27017:27017 -d mongo:7
```

## 4. Load Data (first time only)

```bash
source venv/bin/activate
python scripts/load_movies.py
python scripts/load_music.py
python scripts/load_books.py
```

## 5. Run (two terminals)

**Terminal 1 — Backend:**
```bash
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 — Frontend:**
```bash
source venv/bin/activate
streamlit run frontend.py
```

- Backend API: `http://localhost:8000/docs` (Swagger UI)
- Frontend: `http://localhost:8501` (Streamlit opens it automatically)

## 6. Test

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question":"What is the highest rated movie?"}'
```
