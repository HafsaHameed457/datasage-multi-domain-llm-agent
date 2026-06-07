from fastapi import FastAPI
from pydantic import BaseModel

from app.agent import run_agent

app = FastAPI(title="DataSage")


class QueryRequest(BaseModel):
    question: str
    history: list[list[str]] | None = None
    summary: str = ""


class QueryResponse(BaseModel):
    answer: str
    history: list[list[str]]
    summary: str


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    history = request.history or []
    answer, summary = await run_agent(request.question, history, request.summary)
    updated_history = [*history, ["user", request.question], ["assistant", answer]]
    return QueryResponse(answer=answer, history=updated_history, summary=summary)
