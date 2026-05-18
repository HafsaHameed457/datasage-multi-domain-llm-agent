# DataSage - Multi-Domain LLM Agent

## Problem Statement

Users often need to query across multiple domains (movies, music, books) to get combined insights — e.g., *"What's a highly rated sci-fi movie with positive reviews?"* or *"Find an energetic track with good danceability and show its lyrics."* Traditional databases store structured data (ratings, genres, popularity) separately from unstructured text (reviews, lyrics), making it difficult to query both simultaneously without custom application logic.

## Solution

DataSage is a multi-domain AI agent powered by Google Gemini that understands natural language questions and autonomously decides which databases to query. It bridges structured (PostgreSQL) and unstructured (MongoDB) data across three domains — movies, music, and books — returning combined, context-rich answers.

## Tech Stack

| Layer          | Technology                        |
|----------------|-----------------------------------|
| LLM            | Google Gemini 1.5 Flash (free API)|
| Framework      | LangChain + FastAPI               |
| Structured DB  | PostgreSQL (3 schemas)            |
| Unstructured DB| MongoDB (3 collections)           |
| Frontend       | Streamlit (optional)              |
| Infra          | Docker, Python, Uvicorn           |

## How It Works

1. **Data** — Movie, music, and book datasets are loaded into PostgreSQL (structured fields like rating, genre, popularity) and MongoDB (unstructured text like reviews and lyrics).
2. **Agent** — LangChain creates an OpenAI-style tools agent backed by Gemini. It has 6 tools: 3 SQL query tools (one per domain) and 3 MongoDB search tools.
3. **Query Flow** — User asks a question in natural language → FastAPI receives it → Agent decides which tools to call → Gathers structured data from PostgreSQL and text snippets from MongoDB → Gemini synthesizes the answer.
4. **Example**: *"What is the highest rated sci-fi movie? Show me a review snippet."* triggers `sql_movies` (find the movie) then `mongo_movies` (fetch a review) and returns a combined response.

## Setup

See the project plan for full setup instructions — Docker for databases, ETL scripts for data loading, and `uvicorn` to serve the API.
