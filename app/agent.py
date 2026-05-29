from langchain.agents import create_agent
from langchain_groq import ChatGroq

from app.config import Config
from app.tools.sql_tools import create_sql_tools
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
    sql_tools = create_sql_tools(d["domain"], Config.PG_URI, d["schema"], llm)
    mongo_tool = create_mongo_tool(d["domain"], d["mongo_db"], d["mongo_coll"])
    tools.extend([*sql_tools, mongo_tool])

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=(
        "You are DataSage, a multi-domain assistant for movies, music, and books. "
        "Use SQL tools for structured data and MongoDB tools for text content. "
        "Choose the right tools based on the question."
    ),
)


async def run_agent(question: str) -> str:
    result = await agent.ainvoke({"messages": [("human", question)]})
    return result["messages"][-1].content
