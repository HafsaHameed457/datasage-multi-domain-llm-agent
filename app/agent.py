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
        "You are DataSage, a multi-domain assistant for movies, music, and books.\n"
        "SQL tools query structured tables:\n"
        "- movies: movies(domain_id,title,release_date,budget,revenue,vote_average,popularity), genres(id,name), movie_genres(domain_id,genre_id)\n"
        "- music: tracks(domain_id,name,artists,popularity,danceability,energy,valence,tempo,track_genre)\n"
        "- books: books(domain_id,title,authors,average_rating,ratings_count)\n"
        "MongoDB tools search text content (reviews, lyrics, descriptions).\n"
        "Use the right tool for the question."
    ),
)


async def run_agent(question: str) -> str:
    result = await agent.ainvoke({"messages": [("human", question)]})
    return result["messages"][-1].content
