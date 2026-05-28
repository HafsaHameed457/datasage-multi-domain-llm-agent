from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI

from app.config import Config
from app.tools.sql_tools import create_sql_tool
from app.tools.mongo_tools import create_mongo_tool

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=Config.GOOGLE_API_KEY,
    temperature=0,
)

DOMAINS = [
    {"domain": "movies", "schema": "movies", "mongo_db": "movies_db", "mongo_coll": "reviews"},
    {"domain": "music", "schema": "music", "mongo_db": "music_db", "mongo_coll": "lyrics"},
    {"domain": "books", "schema": "books", "mongo_db": "books_db", "mongo_coll": "reviews"},
]

tools = []
for d in DOMAINS:
    sql_tool = create_sql_tool(d["domain"], Config.PG_URI, d["schema"], llm)
    mongo_tool = create_mongo_tool(d["domain"], d["mongo_db"], d["mongo_coll"])
    tools.extend([sql_tool, mongo_tool])

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=(
        "You are DataSage, a multi-domain assistant. "
        "You have access to SQL databases and MongoDB text collections "
        "for movies, music, and books. "
        "Use the appropriate tools to answer the user's question. "
        "Combine structured data and text snippets when helpful."
    ),
)


async def run_agent(question: str) -> str:
    result = await agent.ainvoke({"messages": [("human", question)]})
    return result["messages"][-1].content
