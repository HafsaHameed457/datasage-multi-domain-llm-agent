# Deployment

## Architecture

```
User → Streamlit Community Cloud (frontend)
                │
                ▼ https://datasage-api.onrender.com
         Render.com (FastAPI Docker)
                │
          ┌─────┴─────┐
          ▼           ▼
      Neon.tech    MongoDB Atlas
   (PostgreSQL)    (M0 cluster)
```

## Services

| Service | Purpose | Cost | Sign-up |
|---------|---------|------|---------|
| [Neon.tech](https://neon.tech) | PostgreSQL | Free (500MB) | Email, no credit card |
| [MongoDB Atlas](https://mongodb.com/atlas) | MongoDB | Free (512MB M0) | Already have |
| [Render](https://render.com) | Backend Docker | Free (spins down idle) | GitHub OAuth |
| [Streamlit Cloud](https://streamlit.io/cloud) | Frontend | Free (public repos) | GitHub OAuth |
| [GitHub](https://github.com) | Code + CI/CD | Free | Already have |

## Setup

### 1. Neon.tech — PostgreSQL

Create a free account at [neon.tech](https://neon.tech), spin up a project, and copy the connection string (`postgresql://user:pass@ep-xxxx.us-east-2.aws.neon.tech/datasage`). You'll load data into it later.

### 2. MongoDB Atlas

You already have this. Create an M0 free cluster, whitelist all IPs (`0.0.0.0/0`) for the database user, and copy the connection string (`mongodb+srv://user:pass@cluster.xxxxx.mongodb.net/`).

### 3. GitHub — Repository

Push the code to a public GitHub repository:

```bash
git remote add origin https://github.com/YOUR_USER/datasage.git
git push -u origin main
```

### 4. Render — Backend

1. Log in at [render.com](https://render.com) via GitHub.
2. From dashboard, click **New +** → **Web Service**.
3. Connect your GitHub repo (`datasage`).
4. Set the following:

   | Field | Value |
   |-------|-------|
   | **Name** | `datasage-api` |
   | **Runtime** | `Docker` |
   | **Branch** | `main` |
   | **Health Check Path** | `/health` |

5. Click **Create Web Service**. Render builds the Docker image and deploys.
6. Go to **Environment** tab and add:

   - `PG_URI` → your Neon connection string
   - `MONGO_URI` → your Atlas connection string
   - `GROQ_API_KEY` → your Groq key

7. Click **Save Changes** → **Manual Deploy** → **Deploy latest commit**.

### 5. Streamlit Cloud — Frontend

1. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
2. Click **Deploy an app** → select your repo → branch `main` → file `frontend.py`.
3. In **Advanced settings**, add `API_URL` as `https://datasage-api.onrender.com/query`.

### 6. CI/CD — GitHub Actions

Pushing to `main` triggers:
- **lint**: `ruff check .` (code style)
- **test**: `pytest` (unit tests)
- Render auto-deploys the Docker backend
- Streamlit Cloud auto-deploys the frontend

### 7. Data Migration

Load the datasets into the production databases (one-time):

```bash
# Point to production by editing .env:
PG_URI=postgresql://user:pass@ep-xxxx.us-east-2.aws.neon.tech/datasage
MONGO_URI=mongodb+srv://user:pass@cluster.xxxxx.mongodb.net/

# Run ETL scripts locally (from project root):
source venv/bin/activate
python scripts/load_movies.py
python scripts/load_music.py
python scripts/load_books.py
```

## Environment Variables

| Variable | Where to set | Source |
|----------|-------------|--------|
| `PG_URI` | Render dashboard → Environment | Neon.tech connection string |
| `MONGO_URI` | Render dashboard → Environment | MongoDB Atlas connection string |
| `GROQ_API_KEY` | Render dashboard → Environment | Groq Console |
| `API_URL` | Streamlit Cloud → Advanced settings | `https://datasage-api.onrender.com/query` |

## Verification

```bash
# Health check
curl https://datasage-api.onrender.com/health

# Query
curl -X POST https://datasage-api.onrender.com/query \
  -H "Content-Type: application/json" \
  -d '{"question":"What is the highest rated movie?"}'
```

## Known Limitations

- **Render free tier**: Spins down after 15 minutes of inactivity. First request after idle takes ~30s (cold start).
- **Groq free tier**: 100K tokens/day, 30 requests/min, 12K TPM. Enough for casual use.
- **MongoDB Atlas M0**: 512MB storage, no backup.
