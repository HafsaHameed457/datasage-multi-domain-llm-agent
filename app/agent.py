import asyncio

from groq import APIStatusError, BadRequestError
from langchain.agents import create_agent
from langchain_groq import ChatGroq

from app.config import Config
from app.tools.sql_tools import create_sql_tool
from app.tools.mongo_tools import create_mongo_tool

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
)

DOMAINS = [
    {"domain": "movies", "schema": "movies", "mongo_db": "movies_db", "mongo_coll": "reviews"},
    {"domain": "music", "schema": "music", "mongo_db": "music_db", "mongo_coll": "lyrics"},
    {"domain": "books", "schema": "books", "mongo_db": "books_db", "mongo_coll": "reviews"},
]

tools = []
for d in DOMAINS:
    tools.append(create_sql_tool(d["domain"], Config.PG_URI, d["schema"], llm))
    tools.append(create_mongo_tool(d["domain"], d["mongo_db"], d["mongo_coll"]))

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=(
        "You are DataSage, a multi-domain assistant for movies, music, and books. "
        "Answer questions naturally without mentioning databases, tools, queries, or internal details."
    ),
)

ROLE_MAP = {"user": "human", "assistant": "ai", "human": "human", "ai": "ai"}
SUMMARY_TRIGGER = 20
KEEP = 10


async def _summarize(conversation: list[list[str]], existing: str = "") -> str:
    lines = [f"{role}: {text}" for role, text in conversation]
    text = "\n".join(lines)

    prompt = (
        "Summarize the key facts from this conversation in one short sentence. "
        "Focus on movies, music, books, ratings, genres, and recommendations discussed.\n\n"
    )
    if existing:
        prompt += f"Previous summary: {existing}\n\n"
    prompt += f"New conversation:\n{text}\n\nSummary:"
    try:
        response = await llm.ainvoke([("human", prompt)])
        return response.content.strip()
    except Exception:
        return existing


async def run_agent(
    question: str, history: list[list[str]] | None = None, summary: str = ""
) -> tuple[str, str]:
    for attempt in range(3):
        try:
            msgs = []
            if history:
                total = len(history)
                if total > SUMMARY_TRIGGER:
                    old = history[:-(KEEP)]
                    recent = history[-(KEEP):]
                    summary = await _summarize(old, summary)
                    msgs.append(("system", f"Conversation summary: {summary}"))
                    for role, text in recent:
                        msgs.append((ROLE_MAP.get(role, "human"), text))
                else:
                    for role, text in history:
                        msgs.append((ROLE_MAP.get(role, "human"), text))
            msgs.append(("human", question))
            result = await agent.ainvoke({"messages": msgs})
            return result["messages"][-1].content, summary
        except (BadRequestError, APIStatusError):
            if attempt < 2:
                await asyncio.sleep(2 ** attempt)
                continue
            raise
